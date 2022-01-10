import logging
import json
import io
import contextlib
import sys
from flask import Flask
from flask import request
from flask_cors import CORS


import pyjion
import pyjion.dis

app = Flask(__name__)
CORS(app)

@app.route('/compile', methods=['POST'])
def main():
    logging.info('Python HTTP trigger function processed a request.')
    result = {}
    BLOCKED_EVENTS = [
        'import',
        'imaplib.send',
        'ftplib.connect',
        'ftplib.sendcmd',
        'open',
        'os.chmod',
        'os.chown',
        'os.exec',
        'os.fork',
        'os.remove',
        'os.rmdir',
        'os.spawn',
        'os.system',
        'smtplib.connect',
        'socket.connect',
        'subprocess.Popen',
        'webbrowser.open',
        'urllib.Request',
        'flask.debughelpers'
    ]
    def block_imports(event, args):
        if event in BLOCKED_EVENTS:
            raise ValueError(f"Code not allowed ({event} {args}).")
    level = int(request.args.get('level', 1))
    if level not in [0, 1, 2]:
        level = 1
    debug  = bool(int(request.args.get('debug', 0)))
    pyjion.config(graph=True, level=level, debug=debug)
    pyjion.enable()

    try:
        sys.addaudithook(block_imports)
        co = compile(request.data, 'demo.py', 'exec')
        exec(co, {}, {}) # run the code once
        exec(co, {}, {}) # run the code again with profile data
        BLOCKED_EVENTS = []
    except Exception as ex:
        return (
            str(ex),
            500
        )

    pyjion.disable()
    result['graph'] = pyjion.graph(co)
    dis_cil = io.StringIO()
    with contextlib.redirect_stdout(dis_cil):
        pyjion.dis.dis(co, True, True)
    result['dis_cil'] = dis_cil.getvalue()
    result['offsets'] = pyjion.offsets(co)
    dis_x64 = io.StringIO()
    with contextlib.redirect_stdout(dis_x64):
        pyjion.dis.dis_native(co, True, False)
    result['dis_x64'] = dis_x64.getvalue()
    result['cfg'] = pyjion.dis.flow_graph(co)
    result['version'] = pyjion.__version__
    result['config'] = pyjion.config()
    return json.dumps(result)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=False, port=80)