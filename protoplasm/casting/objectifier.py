__all__ = [
    'dict_to_proto',
    'dict_to_dataclass',
]
from google.protobuf import json_format
from protoplasm.casting import dictators
from protoplasm.casting import castutils
from protoplasm.structs import *
import dataclasses

import logging

log = logging.getLogger(__name__)


def dict_to_proto(proto_class: Type[GeneratedProtocolMessageType],
                  dict_data: Optional[Dict] = None) -> GeneratedProtocolMessageType:
    """Creates a new instance of the given Protobuf class/type and populates it
    with the data given in the dict.

    :param proto_class: Protobuf class to create
    :param dict_data: Python dict with the data to populate the object with
    :return: A populated Protobuf object (message)
    """
    proto = proto_class()
    json_format.ParseDict(dict_data or {}, proto)
    return proto


def _get_proto_field_name(field: dataclasses.Field):
    return field.metadata.get('pb_name', field.name)


def dict_to_dataclass(dataclass_type: Type[T_DCB], dict_data: Optional[Dict] = None, ignore_extras: bool = False) -> T_DCB:
    """Creates a new instance of the given dataclass type and populates it
    (recursively) with the data given in the dict.

    :param dataclass_type: Dataclass type to create
    :param dict_data: Python dict with the data to populate the object with
    :param ignore_extras: Should dict keys that aren't fields in the target
                          dataclass type be ignored or should they raise
                          ValueErrors?
    :return: A populated Dataclass object
    """
    if not dict_data:
        return dataclass_type()
    if isinstance(dict_data, dict):
        new_dict = {}
        field_map = {_get_proto_field_name(f): f for f in dataclasses.fields(dataclass_type)}  # type: Dict[str, dataclasses.Field]
        for k, v in dict_data.items():
            field = field_map.get(k, None)

            if field:
                is_obj = field.metadata.get('is_obj', False)
                is_list = field.metadata.get('is_list', False)
                is_map = field.metadata.get('is_map', False)
                if is_obj:
                    field_type = castutils.get_dc_field_obj_type(field, dataclass_type)
                    if is_map:
                        new_dict[field.name] = {vk: dict_to_dataclass(field_type, vv, ignore_extras) for vk, vv in v.items()}
                    elif is_list:
                        new_dict[field.name] = [dict_to_dataclass(field_type, vv, ignore_extras) for vv in v]
                    else:
                        new_dict[field.name] = dict_to_dataclass(field_type, v, ignore_extras)
                else:
                    dictator = field.metadata.get('dictator', dictators.BaseDictator)
                    if is_map:
                        new_dict[field.name] = {vk: dictator.from_dict_value(vv, field, dataclass_type) for vk, vv in v.items()}
                    elif is_list:
                        new_dict[field.name] = [dictator.from_dict_value(vv, field, dataclass_type) for vv in v]
                    else:
                        new_dict[field.name] = dictator.from_dict_value(v, field, dataclass_type)
            elif not ignore_extras:
                raise ValueError(f'Field "{field.name}" not found in dataclass "{dataclass_type}"')
        return dataclass_type(**new_dict)
    elif isinstance(dict_data, (list, tuple)):
        new_dict = {}
        for field, v in zip(dataclasses.fields(dataclass_type), dict_data):
            dictator = field.metadata.get('dictator', dictators.BaseDictator)
            new_dict[field.name] = dictator.from_dict_value(v, field, dataclass_type)
        return dataclass_type(**new_dict)
    else:
        field = dataclasses.fields(dataclass_type)[0]
        dictator = field.metadata.get('dictator', dictators.BaseDictator)
        return dataclass_type(dictator.from_dict_value(dict_data, field, dataclass_type))
