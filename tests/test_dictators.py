import unittest
import datetime
import dataclasses
import base64
import enum

import protoplasm.bases.dataclass_bases
from protoplasm.casting import dictators
from protoplasm import bases
import collections

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import os
import sys
import sys
import shutil
import time
HERE = os.path.dirname(__file__)
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')


class FauxEnum(enum.IntEnum):
    DEFAULT = 0
    FOO = 1
    BAR = 2
    OOF = 3
    RAB = 4


@dataclasses.dataclass
class FauxDataClass(protoplasm.bases.dataclass_bases.DataclassBase):
    string: str = dataclasses.field(default=None)
    integer: int = dataclasses.field(default=None)
    floating: float = dataclasses.field(default=None)
    boolean: bool = dataclasses.field(default=None)
    real_bytes: bytes = dataclasses.field(default=None)
    timestamp: datetime.datetime = dataclasses.field(default=None)
    enumerator: FauxEnum = dataclasses.field(default=None)
    duration: datetime.timedelta = dataclasses.field(default=None)
    any: protoplasm.bases.dataclass_bases.DataclassBase = dataclasses.field(default=None)


def _get_field_map(dc):
    return {f.name: f for f in dataclasses.fields(dc)}


def _get_test_args(dc, field_name):
    return getattr(dc, field_name), _get_field_map(dc)[field_name], dc


class BaseDictatorTest(unittest.TestCase):
    def test_none_to_dict_value(self):
        caster = dictators.BaseDictator.to_dict_value
        dc = FauxDataClass()
        self.assertIsNone(dc.string)
        self.assertIsNone(caster(*_get_test_args(dc, 'string')))

        self.assertIsNone(dc.integer)
        self.assertIsNone(caster(*_get_test_args(dc, 'integer')))

        self.assertIsNone(dc.floating)
        self.assertIsNone(caster(*_get_test_args(dc, 'floating')))

        self.assertIsNone(dc.boolean)
        self.assertIsNone(caster(*_get_test_args(dc, 'boolean')))

    def test_to_dict_value(self):
        caster = dictators.BaseDictator.to_dict_value
        dc = FauxDataClass(string='Ðiss is a júníkód stíng viþþ tjænís skvígglí bitts 中國潦草的位',
                           integer=4815162342,
                           floating=3.14159265359,
                           boolean=True)

        self.assertIsNotNone(dc.string)
        self.assertIsInstance(dc.string, str)
        self.assertEqual('Ðiss is a júníkód stíng viþþ tjænís skvígglí bitts 中國潦草的位',
                         caster(*_get_test_args(dc, 'string')))

        self.assertIsNotNone(dc.integer)
        self.assertIsInstance(dc.integer, int)
        self.assertEqual(4815162342, caster(*_get_test_args(dc, 'integer')))

        self.assertIsNotNone(dc.floating)
        self.assertIsInstance(dc.floating, float)
        self.assertEqual(3.14159265359, caster(*_get_test_args(dc, 'floating')))

        self.assertIsNotNone(dc.boolean)
        self.assertIsInstance(dc.boolean, bool)
        self.assertEqual(True, caster(*_get_test_args(dc, 'boolean')))

    def test_none_from_dict_value(self):
        caster = dictators.BaseDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.string)
        dc.string = caster(None, _get_field_map(dc)['string'], dc.__class__)
        self.assertIsNone(dc.string)

        self.assertIsNone(dc.integer)
        dc.integer = caster(None, _get_field_map(dc)['integer'], dc.__class__)
        self.assertIsNone(dc.integer)

        self.assertIsNone(dc.floating)
        dc.floating = caster(None, _get_field_map(dc)['floating'], dc.__class__)
        self.assertIsNone(dc.floating)

        self.assertIsNone(dc.boolean)
        dc.boolean = caster(None, _get_field_map(dc)['boolean'], dc.__class__)
        self.assertIsNone(dc.boolean)

    def test_from_dict_value(self):
        caster = dictators.BaseDictator.from_dict_value
        string = 'Ðiss is a júníkód stíng viþþ tjænís skvígglí bitts 中國潦草的位'
        integer = 4815162342
        floating = 3.14159265359
        boolean = True

        dc = FauxDataClass()

        self.assertIsNone(dc.string)
        dc.string = caster(string, _get_field_map(dc)['string'], dc)
        self.assertIsNotNone(dc.string)
        self.assertIsInstance(dc.string, str)
        self.assertEqual('Ðiss is a júníkód stíng viþþ tjænís skvígglí bitts 中國潦草的位', dc.string)

        self.assertIsNone(dc.integer)
        dc.integer = caster(integer, _get_field_map(dc)['integer'], dc)
        self.assertIsNotNone(dc.integer)
        self.assertIsInstance(dc.integer, int)
        self.assertEqual(4815162342, dc.integer)

        self.assertIsNone(dc.floating)
        dc.floating = caster(floating, _get_field_map(dc)['floating'], dc)
        self.assertIsNotNone(dc.floating)
        self.assertIsInstance(dc.floating, float)
        self.assertEqual(3.14159265359, dc.floating)

        self.assertIsNone(dc.boolean)
        dc.boolean = caster(boolean, _get_field_map(dc)['boolean'], dc)
        self.assertIsNotNone(dc.boolean)
        self.assertIsInstance(dc.boolean, bool)
        self.assertEqual(True, dc.boolean)


