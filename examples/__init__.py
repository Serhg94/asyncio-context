import logging.config
import uuid
import asyncio
from aiohttp import web

from asyncio_context import Context


class ViewsCtx(Context):
    user_id: str = 'UNKNOWN'
    trace_id: str = 'NO_TRACE'


ctx = ViewsCtx()
log = logging.getLogger()


async def another_task():
    log.info('another task')


class MyView(web.View):

    async def get(self):
        ViewsCtx().user_id = self.request.match_info.get('user_id')
        ctx.trace_id = self.request.headers.get('X-Trace-Id', str(uuid.uuid4()))
        log.info('Test request')

        task = asyncio.get_running_loop().create_task(another_task())
        ViewsCtx.copy_to_task(task)

        # To show same trace id in aiohttp exception log
        raise Exception()

        return web.Response(body='hello world!')


app = web.Application()
app.router.add_route("GET", "/user/{user_id}", MyView)


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[trace_id:%(trace_id)s] [user_id:%(user_id)s]:%(message)s'
        },
    },
    'filters': {
        'context2record': {
            '()': 'asyncio_context.logging.Context2Record',
            'ctx_name': 'ViewsCtx'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'filters': ['context2record'],
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
log.info('Starting...')
web.run_app(app)
