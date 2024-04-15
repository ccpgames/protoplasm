__all__ = [
    'require_params',
    'takes_context',
]

import functools
import inspect
import typing
from protoplasm import errors
from protoplasm.casting import castutils

import logging
log = logging.getLogger(__name__)


def _map_args_to_params(param_map, arg_list, kw_map):
    mapped_params = {k: None for k in param_map.keys()}
    if arg_list:
        mapped_params.update(dict(zip(list(param_map.keys())[:len(arg_list)], arg_list)))
    if kw_map:
        mapped_params.update(kw_map)
    return mapped_params


def require_params(arg_name: typing.Union[str, typing.Iterable] = '*', *more_arg_names, typecheck=False):
    arg_is_func = False
    func = None
    if isinstance(arg_name, typing.Callable):
        arg_is_func = True
        func = arg_name
        arg_name = '*'

    def wrap(f):
        param_signature: typing.Dict[str, inspect.Parameter] = dict(inspect.signature(f).parameters)
        required_params = set()

        if arg_name == '*':
            key_list = list(param_signature.keys())
            if key_list and key_list[0] in ('self', 'cls'):
                key_list.pop(0)
            ctx_arg = getattr(f, '__takes_context_as__', None)
            if ctx_arg and key_list[-1] == ctx_arg:
                key_list.pop(-1)
            required_params = set(key_list)
        else:
            arg_list = []
            if isinstance(arg_name, (list, tuple, set)):
                arg_list.extend(arg_name)
            else:
                arg_list.append(arg_name)
            if more_arg_names:
                arg_list.extend(more_arg_names)

            arg_list = set(arg_list)

            for a in arg_list:
                if a not in param_signature:
                    raise NameError(f'Required argument {a} not found in function {f!r} -> {param_signature!r}')
                required_params.add(a)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            given_params = _map_args_to_params(param_signature, args, kwargs)
            for p in required_params:
                val = given_params[p]
                if val is None:
                    raise errors.api.InvalidArgument(f'required parameter "{p}" missing [{f!r}]')
                else:
                    if typecheck:
                        if not castutils.check_type(val, param_signature[p].annotation):
                            raise errors.api.InvalidArgument(f'required parameter "{p}" type is {type(val)} but should be {param_signature[p].annotation} [{f!r}]')

            return f(*args, **kwargs)
        return wrapper
    if arg_is_func:
        return wrap(func)
    return wrap


def takes_context(context_arg_name='context', optional=True):
    arg_is_func = False
    func = None
    if isinstance(context_arg_name, typing.Callable):
        arg_is_func = True
        func = context_arg_name
        context_arg_name = 'context'

    def wrap(f):
        param_signature: typing.Dict[str, inspect.Parameter] = dict(inspect.signature(f).parameters)

        if context_arg_name not in param_signature:
            if not optional:
                raise NameError(f'Context argument {context_arg_name} (non-optional) not found in function {f!r} -> {param_signature!r}')
        else:
            setattr(f, '__takes_context_as__', context_arg_name)

        return f
    if arg_is_func:
        return wrap(func)
    return wrap