class TimestampDictatorTest(unittest.TestCase):
    def test_none_to_dict_value(self):
        caster = dictators.TimestampDictator.to_dict_value
        dc = FauxDataClass()
        self.assertIsNone(dc.timestamp)
        self.assertIsNone(caster(*_get_test_args(dc, 'timestamp')))

    def test_to_dict_value(self):
        caster = dictators.TimestampDictator.to_dict_value
        dc = FauxDataClass(timestamp=datetime.datetime(2010, 4, 9, 22, 38, 39, 987654))

        self.assertIsNotNone(dc.timestamp)
        self.assertIsInstance(dc.timestamp, datetime.datetime)
        self.assertEqual('2010-04-09T22:38:39.987654Z', caster(*_get_test_args(dc, 'timestamp')))

    def test_none_from_dict_value(self):
        caster = dictators.TimestampDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.timestamp)
        dc.timestamp = caster(None, _get_field_map(dc)['timestamp'], dc.__class__)
        self.assertIsNone(dc.timestamp)

    def test_from_dict_value(self):
        caster = dictators.TimestampDictator.from_dict_value
        timestamp_string = '2012-07-03T14:50:51.654321Z'

        dc = FauxDataClass()

        self.assertIsNone(dc.timestamp)
        dc.timestamp = caster(timestamp_string, _get_field_map(dc)['timestamp'], dc.__class__)
        self.assertIsNotNone(dc.timestamp)
        self.assertIsInstance(dc.timestamp, datetime.datetime)
        self.assertEqual(datetime.datetime(2012, 7, 3, 14, 50, 51, 654321), dc.timestamp)


