import logging

import azure.functions as func
import pyjion
import pyjion.dis


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    pyjion.enable()
    pyjion.enable_pgc()
    co = compile(req.get_body(), 'demo.py', 'exec')

    pyjion.disable()

    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
    )
