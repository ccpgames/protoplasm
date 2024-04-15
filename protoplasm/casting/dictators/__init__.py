__all__ = [
    'BaseDictator',
    'TimestampDictator',
    'ByteDictator',
    'EnumDictator',
    'LongDictator',
    'DurationDictator',
    'AnyDictator',
]
import datetime
import base64
import dataclasses
from ccptools import dtu
import enum
import collections

from protoplasm.structs import *
from protoplasm.casting import castutils


class BaseDictator:
    @classmethod
    def to_dict_value(cls, dc_value: Any, field: dataclasses.Field, parent: DataclassBase) -> Any:
        """Casts data from whatever a dataclass stores to a value that protobuf
        messages can parse from a dict.

        :param dc_value: Dataclass value
        :type dc_value: Any
        :param field: The dataclass field descriptor the value comes from
        :type field: dataclasses.Field
        :param parent: The dataclass the field belongs to
        :type parent: object
        :return: A value that the protobuf ParseDict function can use
        :rtype: Any
        """
        return dc_value

    @classmethod
    def from_dict_value(cls, proto_value: Any, field: dataclasses.Field, parent_type: Type[DataclassBase]) -> Any:
        """Casts data from a dict version of a protobuf message into whatever
        value the corresponding dataclass uses.

        :param proto_value: Protobuf dict value
        :type proto_value: Any
        :param field: The dataclass field descriptor the value is going to
        :type field: dataclasses.Field
        :param parent_type: The dataclass the field belongs to
        :type parent_type: object
        :return: A value that the dataclass uses
        :rtype: Any
        """
        return proto_value


