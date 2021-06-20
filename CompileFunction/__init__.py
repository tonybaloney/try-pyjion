import logging
import json
import io
import contextlib

import azure.functions as func
import pyjion
import pyjion.dis


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    result = {}
    pyjion.enable()
    pyjion.enable_pgc()
    co = compile(req.get_body(), 'demo.py', 'exec')
    exec(co)
    result['compile_result1'] = pyjion.info(co)
    exec(co)
    result['compile_result2'] = pyjion.info(co)
    pyjion.disable()

    dis_cil = io.StringIO()
    with contextlib.redirect_stdout(dis_cil):
        pyjion.dis.dis(co, True)
    result['dis_cil'] = dis_cil.getvalue()

    dis_x64 = io.StringIO()
    with contextlib.redirect_stdout(dis_x64):
        pyjion.dis.dis_native(co, True)
    result['dis_x64'] = dis_x64.getvalue()

    return func.HttpResponse(
            json.dumps(result),
            status_code=200
    )
