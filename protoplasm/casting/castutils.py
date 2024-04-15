__all__ = [
    'force_object',
    'kwdict',
    'import_dataclass_by_proto',
    'get_type_from_module_import_as',
    'get_dc_field_obj_type',
    'humps_to_under',
    'check_type',
    'get_type_url',
    'get_type_name_from_url',
    'get_proto_descriptor_by_type_url',
    'get_proto_file_by_type_url',
    'base64_stripper',
    'base64_filler',
    'fuzzy_base64_to_bytes',
]

from collections import abc
import sys
import re
import builtins
import base64
import typing
import enum

from google.protobuf import symbol_database
from google.protobuf import json_format
from ccptools.tpu import strimp

from protoplasm.structs import *

import logging
log = logging.getLogger(__name__)


T_ANY_CLASS = TypeVar('T_ANY_CLASS')

TYPING_MATCHER = re.compile(r'typing.(?P<type>[a-zA-Z]+)\[(?P<inner>[a-zA-Z0-9.,_ ]+)]')
STAR_IMPORT_TYPING_MATCHER = re.compile(r'(?P<type>List|Dict)\[(?P<inner>.+)]')

_POST_39 = sys.version_info >= (3, 9)


def force_object(object_cls: Type[T_ANY_CLASS], value: Any) -> T_ANY_CLASS:
    """Takes a `value` in the form of a single argument, list of arguments, a
    dict of keyword arguments or an object of type `object_cls`.

    If the value is already an object of type `object_cls` or a `None`, it's
    simply returned as is.

    If the `value` is a single argument variable, it is used as the first (and
    only) arg to instantiate a new object of the `object_cls` type which is then
    returned.

    If the `value` is a `list` or `tuple`, the values therein are used as
    `*args` to instantiate a new object of the `object_cls` type which is then
    returned.

    If the `value` is a `dict`, the keys and values therein are used as
    `**kwargs` to  instantiate a new object of the `object_cls` type which is
    then returned.

    This guarantees a return value of either an object of `object_cls` type, a
    none or a raised `Exception`, e.g. if the supplied `value` can't be used as
    `__init__()` arguments in the `object_cls` (most likely a `TypeError` or
    `ValueError`) or if the `__init__()` of that class raises any other
    exception.

    If you need a `None` value forced into a new empty instance of the given
    `object_cls` a simple way to achieve that is:

    ```my_foo = force_object(Foo, my_values) or Foo()```

    One thing worth mentioning is that if `object_cls` takes a `list`, `tuple`
    or a `dict` as it's first `__init__()` argument and the given `value` is of
    that same type and intended to be used as the first and only argument for
    the `__init__()`, that will not work as `value` of those three types will be
    treated as a collection of `*args` or mapping og `**kwargs` for the
    `__init__()` instead of a single argument.

    Solutions to that include:
     - Not using this function for classes that take `list`, `tuple` or `dict`
       as their first arguments. This isn't intended to be a universal solution
       that fits all cases and classes so if you have a square hole, don't use a
       round peg. ;)
     - Wrapping the `value` in a `list` or `tuple` of its own before passing it
       to this function as that will get treated as a list of `*args` for the
       `__init__()`, with the inner `list`, `tuple` or `dict` used correctly as
       the first (and only) argument.
        - This may however not work correctly if `value` is a None and the
          `__init__()` doesn't take kindly to None values for the argument it
          expects to be a `list`, `tuple` or `dict`

    :param object_cls: The class/type to force the given value into
    :param value:
    :type value:
    :return:
    :rtype:
    """
    if value is None or isinstance(value, object_cls):
        return value
    if isinstance(value, dict):
        return object_cls(**value)
    elif isinstance(value, (list, tuple)):
        return object_cls(*value)
    else:
        return object_cls(value)


def kwdict(**kwargs) -> dict:
    """Takes kwargs and turns into a dict using double underscores in order to
    build nested dicts.

    Examples:

    >>> kwdict(foo='one', bar='two')
    {'foo': 'one', 'bar': 'two'}

    >>> kwdict(foo='one', bar__one=1, bar__two=2)
    {'foo': 'one', 'bar': {'one': 1, 'two': 2}}
    """
    d = {}
    subs = {}
    for k, v in kwargs.items():
        first, *rest = k.split('__', 1)
        if rest:
            if first not in subs:
                subs[first] = {}
            subs[first][rest[0]] = v
        else:
            d[first] = v

    for k, v in subs.items():
        d[k] = kwdict(**v)

    return d


