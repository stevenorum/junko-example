#!/usr/bin/env python3A

from junko.config import SUNYATA_CONFIG
from junko.decorators import *

from junko.exceptions import HttpException, render_http_exceptions

from junko.dispatch import DispatchChain, Link, StaticLink
from junko.template_dispatchers import TemplateLink, load_template

from junko.formatting import format_content
from junko import kson as json
from junko import logster
from junko.random_utils import *
from junko.response_core import make_response

import os
import traceback

logster.set_level(logster.DEBUG)

DEBUG_ENABLED = SUNYATA_CONFIG["debug_enabled"]

DEBUG_CHAIN = DispatchChain(debug_name="DEBUG_CHAIN")
STATIC_CHAIN = DispatchChain(debug_name="STATIC_CHAIN")
PAGE_CHAIN = DispatchChain(debug_name="PAGE_CHAIN")

HANDLER_CHAIN = DispatchChain(
    DEBUG_CHAIN,
    STATIC_CHAIN,
    PAGE_CHAIN,
    debug_name="HANDLER_CHAIN"
)

def get_debug_string(request):
    event = to_object(request)
    return json.dumps(event, indent=2, sort_keys=True)+"\n\nDispatch paths:\n"+json.dumps(HANDLER_CHAIN.debug_info(),indent=2,sort_keys=True) + "\n\n\nENVIRON:\n\n" + json.dumps(dict(os.environ), indent=2, sort_keys=True) + "\n\n\nTask root contents:\n\n" + "\n".join(os.listdir(os.environ['LAMBDA_TASK_ROOT']))

def debug(request):
    return make_response(format_content(get_debug_string(request)))

def receive_api_request(request):
    return make_response(format_content(get_debug_string(request)))

STATIC_CHAIN.add_links(
    *[StaticLink(filename, debug_name=filename.split("/")[-1]) for filename in SUNYATA_CONFIG["static_file_list"]]
)

PAGE_CHAIN.add_links(
    TemplateLink(r"^/?(index.html)?$", template_name="index.html", debug_name="Index page"),
    TemplateLink(r"^/?about.html$", template_name="about.html", debug_name="About page"),
    TemplateLink(r"^/?input.html$", template_name="input.html", debug_name="Input page"),
)

if SUNYATA_CONFIG.debug_enabled:
    DEBUG_CHAIN.add_links(
        Link(r"^.*debug$", debug, debug_name="Debug page"),
        Link(r"^/?api.*$", receive_api_request, debug_name="API handler")
    )

@log_calls
@render_http_exceptions
@log_errors
def catchall(event, context):
    try:
        request = to_object(event)
        request["lambda_context"] = context
        response = HANDLER_CHAIN.dispatch(request)
        if response:
            return response
        raise HttpException.from_code(404)
    except Exception as e:
        if SUNYATA_CONFIG.debug_enabled:
            return make_response(body=format_content(traceback.format_exc()))
        else:
            raise e
