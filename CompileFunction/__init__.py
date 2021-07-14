import logging
import json
import io
import contextlib
import sys

import azure.functions as func
import pyjion
import pyjion.dis


def main(req: func.HttpRequest) -> func.HttpResponse:
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
        'urllib.Request'
    ]
    def block_imports(event, args):
        if event in BLOCKED_EVENTS:
            raise ValueError("Code not allowed.")

    pyjion.enable()
    pyjion.enable_pgc()
    pyjion.enable_graphs()
    pyjion.enable_debug()

    try:
        sys.addaudithook(block_imports)
        co = compile(req.get_body(), 'demo.py', 'exec')
        exec(co, {}, {}) # run the code once
        result['compile_result1'] = pyjion.info(co)
        exec(co, {}, {}) # run the code again with profile data
        result['compile_result2'] = pyjion.info(co)
        BLOCKED_EVENTS = []
    except Exception as ex:
        return func.HttpResponse(
            str(ex),
            status_code=500
        )

    pyjion.disable()
    result['graph'] = pyjion.get_graph(co)
    dis_cil = io.StringIO()
    with contextlib.redirect_stdout(dis_cil):
        pyjion.dis.dis(co, True)
    result['dis_cil'] = dis_cil.getvalue()
    result['offsets'] = pyjion.get_offsets(co)
    dis_x64 = io.StringIO()
    with contextlib.redirect_stdout(dis_x64):
        pyjion.dis.dis_native(co, True)
    result['dis_x64'] = dis_x64.getvalue()
    result['version'] = pyjion.__version__
    return func.HttpResponse(
            json.dumps(result),
            status_code=200
    )