def import_dataclass_by_proto(proto_class: GeneratedProtocolMessageType) -> Type[DataclassBase]:
    """Dynamically imports and returns the dataclass type corresponding to the
    given Protobuf message class.

    This will also cache that dataclass type in the Protobuf message class in
    order to speed up subsequent future imports by a tiny tiny fraction.

    :param proto_class: The Protobuf message class that we need to find the
                        dataclass version of.
    """
    cls = getattr(proto_class, '__dataclass_cls__', None)
    if not cls:
        if not isinstance(proto_class, type):
            proto_class = proto_class.__class__
        cls = strimp.get_class(''.join([proto_class.__module__[:-3], 'dc.', proto_class.__name__]), reraise=True)
        setattr(proto_class, '__dataclass_cls__', cls)
    return cls


# TODO(thordurm@ccpgames.com>): Maybe this should live in typeutils strimp?!?
def get_type_from_module_import_as(type_name: str, cls: Type) -> Type:
    cls_module = sys.modules.get(cls.__module__)
    if not cls_module:
        raise ImportError(f'get_type_from_module_import_as failed to find {cls.__module__} in sys.modules')

    if '.' in type_name:
        m = TYPING_MATCHER.match(type_name)
        if m:  # From 'typing' (this is pre-version 4.1 stuff, kept in for backwards compatibility)
            return _get_from_typing(m.group('type'), m.group('inner'), cls)
        else:
            m = STAR_IMPORT_TYPING_MATCHER.match(type_name)
            if m:  # From 'typing' via 'from typing import *'
                return _get_from_typing(m.group('type'), m.group('inner'), cls)

            else:  # From somewhere else
                as_name, type_name = type_name.rsplit('.', 1)
                cls_module = sys.modules.get(cls.__module__)
                if not cls_module:
                    raise ImportError(f'get_type_from_module_import_as failed to find {cls.__module__} in sys.modules')

                alias_module = cls_module
                for as_part in as_name.split('.'):
                    alias_module = getattr(alias_module, as_part, None)

                    if not alias_module:
                        raise ImportError(f'get_type_from_module_import_as failed to find {as_name} in {cls_module}')
    else:
        builtin_type = getattr(builtins, type_name, None)
        if not builtin_type:
            m = STAR_IMPORT_TYPING_MATCHER.match(type_name)
            if m:  # From 'typing' via 'from typing import *'
                return _get_from_typing(m.group('type'), m.group('inner'), cls)
        else:
            if isinstance(builtin_type, type):
                return builtin_type

        alias_module = cls_module

    actual_type = getattr(alias_module, type_name, None)
    if not actual_type:
        raise ImportError(f'get_type_from_module_import_as failed to find {actual_type} in {alias_module}')

    return actual_type


def _get_from_typing(type_name: str, inner_str: str, cls: Type) -> Type:
    typing_type = getattr(typing, type_name, None)  # E.g. List
    if not typing_type:
        raise ImportError(f'get_type_from_module_import_as->_get_from_typing failed to find {type_name} in typing module')
    if inner_str:
        args = tuple([get_type_from_module_import_as(a.strip(), cls) for a in inner_str.split(',')])
        return typing_type[args]
    return typing_type


def get_dc_field_obj_type(dc_field: dataclasses.Field,
                          parent_dataclass: Type[DataclassBase]) -> Union[Type, Type[DataclassBase], enum.EnumMeta]:
    """Fetches the "actual" type of a dataclass field. In the case of lists and
    maps/dicts this means the type of the values the lists/maps/dicts contain.

    This assumes a dataclass generated by protoplasm.

    :param dc_field: The dataclass field who's type we need.
    :param parent_dataclass: The dataclass itself
    :return: The type defined in the dataclass field
    """
    if isinstance(dc_field.type, str):
        dc_field.type = get_type_from_module_import_as(dc_field.type, parent_dataclass)

    if dc_field.metadata.get('is_map', False):
        return dc_field.type.__args__[1]
    elif dc_field.metadata.get('is_list', False):
        return dc_field.type.__args__[0]
    else:
        return dc_field.type


def humps_to_under(string: str) -> str:
    buf = []
    if string.endswith('ID'):
        if len(string) > 2 and string[-3].islower():
            string = f'{string[:-2]}_id'
        else:
            return string.lower()

    for i, c in enumerate(string):
        if c.isupper():
            if i != 0:
                buf.append('_')
            c = c.lower()
        buf.append(c)
    return ''.join(buf)


