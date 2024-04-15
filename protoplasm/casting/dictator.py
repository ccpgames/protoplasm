__all__ = [
    'proto_to_dict',
    'dataclass_to_dict',
]
from protoplasm.casting import dictators
from protoplasm.structs import *

from google.protobuf import json_format

import logging
log = logging.getLogger(__name__)


def proto_to_dict(proto: GeneratedProtocolMessageType) -> Dict:
    """Turns a Protobuf message object into a dict.
    """
    return json_format.MessageToDict(proto,
                                     preserving_proto_field_name=True,
                                     use_integers_for_enums=True)


def dataclass_to_dict(dc) -> Dict:
    """Turns a Dataclass object into a dict with the data values serialized so
    that they can be turned into Protobuf objects.

    This will also turn non-proto related dataclasses into dicts but those won't
     necessarily be usable to build Protobuf messages as this will simply use
     the asdict call in the standard dataclass library.

    :param dc: The dataclass to turn into a dict
    :return: A dictionary of Proto-ready values.
    """
    if not hasattr(dc, '__proto_cls__'):  # Plain dataclass
        return dataclasses.asdict(dc)

    d = {}
    for field in dataclasses.fields(dc):
        dicted = _dataclass_field_to_dict_field(field, dc)
        # if dicted:
        if dicted is not None:  # TODO(thordurm@ccpgames.com>) 2024-04-15: To include "default/empty" fields or not?
            d[_get_proto_field_name(field)] = dicted

    return d


def _get_proto_field_name(field: dataclasses.Field):
    return field.metadata.get('pb_name', field.name)


def _dataclass_field_to_dict_field(field: dataclasses.Field, dc):
    val = getattr(dc, field.name)

    if val is None:
        return None

    dictator_cls = field.metadata.get('dictator', dictators.BaseDictator)
    is_obj = field.metadata.get('is_obj', False)
    is_list = field.metadata.get('is_list', False)
    is_map = field.metadata.get('is_map', False)

    if is_obj:
        if is_map:
            return {k: dataclass_to_dict(v) for k, v in val.items()} if val else None
        elif is_list:
            return [dataclass_to_dict(v) for v in val] if val else None
        else:
            return dataclass_to_dict(val)
    else:
        if is_map:
            return {k: dictator_cls.to_dict_value(v, field, dc) for k, v in val.items()} if val else None
        elif is_list:
            return [dictator_cls.to_dict_value(v, field, dc) for v in val] if val else None
        else:
            return dictator_cls.to_dict_value(val, field, dc)