class TimestampDictator(BaseDictator):
    @classmethod
    def to_dict_value(cls, dc_value: Optional[datetime.datetime],
                      field: dataclasses.Field, parent: DataclassBase) -> Optional[str]:
        """Casts data from a dataclass datetime values to iso string (with
        tailing Z).

        Format: %Y-%m-%dT%H:%M:%S.%fZ

        :param dc_value: Dataclass value of a python datetime
        :type dc_value: datetime.datetime | None
        :param field: The dataclass field descriptor the value comes from
        :type field: dataclasses.Field
        :param parent: The dataclass the field belongs to
        :type parent: object
        :return: Datetime as an iso string (with trailing Z)
        :rtype: str | None
        """
        if not dc_value:
            return None

        if not isinstance(dc_value, datetime.datetime):
            raise TypeError(f'TimestampDictator.to_dict_value expected datetime, got {type(dc_value)}')

        if dc_value.microsecond:
            return dc_value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return dc_value.strftime('%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    def from_dict_value(cls, proto_value: Optional[str],
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> Optional[datetime.datetime]:
        """Casts a timestamp value from a iso-string (with trailing Z) to a
        datetime.

        Format: %Y-%m-%dT%H:%M:%S.%fZ

        :param proto_value: Protobuf dict value of an iso-string (with trailing Z)
        :type proto_value: str | None
        :param field: The dataclass field descriptor the value is going to
        :type field: dataclasses.Field
        :param parent_type: The dataclass the field belongs to
        :type parent_type: object
        :return: A python datetime value
        :rtype: datetime.datetime | None
        """
        if not proto_value:
            return None

        val = dtu.any_to_datetime(proto_value, None)
        if val is None:
            raise ValueError(f'TimestampDictator.from_dict_value failed to convert "{proto_value!r}" to datetime')

        return val


class ByteDictator(BaseDictator):
    @classmethod
    def to_dict_value(cls, dc_value: Optional[bytes],
                      field: dataclasses.Field, parent: DataclassBase) -> str:
        """Casts data from python bytes to base64 encoded string (bytes)

        :param dc_value: Dataclass value of python bytes
        :type dc_value: bytes | None
        :param field: The dataclass field descriptor the value comes from
        :type field: dataclasses.Field
        :param parent: The dataclass the field belongs to
        :type parent: object
        :return: A base64 encoded string (bytes) version of the bytes
        :rtype: bytes
        """
        if not dc_value:
            return ''

        if not isinstance(dc_value, bytes):
            raise TypeError(f'ByteDictator.to_dict_value expected bytes, got {type(dc_value)}')

        return base64.encodebytes(dc_value).decode('utf-8').strip()

    @classmethod
    def from_dict_value(cls, proto_value: Optional[Union[str, bytes]],
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> bytes:
        """Casts a base64 encodes string of bytes into python bytes from a iso-string (with trailing Z) to a
        datetime.

        :param proto_value: Protobuf dict value of a base64 endoced string
        :type proto_value: str | bytes | None
        :param field: The dataclass field descriptor the value is going to
        :type field: dataclasses.Field
        :param parent_type: The dataclass the field belongs to
        :type parent_type: object
        :return: A python bytes value
        :rtype: bytes | None
        """
        if not proto_value:
            return b''

        if isinstance(proto_value, bytes):
            return proto_value

        if isinstance(proto_value, str):
            return base64.decodebytes(proto_value.encode('utf-8'))


class EnumDictator(BaseDictator):
    @classmethod
    def to_dict_value(cls, dc_value: Optional[Union[int, enum.IntEnum]],
                      field: dataclasses.Field, parent: DataclassBase) -> int:
        """Casts data from python enum type to plain int for Protobuf

        :param dc_value: Dataclass value of python enum
        :type dc_value: int | enum.IntEnum | None
        :param field: The dataclass field descriptor the value comes from
        :type field: dataclasses.Field
        :param parent: The dataclass the field belongs to
        :type parent: object
        :return: Integer value of the enum
        :rtype: int | None
        """
        if dc_value is None:
            return 0

        if isinstance(dc_value, enum.IntEnum):
            return dc_value.value

        return dc_value

    @classmethod
    def from_dict_value(cls, proto_value: Optional[Union[int, str]],
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> enum.IntEnum:
        """Casts an integer or string from a Protobuf enum into a Python enum object.

        :param proto_value: Protobuf int or string version of an enum
        :type proto_value: int | str | None
        :param field: The dataclass field descriptor the value is going to
        :type field: dataclasses.Field
        :param parent_type: The dataclass the field belongs to
        :type parent_type: object
        :return: A Python enum.IntEnum object
        :rtype: enum.IntEnum | None
        """
        if proto_value is None:
            proto_value = 0

        enum_type: enum.EnumMeta = castutils.get_dc_field_obj_type(field, parent_type)

        if isinstance(proto_value, str):
            return enum_type[proto_value]

        return enum_type(proto_value)


class LongDictator:
    @classmethod
    def to_dict_value(cls, dc_value: Union[str, int], field: dataclasses.Field, parent: DataclassBase) -> str:
        """

        :param dc_value: Dataclass value
        :type dc_value: Any
        :param field: The dataclass field descriptor the value comes from
        :type field: dataclasses.Field
        :param parent: The dataclass the field belongs to
        :type parent: object
        :return: A value that the protobuf ParseDict function can use
        :rtype: Any
        """
        if dc_value is None:
            return '0'
        return str(dc_value)

    @classmethod
    def from_dict_value(cls, proto_value: Union[str, int],
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> int:
        """

        :param proto_value: Protobuf dict value
        :type proto_value: Any
        :param field: The dataclass field descriptor the value is going to
        :type field: dataclasses.Field
        :param parent_type: The dataclass the field belongs to
        :type parent_type: object
        :return: A value that the dataclass uses
        :rtype: Any
        """
        if proto_value is None:
            return 0
        return int(proto_value)


class DurationDictator:
    @classmethod
    def to_dict_value(cls, dc_value: datetime.timedelta,
                      field: dataclasses.Field, parent: DataclassBase) -> Optional[str]:
        """google.protobuf.duration
        datetime.timedelta -> '123.456789s'
        """
        if dc_value is None:
            return None

        return f'{dc_value.total_seconds():f}s'

    @classmethod
    def from_dict_value(cls, proto_value: Union[str, int, float],
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> Optional[datetime.timedelta]:
        """google.protobuf.duration
        '123.456789s' -> datetime.timedelta
        """
        if proto_value is None:
            return None

        if isinstance(proto_value, str):
            proto_value = proto_value.strip().lower()
            if proto_value[-1] == 's':
                proto_value = proto_value[:-1]
            proto_value = float(proto_value)

        return datetime.timedelta(seconds=proto_value)


class AnyDictator:
    @classmethod
    def to_dict_value(cls, dc_value: Optional[DataclassBase],
                      field: dataclasses.Field, parent: DataclassBase) -> Optional[collections.OrderedDict]:
        """google.protobuf.Any
        DataclassBase -> OrderedDict([('@type', '?'), ('key_1', 'value_1'), ('key_n', 'value_n')])
        """
        if dc_value is None:
            return None

        from protoplasm.casting.dictator import dataclass_to_dict
        from protoplasm.casting import castutils

        base_dict = dataclass_to_dict(dc_value)

        ordered_dict = collections.OrderedDict()
        ordered_dict['@type'] = castutils.get_type_url(dc_value.__proto_cls__)

        ordered_dict.update(base_dict)
        return ordered_dict

    @classmethod
    def from_dict_value(cls, proto_value: collections.OrderedDict,
                        field: dataclasses.Field, parent_type: Type[DataclassBase]) -> Optional[DataclassBase]:
        """google.protobuf.Any
        OrderedDict([('@type', '?'), ('key_1', 'value_1'), ('key_n', 'value_n')]) -> DataclassBase
        """
        if proto_value is None or '@type' not in proto_value:
            return None

        from protoplasm.casting import castutils
        from protoplasm.casting.objectifier import dict_to_dataclass

        type_url = proto_value.pop('@type')
        proto_class = castutils.get_proto_descriptor_by_type_url(type_url)._concrete_class  # noqa
        dc_cls = castutils.import_dataclass_by_proto(proto_class)

        return dict_to_dataclass(dc_cls, proto_value)
