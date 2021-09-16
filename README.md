# asyncio-context

Tool for store data within asyncio task (for example, in all coroutines across handling aiohttp request) and enrich logging record with this data.  
Small, nice-looking and with annotations. 

Install
==========================
pip install asyncio-context

Example
==========================
It can be used for logging trace id and other info about request:
```python
...
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
...
```
```python
from asyncio_context import Context

class ViewsCtx(Context):
    user_id: str = 'UNKNOWN'
    trace_id: str = 'NO_TRACE'
    
ctx = ViewsCtx()
log = logging.getLogger()

class MyView(web.View):
    async def get(self):
        
        ctx.trace_id = self.request.headers.get('X-Trace-Id', str(uuid.uuid4()))
        # or
        ViewsCtx().user_id = self.request.match_info.get('user_id')
        
        log.info('Test request')
        # GET http://localhost:8080/user/123
        # [trace_id:ea38e89d-fba1-40a3-899e-297c6cd76732] [user_id:123]:Test request
```

Context can be copied to another asyncio task:
```python
task = asyncio.get_running_loop().create_task(another_task())
ViewsCtx.copy_to_task(task)
```