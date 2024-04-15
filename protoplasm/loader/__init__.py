__all__ = [
    'get_dataclass_by_message_name',
]

import typing
from google.protobuf import symbol_database
from protoplasm.bases import dataclass_bases
from protoplasm.casting import castutils

import logging
log = logging.getLogger(__name__)


def get_dataclass_by_message_name(message_name: str) -> typing.Type[dataclass_bases.DataclassBase]:
    sym_db = symbol_database.Default()
    proto_msg = sym_db.pool.FindMessageTypeByName(message_name)
    return castutils.import_dataclass_by_proto(proto_msg._concrete_class)