class ByteDictatorTest(unittest.TestCase):
    def test_none_to_dict_value(self):
        caster = dictators.ByteDictator.to_dict_value
        dc = FauxDataClass()
        self.assertIsNone(dc.real_bytes)
        # self.assertEqual(b'', dc.real_bytes)
        # self.assertIsNone(caster(*_get_test_args(dc, 'real_bytes')))
        self.assertEqual('', caster(*_get_test_args(dc, 'real_bytes')))

    def test_to_dict_value(self):
        caster = dictators.ByteDictator.to_dict_value
        as_str = '♡♠♢♣'
        as_bytes = as_str.encode('utf-8')
        as_base64 = base64.encodebytes(as_bytes).decode('utf-8').strip()

        dc = FauxDataClass(real_bytes=as_bytes)

        self.assertIsNotNone(dc.real_bytes)
        self.assertIsInstance(dc.real_bytes, bytes)
        self.assertEqual(as_base64, caster(*_get_test_args(dc, 'real_bytes')))

    def test_none_from_dict_value(self):
        caster = dictators.ByteDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.real_bytes)
        # self.assertEqual(b'', dc.real_bytes)
        dc.real_bytes = caster(None, _get_field_map(dc)['real_bytes'], dc.__class__)
        # self.assertIsNone(dc.real_bytes)
        self.assertEqual(b'', dc.real_bytes)

    def test_from_dict_value(self):
        caster = dictators.ByteDictator.from_dict_value
        as_str = '♡♠♢♣'
        as_bytes = as_str.encode('utf-8')
        as_base64 = base64.encodebytes(as_bytes).decode('utf-8').strip()

        dc = FauxDataClass()

        self.assertIsNone(dc.real_bytes)
        dc.real_bytes = caster(as_base64, _get_field_map(dc)['real_bytes'], dc.__class__)
        self.assertIsNotNone(dc.real_bytes)
        self.assertIsInstance(dc.real_bytes, bytes)
        self.assertEqual(as_bytes, dc.real_bytes)


class EnumDictatorTest(unittest.TestCase):
    def test_none_to_dict_value(self):
        caster = dictators.EnumDictator.to_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.enumerator)
        # self.assertEqual(0, dc.enumerator)
        # self.assertIsNone(caster(*_get_test_args(dc, 'enumerator')))
        self.assertEqual(0, caster(*_get_test_args(dc, 'enumerator')))

    def test_to_dict_value(self):
        caster = dictators.EnumDictator.to_dict_value
        dc = FauxDataClass(enumerator=FauxEnum.FOO)

        self.assertIsNotNone(dc.enumerator)
        self.assertIsInstance(dc.enumerator, enum.IntEnum)
        self.assertEqual(FauxEnum.FOO.value, caster(*_get_test_args(dc, 'enumerator')))

    def test_none_from_dict_value(self):
        caster = dictators.EnumDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.enumerator)
        # self.assertEqual(0, dc.enumerator)
        dc.enumerator = caster(None, _get_field_map(dc)['enumerator'], dc.__class__)
        # self.assertIsNone(dc.enumerator)
        self.assertEqual(FauxEnum.DEFAULT, dc.enumerator)

    def test_from_dict_value(self):
        caster = dictators.EnumDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.enumerator)
        dc.enumerator = caster(2, _get_field_map(dc)['enumerator'], dc.__class__)
        self.assertIsNotNone(dc.enumerator)
        self.assertIsInstance(dc.enumerator, enum.IntEnum)
        self.assertEqual(FauxEnum.BAR, dc.enumerator)

        dc2 = FauxDataClass()

        self.assertIsNone(dc2.enumerator)
        dc2.enumerator = caster('OOF', _get_field_map(dc2)['enumerator'], dc2.__class__)
        self.assertIsNotNone(dc2.enumerator)
        self.assertIsInstance(dc2.enumerator, enum.IntEnum)
        self.assertEqual(FauxEnum.OOF, dc2.enumerator)


