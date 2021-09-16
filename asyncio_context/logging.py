import logging
from .context import context_register


class Context2Record(logging.Filter):

    def __init__(self, *a, ctx_name, **kw):
        self.ctx_name = ctx_name
        super().__init__(*a, **kw)

    def filter(self, record):
        ctx_cls = context_register.get(self.ctx_name)
        for name, value in ctx_cls.dict().items():
            setattr(record, name, value)
        return True