def check_type(val: Any, type_or_annotation: Any) -> bool:
    # TODO(thordurm@ccpgames.com>): Move to or copy to typeutils

    def _is_special(toa: Any) -> bool:
        if _POST_39:
            if isinstance(toa, typing._SpecialGenericAlias):  # noqa
                return True
        else:
            return toa._special  # noqa

    if val is None and type_or_annotation is None:
        return True

    m = getattr(type_or_annotation, '__module__', None)
    if m == 'typing':
        if type_or_annotation == Any:
            return True
        if isinstance(type_or_annotation, typing._GenericAlias):  # noqa
            if _is_special(type_or_annotation):  # noqa Not subscripted
                return isinstance(val, type_or_annotation.__origin__)

            else:
                if type_or_annotation.__origin__ == Union:
                    if not type_or_annotation.__args__:
                        return True
                    if Any in type_or_annotation.__args__:
                        return True
                    return isinstance(val, type_or_annotation.__args__)

                elif type_or_annotation.__origin__ in (list, set):  # Check list and set
                    if not isinstance(val, type_or_annotation.__origin__):
                        return False
                    if not type_or_annotation.__args__ or Any in type_or_annotation.__args__:
                        return True
                    for sub_val in val:
                        if not check_type(sub_val, Union[type_or_annotation.__args__]):
                            return False
                    return True  # Should be good now! :)

                elif type_or_annotation.__origin__ == tuple:  # Check tuple!
                    if not isinstance(val, tuple):
                        return False
                    if not type_or_annotation.__args__:
                        return True

                    if type_or_annotation.__args__[-1] is ... and len(type_or_annotation.__args__) == 2:
                        for sub_val in val:
                            if not check_type(sub_val, Union[type_or_annotation.__args__[0]]):
                                return False
                        return True  # Should be good now! :)

                    if len(type_or_annotation.__args__) != len(val):
                        return False

                    for i, sub_val in enumerate(val):
                        if not check_type(sub_val, Union[type_or_annotation.__args__[i]]):
                            return False

                    return True  # Should be good now! :)

                elif issubclass(type_or_annotation.__origin__, abc.Mapping):
                    if not isinstance(val, type_or_annotation.__origin__):
                        return False
                    if not type_or_annotation.__args__ or type_or_annotation.__args__ == (Any, Any):
                        return True

                    for k, v in val.items():
                        if not (check_type(k, Union[type_or_annotation.__args__[0]]) and check_type(v, Union[type_or_annotation.__args__[1]])):
                            return False
                    return True
                else:
                    log.warning('I do not know how to check type %r of typing module:(', type_or_annotation)
        if isinstance(type_or_annotation, TypeVar):
            # TODO(thordurm@ccpgames.com>): Not really tested and supported yet officially...
            # TODO(thordurm@ccpgames.com>): Main issue is nested types (if they don't flatten)
            return check_type(val, Union[type_or_annotation.__constraints__])
    return isinstance(val, type_or_annotation)


def get_type_url(proto: GeneratedProtocolMessageType, prefix: str = 'type.googleapis.com/') -> str:
    # TODO(thordurm@ccpgames.com>) 2024-04-15: Not sure how best to support any prefix other than "type.googleapis.com/" here
    if not prefix:
        return f'/{proto.DESCRIPTOR.full_name}'
    if prefix[-1] == '/':
        return f'{prefix}{proto.DESCRIPTOR.full_name}'
    return f'{prefix}/{proto.DESCRIPTOR.full_name}'


def get_type_name_from_url(type_url: str) -> str:
    # TODO(thordurm@ccpgames.com>) 2024-04-15: Not sure how best to support any prefix other than "type.googleapis.com/" here
    return type_url.split('/')[-1]


def get_proto_descriptor_by_type_url(type_url: str) -> json_format.descriptor.Descriptor:
    # TODO(thordurm@ccpgames.com>) 2024-04-15: Not sure how best to support any prefix other than "type.googleapis.com/" here
    type_name = get_type_name_from_url(type_url)
    db = symbol_database.Default()
    try:
        message_descriptor = db.pool.FindMessageTypeByName(type_name)
    except KeyError:
        raise TypeError('Can not find message descriptor by type_url: {0}. You may need to import the pb2 file'
                        ' before it registers in the SymbolDatabase'.format(type_url))
    return message_descriptor


def get_proto_file_by_type_url(type_url: str) -> json_format.descriptor.FileDescriptor:
    # TODO(thordurm@ccpgames.com>) 2024-04-15: Not sure how best to support any prefix other than "type.googleapis.com/" here
    type_name = get_type_name_from_url(type_url)
    db = symbol_database.Default()
    try:
        file_descriptor = db.pool.FindFileContainingSymbol(type_name)
    except KeyError:
        raise TypeError('Can not find file descriptor by type_url: {0}. You may need to import the pb2 file before'
                        ' it registers in the SymbolDatabase'.format(type_url))
    return file_descriptor


def base64_stripper(base64str: Union[bytes, str]) -> bytes:
    if isinstance(base64str, str):
        base64str = base64str.encode()
    return base64str.strip().replace(b'\r', b'').replace(b'\n', b'').replace(b'\t', b'').replace(b'=', b'')


def base64_filler(base64str: Union[bytes, str]) -> bytes:
    if isinstance(base64str, str):
        base64str = base64str.encode()
    base64str = base64str.strip().replace(b'\r', b'').replace(b'\n', b'').replace(b'\t', b'')
    return base64str + b'=' * (4 - (len(base64str) % 4) or 4)


def fuzzy_base64_to_bytes(base64str: Union[bytes, str]) -> bytes:
    return base64.decodebytes(base64_filler(base64str))