class DurationDictatorTest(unittest.TestCase):
    def test_none_to_dict_value(self):
        caster = dictators.DurationDictator.to_dict_value
        dc = FauxDataClass()
        self.assertIsNone(dc.duration)
        self.assertIsNone(caster(*_get_test_args(dc, 'duration')))

    def test_to_dict_value(self):
        caster = dictators.DurationDictator.to_dict_value
        dc = FauxDataClass(duration=datetime.timedelta(seconds=12.3456789))

        self.assertIsNotNone(dc.duration)
        self.assertIsInstance(dc.duration, datetime.timedelta)
        self.assertEqual('12.345679s', caster(*_get_test_args(dc, 'duration')))

    def test_none_from_dict_value(self):
        caster = dictators.DurationDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.duration)
        dc.duration = caster(None, _get_field_map(dc)['duration'], dc.__class__)
        self.assertIsNone(dc.duration)

    def test_from_dict_value(self):
        caster = dictators.DurationDictator.from_dict_value
        duration_string = '12.345679s'

        dc = FauxDataClass()

        self.assertIsNone(dc.duration)
        dc.duration = caster(duration_string, _get_field_map(dc)['duration'], dc.__class__)
        self.assertIsNotNone(dc.duration)
        self.assertIsInstance(dc.duration, datetime.timedelta)
        self.assertEqual(datetime.timedelta(seconds=12.3456789), dc.duration)

        self.assertEqual(datetime.timedelta(seconds=12.3456789), caster(12.3456789, _get_field_map(dc)['duration'], dc.__class__))
        self.assertEqual(datetime.timedelta(seconds=123456), caster(123456, _get_field_map(dc)['duration'], dc.__class__))
        self.assertEqual(datetime.timedelta(seconds=12.3456789), caster('12.3456789', _get_field_map(dc)['duration'], dc.__class__))


class AnyDictatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Remove old stuff...
        build_package = os.path.join(BUILD_ROOT, 'sandbox')
        if os.path.exists(build_package):
            shutil.rmtree(build_package)
            time.sleep(0.1)

        from neobuilder.neobuilder import NeoBuilder

        # Build stuff...
        builder = NeoBuilder(package='sandbox',
                             protopath=PROTO_ROOT,
                             build_root=BUILD_ROOT)
        builder.build()

        # Add build root to path to access its modules
        sys.path.append(BUILD_ROOT)

    def test_none_to_dict_value(self):
        caster = dictators.AnyDictator.to_dict_value
        dc = FauxDataClass()
        self.assertIsNone(dc.any)
        self.assertIsNone(caster(*_get_test_args(dc, 'any')))

    def test_to_dict_value(self):
        from sandbox.test import rainbow_dc

        caster = dictators.AnyDictator.to_dict_value
        dc = FauxDataClass(any=rainbow_dc.SubMessage('FOO!', 'BAR!!'))

        self.assertIsNotNone(dc.any)
        self.assertIsInstance(dc.any, protoplasm.bases.dataclass_bases.DataclassBase)
        self.assertIsInstance(dc.any, rainbow_dc.SubMessage)

        expected = collections.OrderedDict([
            ('@type', 'type.googleapis.com/sandbox.test.SubMessage'),
            ('foo', 'FOO!'),
            ('bar', 'BAR!!')
        ])

        self.assertEqual(expected, caster(*_get_test_args(dc, 'any')))

    def test_none_from_dict_value(self):
        caster = dictators.AnyDictator.from_dict_value
        dc = FauxDataClass()

        self.assertIsNone(dc.any)
        dc.duration = caster(None, _get_field_map(dc)['any'], dc.__class__)
        self.assertIsNone(dc.any)

    def test_from_dict_value(self):
        from sandbox.test import anytest_dc
        from sandbox.test import rainbow_dc

        caster = dictators.AnyDictator.from_dict_value

        input_value = collections.OrderedDict([
            ('@type', 'type.evetech.net/sandbox.test.SubMessage'),
            ('foo', 'FOO!'),
            ('bar', 'BAR!!')
        ])

        dc = anytest_dc.AnyMessage()

        self.assertIsNone(dc.my_any)

        dc.my_any = caster(input_value, _get_field_map(dc)['my_any'], dc.__class__)

        self.assertIsNotNone(dc.my_any)
        self.assertIsInstance(dc.my_any, protoplasm.bases.dataclass_bases.DataclassBase)
        self.assertIsInstance(dc.my_any, rainbow_dc.SubMessage)
        self.assertEqual(rainbow_dc.SubMessage('FOO!', 'BAR!!'), dc.my_any)
