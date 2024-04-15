from __future__ import annotations

__all__ = [
    'DataclassBase',
    'T_DCB',  # Required...?!?
]

import json
import base64

from protoplasm.structs._base import *
import dataclasses

import logging
log = logging.getLogger(__name__)

T_DCB = TypeVar('T_DCB', bound='DataclassBase')


@dataclasses.dataclass
class DataclassBase(Generic[T_DCB]):
    __proto_cls__: ClassVar[GeneratedProtocolMessageType]

    def __post_init__(self):
        from protoplasm.casting import castutils
        for f in dataclasses.fields(self):
            if f.metadata.get('is_obj', False):
                f_val = getattr(self, f.name, None)
                if f_val:
                    f_type = castutils.get_dc_field_obj_type(f, self)
                    if f.metadata.get('is_map', False):
                        for k in f_val.keys():
                            f_val[k] = castutils.force_object(f_type, f_val[k])
                    elif f.metadata.get('is_list', False):
                        for i in range(len(f_val)):
                            f_val[i] = castutils.force_object(f_type, f_val[i])
                    else:
                        setattr(self, f.name, castutils.force_object(f_type, f_val))

    def to_dict(self) -> Dict:
        """Turns this `DataclassBase` into a dict of its fields and values
        recursively and returns, so for any field value that is itself a
        `DataclassBase`, `to_dict` is also called, resulting in a nested dict of
        only "primitive" (and JSON serializable) values.
        """
        from protoplasm import casting
        return casting.dataclass_to_dict(self)

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_proto(self) -> GeneratedProtocolMessageType:
        from protoplasm import casting
        return casting.dataclass_to_proto(self)

    def to_protostr(self) -> bytes:
        from protoplasm import casting
        return casting.dataclass_to_proto(self).SerializeToString()

    def to_base64(self) -> bytes:
        return base64.encodebytes(self.to_protostr()).strip().replace(b'\r',
                                                                      b'').replace(b'\n', b'').replace(b'\t', b'')

    def unpack(self) -> Dict[str, Any]:
        """Returns a dict with the fields of this `DataclassBase` as keys and
        their values as they are.

        The main difference between this and the `to_dict` method is that
        `to_dict` is recursive so on any field value that is itself a
        `DataclassBase`, `to_dict` is also called, resulting in a nested dict of
        only "primitive" (and JSON serializable) values.

        This `unpack` method on the other hand will leave any `DataclassBase`
        values be.

        The main use-case for this method is to "unpack"/"explode"/"break up" a
        gRPC Proto Service Request/Response message up into individual method
        arguments.
        """
        d = {}
        for field in dataclasses.fields(self):
            d[field.name] = getattr(self, field.name)
        return d

    def explode(self) -> Optional[Union[Tuple[Any], Any]]:
        """Returns a tuple with the field values of this `DataclassBase` or if
        this `DataclassBase` only contains one field, returns that field's value
        alone.

        This is similar to the `unpack()` method except this only returns values
        and if there's only a single field (as many RPC Response messages do),
        it's not wrapped in a tuple.

        The main use-case for this method is to "unpack" a gRPC Proto Service
        RPC Unary Response message up into individual return values (often just
        one).
        """
        tu = []
        for field in dataclasses.fields(self):
            tu.append(getattr(self, field.name))
        if not tu:
            return  # We can theoretically have "empty" Response message classes
        if len(tu) == 1:
            return tu[0]
        return tuple(tu)

    @classmethod
    def from_kwdict(cls, **kwargs) -> T_DCB:
        from protoplasm.casting import castutils
        return cls.from_dict(castutils.kwdict(**kwargs))

    @classmethod
    def from_dict(cls, dict_data: dict, ignore_extras: bool = False) -> T_DCB:
        from protoplasm import casting
        return casting.dict_to_dataclass(cls, dict_data, ignore_extras)

    @classmethod
    def from_json(cls, json_string: str) -> T_DCB:
        return cls.from_dict(json.loads(json_string))

    @classmethod
    def from_proto(cls, proto: GeneratedProtocolMessageType) -> T_DCB:
        from protoplasm import casting
        return cls.from_dict(casting.proto_to_dict(proto))

    @classmethod
    def from_protostr(cls, protostr: bytes) -> T_DCB:
        proto = cls.__proto_cls__()
        proto.ParseFromString(protostr)
        return cls.from_proto(proto)

    @classmethod
    def from_base64(cls, base64str: Union[bytes, str]) -> T_DCB:
        from protoplasm.casting import castutils
        return cls.from_protostr(castutils.fuzzy_base64_to_bytes(base64str))

    @classmethod
    def from_clone(cls, clone: DataclassBase) -> T_DCB:
        return cls.from_dict(clone.to_dict(), ignore_extras=True)
