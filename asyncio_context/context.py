import asyncio
from typing import Dict


TASK_CONTEXT_ATTR = 'asyncio_context'
context_register: Dict[str, 'Context'] = {}


def _get_raw_ctx() -> dict:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return {}
    task = asyncio.current_task(loop=loop)
    return getattr(task, TASK_CONTEXT_ATTR, {})


class _Attrs2Context(type):

    @staticmethod
    def make_setter(name):
        def setter(self, value):
            task = asyncio.current_task()
            ctx_name = f'{self._prefix}{name}'
            if not hasattr(task, TASK_CONTEXT_ATTR):
                new_ctx = {
                    f'{self._prefix}{k}': v for k, v in self._origin.items()}
                setattr(task, TASK_CONTEXT_ATTR, new_ctx)
            getattr(task, TASK_CONTEXT_ATTR)[ctx_name] = value

        return setter

    @staticmethod
    def make_getter(name):
        def getter(self):
            ctx = _get_raw_ctx()
            ctx_name = f'{self._prefix}{name}'
            if ctx_name not in ctx:
                return self._origin[name]
            return ctx[ctx_name]

        return getter

    def __new__(mcs, name, bases, attrs):
        new_attrs = {'_origin': {}}
        for attr_name, attr_value in attrs.items():
            if attr_name.startswith('_') or attr_name in (
                    'dict', 'copy_to_task'):
                new_attrs[attr_name] = attr_value
                continue
            new_attrs['_origin'][attr_name] = attr_value
            new_attrs[attr_name] = property(
                fget=mcs.make_getter(attr_name),
                fset=mcs.make_setter(attr_name))
        return super().__new__(mcs, name, bases, new_attrs)


class Context(metaclass=_Attrs2Context):
    _origin: dict
    _prefix: str = ''

    def __init_subclass__(cls, **kwargs):
        context_register[cls.__qualname__] = cls

    @classmethod
    def dict(cls) -> dict:
        ctx = _get_raw_ctx()
        res = {}
        for k, v in cls._origin.items():
            ctx_name = f'{cls._prefix}{k}'
            res[k] = ctx.get(ctx_name, cls._origin[k])
        return res

    @classmethod
    def copy_to_task(cls, task: asyncio.Task):
        setattr(task, TASK_CONTEXT_ATTR, cls.dict())
