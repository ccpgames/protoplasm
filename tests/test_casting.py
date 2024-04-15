import base64
import datetime
import unittest
import os
import sys

from protoplasm import casting

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import shutil
import time
HERE = os.path.dirname(__file__)
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')


class CastingTest(unittest.TestCase):
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

    def test_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc

        p1 = rainbow_pb2.SubMessage()
        p1.foo = 'Foo!'
        p1.bar = 'Bar!!!'

        dc1 = rainbow_dc.SubMessage()
        dc1.foo = 'Foo!'
        dc1.bar = 'Bar!!!'

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))

        p2 = rainbow_pb2.SubMessage()
        p2.foo = 'Foo Two!'

        dc2 = rainbow_dc.SubMessage()
        dc2.foo = 'Foo Two!'

        self.assertEqual(p2, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2))

        p3 = rainbow_pb2.SubMessage()
        p3.foo = '这是中国人'

        dc3 = rainbow_dc.SubMessage()
        dc3.foo = '这是中国人'

        self.assertEqual(p3, casting.dataclass_to_proto(dc3))
        self.assertEqual(dc3, casting.proto_to_dataclass(p3))

        p4 = rainbow_pb2.SubMessage()
        dc4 = rainbow_dc.SubMessage()

        self.assertEqual(p4, casting.dataclass_to_proto(dc4))
        self.assertEqual(dc4, casting.proto_to_dataclass(p4))

        self.assertNotEqual(dc1, casting.proto_to_dataclass(p2))

        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

    def test_nested_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc

        p1 = rainbow_pb2.RainbowMessage()
        dc1 = rainbow_dc.RainbowMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        p4 = rainbow_pb2.RainbowMessage()
        p4.simple_field = 'Green'
        p4.message_field.foo = 'Blue'
        p4.message_field.bar = 'Yellow'
        
        dc4 = rainbow_dc.RainbowMessage()
        dc4.simple_field = 'Green'
        dc4.message_field = rainbow_dc.SubMessage()
        dc4.message_field.foo = 'Blue'
        dc4.message_field.bar = 'Yellow'

        self.assertEqual(p4, casting.dataclass_to_proto(dc4))
        self.assertEqual(dc4, casting.proto_to_dataclass(p4))
        self.assertEqual(dc4, casting.proto_to_dataclass(casting.dataclass_to_proto(dc4)))
        self.assertEqual(p4, casting.dataclass_to_proto(casting.proto_to_dataclass(p4)))
        
        p10 = rainbow_pb2.RainbowMessage()
        p10.simple_field = 'Green'
        p10.message_field.foo = 'Blue'
        p10.message_field.bar = 'Yellow'
        p10.simple_list.append('Four')
        p10.simple_list.append('Seven')
        p10.simple_list.append('99')
        m7 = p10.message_list.add()
        m7.foo = 'Foo in a list'
        m7.bar = 'Candybar'
        m8 = p10.message_list.add()
        m8.foo = 'a Fool in a list'
        m8.bar = 'Tequila bar'
        p10.simple_map['dora'] = 'Imamap!'
        p10.simple_map['diego'] = 'Camera!'
        p10.message_map['mickey'].foo = 'mouse'
        p10.message_map['donald'].foo = 'duck'
        p10.message_map['donald'].bar = 'trump'

        dc10 = rainbow_dc.RainbowMessage()
        dc10.simple_field = 'Green'
        dc10.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc10.simple_list.append('Four')
        dc10.simple_list.append('Seven')
        dc10.simple_list.append('99')
        dc10.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc10.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))
        dc10.simple_map['dora'] = 'Imamap!'
        dc10.simple_map['diego'] = 'Camera!'
        dc10.message_map['mickey'] = rainbow_dc.SubMessage(foo='mouse')
        dc10.message_map['donald'] = rainbow_dc.SubMessage(foo='duck', bar='trump')

        self.assertEqual(p10, casting.dataclass_to_proto(dc10))
        self.assertEqual(dc10, casting.proto_to_dataclass(p10))
        self.assertEqual(dc10, casting.proto_to_dataclass(casting.dataclass_to_proto(dc10)))
        self.assertEqual(p10, casting.dataclass_to_proto(casting.proto_to_dataclass(p10)))

    def test_timestamp_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc

        p1 = rainbow_pb2.TimestampMessage()
        dc1 = rainbow_dc.TimestampMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        ts1 = '2012-07-03T14:50:51.654321Z'
        dt1 = datetime.datetime(2012, 7, 3, 14, 50, 51, 654321)
        self.assertEqual(ts1, dt1.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts2 = '2010-04-09T22:38:39.009870Z'
        dt2 = datetime.datetime(2010, 4, 9, 22, 38, 39, 9870)
        self.assertEqual(ts2, dt2.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts3 = '1979-07-06T14:30:00.000000Z'
        dt3 = datetime.datetime(1979, 7, 6, 14, 30)
        self.assertEqual(ts3, dt3.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts4 = '2049-01-01T12:00:00.000000Z'
        dt4 = datetime.datetime(2049, 1, 1, 12)
        self.assertEqual(ts4, dt4.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts5 = '2049-01-01T00:00:00.000000Z'
        dt5 = datetime.datetime(2049, 1, 1)
        self.assertEqual(ts5, dt5.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        p_expect = rainbow_pb2.TimestampMessage()
        p_expect.my_timestamp.FromJsonString(ts1)
        p_expect.my_timestamp_list.add().FromJsonString(ts2)
        p_expect.my_timestamp_list.add().FromJsonString(ts3)
        p_expect.my_timestamp_map['noon'].FromJsonString(ts4)
        p_expect.my_timestamp_map['midnight'].FromJsonString(ts5)

        dc_expect = rainbow_dc.TimestampMessage()
        dc_expect.my_timestamp = dt1
        dc_expect.my_timestamp_list.append(dt2)
        dc_expect.my_timestamp_list.append(dt3)
        dc_expect.my_timestamp_map['noon'] = dt4
        dc_expect.my_timestamp_map['midnight'] = dt5

        self.assertEqual(p_expect, casting.dataclass_to_proto(dc_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(p_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(casting.dataclass_to_proto(dc_expect)))
        self.assertEqual(p_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p_expect)))

    def test_byte_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc

        p1 = rainbow_pb2.BytesMessage()
        dc1 = rainbow_dc.BytesMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        as_str_1 = 'Þórður Matthíasson'
        as_bytes_1 = as_str_1.encode('utf-8')
        as_base64_1 = base64.encodebytes(as_bytes_1).decode('utf-8').strip()

        as_str_2 = '♡'
        as_bytes_2 = as_str_2.encode('utf-8')
        as_base64_2 = base64.encodebytes(as_bytes_2).decode('utf-8').strip()

        as_str_3 = '♠'
        as_bytes_3 = as_str_3.encode('utf-8')
        as_base64_3 = base64.encodebytes(as_bytes_3).decode('utf-8').strip()

        as_str_4 = '♢'
        as_bytes_4 = as_str_4.encode('utf-8')
        as_base64_4 = base64.encodebytes(as_bytes_4).decode('utf-8').strip()

        as_str_5 = '♣'
        as_bytes_5 = as_str_5.encode('utf-8')
        as_base64_5 = base64.encodebytes(as_bytes_5).decode('utf-8').strip()

        p_expect = rainbow_pb2.BytesMessage()
        p_expect.my_bytes = as_bytes_1
        p_expect.my_bytes_list.append(as_bytes_2)
        p_expect.my_bytes_list.append(as_bytes_3)
        p_expect.my_bytes_map['zero'] = as_bytes_4
        p_expect.my_bytes_map['one'] = as_bytes_5

        dc_expect = rainbow_dc.BytesMessage()
        dc_expect.my_bytes = as_bytes_1
        dc_expect.my_bytes_list.append(as_bytes_2)
        dc_expect.my_bytes_list.append(as_bytes_3)
        dc_expect.my_bytes_map['zero'] = as_bytes_4
        dc_expect.my_bytes_map['one'] = as_bytes_5

        self.assertEqual(p_expect, casting.dataclass_to_proto(dc_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(p_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(casting.dataclass_to_proto(dc_expect)))
        self.assertEqual(p_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p_expect)))

    def test_enum_proto_to_dataclass_and_back(self):
        from sandbox.test import enums_pb2
        from sandbox.test import enums_dc

        p1 = enums_pb2.WithExternalEnum()
        dc1 = enums_dc.WithExternalEnum()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        p_expect = enums_pb2.WithExternalEnum()
        p_expect.my_enum = enums_pb2.TWO

        p_expect.my_enum_list.append(enums_pb2.ONE)
        p_expect.my_enum_list.append(enums_pb2.THREE)

        p_expect.my_enum_map['one'] = enums_pb2.ONE
        p_expect.my_enum_map['two'] = enums_pb2.TWO

        p_expect.my_alias_enum = enums_pb2.SIX

        p_expect.my_alias_enum_list.append(enums_pb2.FOUR)
        p_expect.my_alias_enum_list.append(enums_pb2.FIVE)
        p_expect.my_alias_enum_list.append(enums_pb2.FJORIR)

        p_expect.my_alias_enum_map['six'] = enums_pb2.SIX
        p_expect.my_alias_enum_map['sex'] = enums_pb2.SEX
        p_expect.my_alias_enum_map['fimm'] = enums_pb2.FIVE

        dc_expect = enums_dc.WithExternalEnum()
        dc_expect.my_enum = enums_dc.TWO

        dc_expect.my_enum_list.append(enums_dc.ONE)
        dc_expect.my_enum_list.append(enums_dc.THREE)

        dc_expect.my_enum_map['one'] = enums_dc.ONE
        dc_expect.my_enum_map['two'] = enums_dc.TWO

        dc_expect.my_alias_enum = enums_dc.SIX

        dc_expect.my_alias_enum_list.append(enums_dc.FOUR)
        dc_expect.my_alias_enum_list.append(enums_dc.FIVE)
        dc_expect.my_alias_enum_list.append(enums_dc.FJORIR)

        dc_expect.my_alias_enum_map['six'] = enums_dc.SIX
        dc_expect.my_alias_enum_map['sex'] = enums_dc.SEX
        dc_expect.my_alias_enum_map['fimm'] = enums_dc.FIVE

        self.assertEqual(p_expect, casting.dataclass_to_proto(dc_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(p_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(casting.dataclass_to_proto(dc_expect)))
        self.assertEqual(p_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p_expect)))

        p_expect2 = enums_pb2.WithInternalEnum()
        p_expect2.my_internal_enum = enums_pb2.WithInternalEnum.SIX

        p_expect2.my_internal_enum_list.append(enums_pb2.WithInternalEnum.FIVE)
        p_expect2.my_internal_enum_list.append(enums_pb2.WithInternalEnum.FOUR)

        p_expect2.my_internal_enum_map['no5'] = enums_pb2.WithInternalEnum.FIVE
        p_expect2.my_internal_enum_map['no6'] = enums_pb2.WithInternalEnum.SIX

        p_expect2.my_internal_alias_enum = enums_pb2.WithInternalEnum.SEVEN

        p_expect2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.SJO)
        p_expect2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.ATTA)
        p_expect2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.EIGHT)

        p_expect2.my_internal_alias_enum_map['no9'] = enums_pb2.WithInternalEnum.NIU
        p_expect2.my_internal_alias_enum_map['no9B'] = enums_pb2.WithInternalEnum.NINE
        p_expect2.my_internal_alias_enum_map['default'] = enums_pb2.WithInternalEnum.ZERO

        dc_expect2 = enums_dc.WithInternalEnum()
        dc_expect2.my_internal_enum = enums_dc.WithInternalEnum.SIX

        dc_expect2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FIVE)
        dc_expect2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FOUR)

        dc_expect2.my_internal_enum_map['no5'] = enums_dc.WithInternalEnum.FIVE
        dc_expect2.my_internal_enum_map['no6'] = enums_dc.WithInternalEnum.SIX

        dc_expect2.my_internal_alias_enum = enums_dc.WithInternalEnum.SEVEN

        dc_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.SJO)
        dc_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.ATTA)
        dc_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.EIGHT)

        dc_expect2.my_internal_alias_enum_map['no9'] = enums_dc.WithInternalEnum.NIU
        dc_expect2.my_internal_alias_enum_map['no9B'] = enums_dc.WithInternalEnum.NINE
        dc_expect2.my_internal_alias_enum_map['default'] = enums_dc.WithInternalEnum.ZERO

        self.assertEqual(p_expect2, casting.dataclass_to_proto(dc_expect2))
        self.assertEqual(dc_expect2, casting.proto_to_dataclass(p_expect2))
        self.assertEqual(dc_expect2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc_expect2)))
        self.assertEqual(p_expect2, casting.dataclass_to_proto(casting.proto_to_dataclass(p_expect2)))

    def test_duration_proto_to_dataclass_and_back(self):
        from sandbox.test import timeduration_pb2
        from sandbox.test import timeduration_dc

        p1 = timeduration_pb2.DurationMessage()
        dc1 = timeduration_dc.DurationMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        p_expect = timeduration_pb2.DurationMessage()
        p_expect.my_duration.seconds = 987
        p_expect.my_duration.nanos = 654321000

        dl_1 = p_expect.my_duration_list.add()
        dl_1.seconds = 0
        dl_1.nanos = 42000

        dl_2 = p_expect.my_duration_list.add()
        dl_2.seconds = 100001

        p_expect.my_duration_map['short'].nanos = 7000
        p_expect.my_duration_map['long'].seconds = 60*60*24*4  # 4 days

        dc_expect = timeduration_dc.DurationMessage(datetime.timedelta(seconds=987.654321),
                                                    [
                                                        datetime.timedelta(seconds=0.000042),
                                                        datetime.timedelta(seconds=100001)
                                                    ],
                                                    {
                                                        'short': datetime.timedelta(microseconds=7),
                                                        'long': datetime.timedelta(days=4)
                                                    })

        self.assertEqual(p_expect, casting.dataclass_to_proto(dc_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(p_expect))
        self.assertEqual(dc_expect, casting.proto_to_dataclass(casting.dataclass_to_proto(dc_expect)))
        self.assertEqual(p_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p_expect)))

    def test_any_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc
        from sandbox.test import anytest_pb2
        from sandbox.test import anytest_dc

        p1 = anytest_pb2.AnyMessage()
        dc1 = anytest_dc.AnyMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        p2_sub = rainbow_pb2.SubMessage()
        p2_sub.foo = 'OOF'
        p2_sub.bar = 'RAB'

        p2_expect = anytest_pb2.AnyMessage()
        p2_expect.my_any.Pack(p2_sub)

        dc2_sub = rainbow_dc.SubMessage('OOF', 'RAB')
        dc2 = anytest_dc.AnyMessage()
        dc2.my_any = dc2_sub

        self.assertEqual(p2_sub, casting.dataclass_to_proto(dc2_sub))
        self.assertEqual(dc2_sub, casting.proto_to_dataclass(p2_sub))
        self.assertEqual(dc2_sub, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2_sub)))
        self.assertEqual(p2_sub, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_sub)))

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

        i1 = p2_expect.my_any_list.add()
        i1.Pack(casting.mkproto(rainbow_pb2.SubMessage, foo='too', bar='beer'))
        i2 = p2_expect.my_any_list.add()
        i2.Pack(casting.mkproto(rainbow_pb2.SubMessage, foo='three', bar='tequila'))

        self.assertNotEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertNotEqual(dc2, casting.proto_to_dataclass(p2_expect))

        dc2.my_any_list = [rainbow_dc.SubMessage(foo='too', bar='beer'), rainbow_dc.SubMessage(foo='three', bar='tequila')]

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

        p2_expect.my_any_map['mars'].Pack(casting.mkproto(rainbow_pb2.SubMessage, foo='xy'))
        p2_expect.my_any_map['venus'].Pack(casting.mkproto(rainbow_pb2.SubMessage, foo='xx'))

        self.assertNotEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertNotEqual(dc2, casting.proto_to_dataclass(p2_expect))

        dc2.my_any_map['mars'] = rainbow_dc.SubMessage('xy')
        dc2.my_any_map['venus'] = rainbow_dc.SubMessage('xx')

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

    def test_any_nested_proto_to_dataclass_and_back(self):
        from sandbox.test import rainbow_pb2
        from sandbox.test import rainbow_dc
        from sandbox.test import anytest_pb2
        from sandbox.test import anytest_dc

        p1 = anytest_pb2.AnyMessage()
        dc1 = anytest_dc.AnyMessage()

        self.assertEqual(p1, casting.dataclass_to_proto(dc1))
        self.assertEqual(dc1, casting.proto_to_dataclass(p1))
        self.assertEqual(dc1, casting.proto_to_dataclass(casting.dataclass_to_proto(dc1)))
        self.assertEqual(p1, casting.dataclass_to_proto(casting.proto_to_dataclass(p1)))

        p10 = rainbow_pb2.RainbowMessage()
        p10.simple_field = 'Green'
        p10.message_field.foo = 'Blue'
        p10.message_field.bar = 'Yellow'
        p10.simple_list.append('Four')
        p10.simple_list.append('Seven')
        p10.simple_list.append('99')
        m7 = p10.message_list.add()
        m7.foo = 'Foo in a list'
        m7.bar = 'Candybar'
        m8 = p10.message_list.add()
        m8.foo = 'a Fool in a list'
        m8.bar = 'Tequila bar'
        p10.simple_map['dora'] = 'Imamap!'
        p10.simple_map['diego'] = 'Camera!'
        p10.message_map['mickey'].foo = 'mouse'
        p10.message_map['donald'].foo = 'duck'
        p10.message_map['donald'].bar = 'trump'

        dc10 = rainbow_dc.RainbowMessage()
        dc10.simple_field = 'Green'
        dc10.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc10.simple_list.append('Four')
        dc10.simple_list.append('Seven')
        dc10.simple_list.append('99')
        dc10.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc10.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))
        dc10.simple_map['dora'] = 'Imamap!'
        dc10.simple_map['diego'] = 'Camera!'
        dc10.message_map['mickey'] = rainbow_dc.SubMessage(foo='mouse')
        dc10.message_map['donald'] = rainbow_dc.SubMessage(foo='duck', bar='trump')

        self.assertEqual(p10, casting.dataclass_to_proto(dc10))
        self.assertEqual(dc10, casting.proto_to_dataclass(p10))
        self.assertEqual(dc10, casting.proto_to_dataclass(casting.dataclass_to_proto(dc10)))
        self.assertEqual(p10, casting.dataclass_to_proto(casting.proto_to_dataclass(p10)))

        p2_expect = anytest_pb2.AnyMessage()
        p2_expect.my_any.Pack(p10)

        dc2 = anytest_dc.AnyMessage()
        dc2.my_any = dc10

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

        i1 = p2_expect.my_any_list.add()
        i1.Pack(p10)
        i2 = p2_expect.my_any_list.add()
        i2.Pack(p10)

        self.assertNotEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertNotEqual(dc2, casting.proto_to_dataclass(p2_expect))

        dc2.my_any_list = [dc10, dc10]

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

        p2_expect.my_any_map['mars'].Pack(p10)
        p2_expect.my_any_map['venus'].Pack(p10)

        self.assertNotEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertNotEqual(dc2, casting.proto_to_dataclass(p2_expect))

        dc2.my_any_map['mars'] = dc10
        dc2.my_any_map['venus'] = dc10

        self.assertEqual(p2_expect, casting.dataclass_to_proto(dc2))
        self.assertEqual(dc2, casting.proto_to_dataclass(p2_expect))
        self.assertEqual(dc2, casting.proto_to_dataclass(casting.dataclass_to_proto(dc2)))
        self.assertEqual(p2_expect, casting.dataclass_to_proto(casting.proto_to_dataclass(p2_expect)))

    def test_cloning(self):
        from sandbox.test import clones_dc

        thing_1 = clones_dc.ThingOne(
            my_string='this is a string',
            my_number=42,
            my_float=4.2,
            my_timestamp=datetime.datetime(2019, 3, 28, 10, 13, 8, 123456),
            my_subthing=clones_dc.SubThing(foo='F', bar='B'),
            my_unique_string='I REFUSE TO BE CLONED!!!'
        )

        thing_2 = clones_dc.ThingTwo.from_clone(thing_1)

        self.assertEqual(thing_1.my_string, thing_2.my_string)
        self.assertEqual(thing_1.my_number, thing_2.my_number)
        self.assertEqual(thing_1.my_float, thing_2.my_float)
        self.assertEqual(thing_1.my_timestamp, thing_2.my_timestamp)
        self.assertEqual(thing_1.my_subthing, thing_2.my_subthing)

        self.assertNotEqual(thing_1.my_unique_string, thing_2.my_special_string)
