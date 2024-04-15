import datetime
import unittest
import base64
import os
import sys

from protoplasm import casting
from protoplasm.casting import dictator
from protoplasm.casting import castutils

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import shutil
import time
HERE = os.path.dirname(__file__)
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')



class ProtoToDictTest(unittest.TestCase):
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

    def test_proto_to_dict(self):
        from sandbox.test import rainbow_pb2

        expected = {'simple_field': 'Green',
                    'message_field': {
                        'foo': 'Blue',
                        'bar': 'Yellow'
                    },
                    'simple_list': ['Four', 'Seven', '99'],
                    'message_list': [{'foo': 'Foo in a list',
                                      'bar': 'Candybar'},
                                     {'foo': 'a Fool in a list',
                                      'bar': 'Tequila bar'}],
                    'simple_map': {'dora': 'Imamap!',
                                   'diego': 'Camera!'},
                    'message_map': {'mickey': {'foo': 'mouse'},
                                    'donald': {'foo': 'duck',
                                               'bar': 'trump'}}}

        p11 = casting.mkproto(rainbow_pb2.RainbowMessage,
                                         simple_map__diego='Camera!',
                                         simple_field='Green',
                                         message_field__foo='Blue',
                                         message_field__bar='Yellow',
                                         simple_list=['Four', 'Seven', '99'],
                                         message_list=[castutils.kwdict(foo='Foo in a list',
                                                               bar='Candybar'),
                                              castutils.kwdict(foo='a Fool in a list',
                                                               bar='Tequila bar')],
                                         simple_map__dora='Imamap!',
                                         message_map__donald__foo='duck',
                                         message_map__donald__bar='trump',
                                         message_map__mickey__foo='mouse')

        self.assertEqual(expected, dictator.proto_to_dict(p11))

    def test_proto_timestamp_to_dict(self):
        from sandbox.test import rainbow_pb2

        ts1 = '2012-07-03T14:50:51.654321Z'
        dt1 = datetime.datetime(2012, 7, 3, 14, 50, 51, 654321)
        self.assertEqual(ts1, dt1.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts2 = '2010-04-09T22:38:39.009870Z'
        dt2 = datetime.datetime(2010, 4, 9, 22, 38, 39, 9870)
        self.assertEqual(ts2, dt2.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts3 = '1979-07-06T14:30:00Z'
        dt3 = datetime.datetime(1979, 7, 6, 14, 30)
        self.assertEqual(ts3, dt3.strftime('%Y-%m-%dT%H:%M:%SZ'))

        ts4 = '2049-01-01T12:00:00Z'
        dt4 = datetime.datetime(2049, 1, 1, 12)
        self.assertEqual(ts4, dt4.strftime('%Y-%m-%dT%H:%M:%SZ'))

        ts5 = '2049-01-01T00:00:00Z'
        dt5 = datetime.datetime(2049, 1, 1)
        self.assertEqual(ts5, dt5.strftime('%Y-%m-%dT%H:%M:%SZ'))

        expected = {'my_timestamp': ts1,
                    'my_timestamp_list': [ts2, ts3],
                    'my_timestamp_map': {
                        'noon': ts4,
                        'midnight': ts5}}

        p12 = casting.mkproto(rainbow_pb2.TimestampMessage,
                                         my_timestamp=ts1,
                                         my_timestamp_list=[ts2, ts3],
                                         my_timestamp_map__noon=ts4,
                                         my_timestamp_map__midnight=ts5)

        self.assertEqual(expected, dictator.proto_to_dict(p12))

    def test_proto_bytes_to_dict(self):
        from sandbox.test import rainbow_pb2

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

        expected = {'my_bytes': as_base64_1,
                    'my_bytes_list': [as_base64_2, as_base64_3],
                    'my_bytes_map': {
                        'zero': as_base64_4,
                        'one': as_base64_5}}

        p13 = casting.mkproto(rainbow_pb2.BytesMessage,
                                         my_bytes=as_base64_1,
                                         my_bytes_list=[as_base64_2, as_base64_3],
                                         my_bytes_map__zero=as_base64_4,
                                         my_bytes_map__one=as_base64_5)

        self.assertEqual(expected, dictator.proto_to_dict(p13))

    def test_proto_enums_to_dict(self):
        from sandbox.test import enums_pb2

        p1 = enums_pb2.WithExternalEnum()
        p1.my_enum = enums_pb2.TWO

        p1.my_enum_list.append(enums_pb2.ONE)
        p1.my_enum_list.append(enums_pb2.THREE)

        p1.my_enum_map['one'] = enums_pb2.ONE
        p1.my_enum_map['two'] = enums_pb2.TWO

        p1.my_alias_enum = enums_pb2.SIX

        p1.my_alias_enum_list.append(enums_pb2.FOUR)
        p1.my_alias_enum_list.append(enums_pb2.FIVE)
        p1.my_alias_enum_list.append(enums_pb2.FJORIR)

        p1.my_alias_enum_map['six'] = enums_pb2.SIX
        p1.my_alias_enum_map['sex'] = enums_pb2.SEX
        p1.my_alias_enum_map['fimm'] = enums_pb2.FIVE

        expected = {'my_enum': 2,
                    'my_alias_enum': 3,
                    'my_enum_list': [1, 3],
                    'my_alias_enum_list': [1, 2, 1],
                    'my_enum_map': {'one': 1,
                                    'two': 2},
                    'my_alias_enum_map': {'six': 3,
                                          'sex': 3,
                                          'fimm': 2}}

        self.assertEqual(expected, dictator.proto_to_dict(p1))

        p2 = enums_pb2.WithInternalEnum()
        p2.my_internal_enum = enums_pb2.WithInternalEnum.SIX

        p2.my_internal_enum_list.append(enums_pb2.WithInternalEnum.FIVE)
        p2.my_internal_enum_list.append(enums_pb2.WithInternalEnum.FOUR)

        p2.my_internal_enum_map['no5'] = enums_pb2.WithInternalEnum.FIVE
        p2.my_internal_enum_map['no6'] = enums_pb2.WithInternalEnum.SIX

        p2.my_internal_alias_enum = enums_pb2.WithInternalEnum.SEVEN

        p2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.SJO)
        p2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.ATTA)
        p2.my_internal_alias_enum_list.append(enums_pb2.WithInternalEnum.EIGHT)

        p2.my_internal_alias_enum_map['no9'] = enums_pb2.WithInternalEnum.NIU
        p2.my_internal_alias_enum_map['no9B'] = enums_pb2.WithInternalEnum.NINE
        p2.my_internal_alias_enum_map['default'] = enums_pb2.WithInternalEnum.ZERO

        expected2 = {'my_internal_enum': 6,
                     'my_internal_alias_enum': 7,
                     'my_internal_enum_list': [5, 4],
                     'my_internal_alias_enum_list': [7, 8, 8],
                     'my_internal_enum_map': {'no5': 5,
                                              'no6': 6},
                     'my_internal_alias_enum_map': {'no9': 9,
                                                    'no9B': 9,
                                                    'default': 0}}

        self.assertEqual(expected2, dictator.proto_to_dict(p2))


class DataclassToDictTest(unittest.TestCase):
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

    def test_dataclass_to_dict(self):
        from sandbox.test import rainbow_dc

        expected = {'simple_field': 'Green',
                    'message_field': {
                        'foo': 'Blue',
                        'bar': 'Yellow'
                    },
                    'simple_list': ['Four', 'Seven', '99'],
                    'message_list': [{'foo': 'Foo in a list',
                                      'bar': 'Candybar'},
                                     {'foo': 'a Fool in a list',
                                      'bar': 'Tequila bar'}],
                    'simple_map': {'dora': 'Imamap!',
                                   'diego': 'Camera!'},
                    'message_map': {'mickey': {'foo': 'mouse',
                                               'bar': ''},  # TODO(thordurm@ccpgames.com>) 2024-04-15: Should we include "default/empty" values?!?
                                    'donald': {'foo': 'duck',
                                               'bar': 'trump'}}}

        dc = rainbow_dc.RainbowMessage(simple_field='Green',
                                       message_field=rainbow_dc.SubMessage(foo='Blue',
                                                                           bar='Yellow'),
                                       simple_list=['Four', 'Seven', '99'],
                                       message_list=[rainbow_dc.SubMessage(foo='Foo in a list',
                                                                           bar='Candybar'),
                                                     rainbow_dc.SubMessage(foo='a Fool in a list',
                                                                           bar='Tequila bar')],
                                       simple_map={'dora': 'Imamap!',
                                                   'diego': 'Camera!'},
                                       message_map={'donald': rainbow_dc.SubMessage(foo='duck',
                                                                                    bar='trump'),
                                                    'mickey': rainbow_dc.SubMessage(foo='mouse')})

        self.assertEqual(expected, dictator.dataclass_to_dict(dc))

        dc2 = rainbow_dc.RainbowMessage(simple_field='Green',
                                        message_field=rainbow_dc.SubMessage(foo='Blue',
                                                                            bar='Yellow'),
                                        simple_list=['Four', 'Seven', '99'],
                                        message_list=[rainbow_dc.SubMessage(foo='Foo in a list',
                                                                            bar='Candybar'),
                                                      rainbow_dc.SubMessage(foo='a Fool in a list',
                                                                            bar='Tequila bar')],
                                        simple_map={'dora': 'Imamap!',
                                                    'diego': 'Camera!'},
                                        message_map={'donald': rainbow_dc.SubMessage(foo='duck',
                                                                                     bar='trump'),
                                                     'mickey': rainbow_dc.SubMessage(foo='rat')})

        self.assertNotEqual(expected, dictator.dataclass_to_dict(dc2))

    def test_dataclass_timestamp_to_dict(self):
        from sandbox.test import rainbow_dc

        ts1 = '2012-07-03T14:50:51.654321Z'
        dt1 = datetime.datetime(2012, 7, 3, 14, 50, 51, 654321)
        self.assertEqual(ts1, dt1.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts2 = '2010-04-09T22:38:39.009870Z'
        dt2 = datetime.datetime(2010, 4, 9, 22, 38, 39, 9870)
        self.assertEqual(ts2, dt2.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ts3 = '1979-07-06T14:30:00Z'
        dt3 = datetime.datetime(1979, 7, 6, 14, 30)
        self.assertEqual(ts3, dt3.strftime('%Y-%m-%dT%H:%M:%SZ'))

        ts4 = '2049-01-01T12:00:00Z'
        dt4 = datetime.datetime(2049, 1, 1, 12)
        self.assertEqual(ts4, dt4.strftime('%Y-%m-%dT%H:%M:%SZ'))

        ts5 = '2049-01-01T00:00:00Z'
        dt5 = datetime.datetime(2049, 1, 1)
        self.assertEqual(ts5, dt5.strftime('%Y-%m-%dT%H:%M:%SZ'))

        expected = {'my_timestamp': ts1,
                    'my_timestamp_list': [ts2, ts3],
                    'my_timestamp_map': {
                        'noon': ts4,
                        'midnight': ts5}}

        dc = rainbow_dc.TimestampMessage(my_timestamp=dt1,
                                         my_timestamp_list=[dt2, dt3],
                                         my_timestamp_map={'noon': dt4,
                                                           'midnight': dt5})

        self.assertEqual(expected, dictator.dataclass_to_dict(dc))

    def test_dataclass_bytes_to_dict(self):
        from sandbox.test import rainbow_dc

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

        expected = {'my_bytes': as_base64_1,
                    'my_bytes_list': [as_base64_2, as_base64_3],
                    'my_bytes_map': {
                        'zero': as_base64_4,
                        'one': as_base64_5}}

        dc = rainbow_dc.BytesMessage(my_bytes=as_bytes_1,
                                     my_bytes_list=[as_bytes_2, as_bytes_3],
                                     my_bytes_map={'zero': as_bytes_4,
                                                   'one': as_bytes_5})

        self.assertEqual(expected, dictator.dataclass_to_dict(dc))

    def test_dataclass_enums_to_dict(self):
        from sandbox.test import enums_dc
        dc1 = enums_dc.WithExternalEnum()
        dc1.my_enum = enums_dc.TWO

        dc1.my_enum_list.append(enums_dc.ONE)
        dc1.my_enum_list.append(enums_dc.THREE)

        dc1.my_enum_map['one'] = enums_dc.ONE
        dc1.my_enum_map['two'] = enums_dc.TWO

        dc1.my_alias_enum = enums_dc.SIX

        dc1.my_alias_enum_list.append(enums_dc.FOUR)
        dc1.my_alias_enum_list.append(enums_dc.FIVE)
        dc1.my_alias_enum_list.append(enums_dc.FJORIR)

        dc1.my_alias_enum_map['six'] = enums_dc.SIX
        dc1.my_alias_enum_map['sex'] = enums_dc.SEX
        dc1.my_alias_enum_map['fimm'] = enums_dc.FIVE

        expected = {'my_enum': 2,
                    'my_alias_enum': 3,
                    'my_enum_list': [1, 3],
                    'my_alias_enum_list': [1, 2, 1],
                    'my_enum_map': {'one': 1,
                                    'two': 2},
                    'my_alias_enum_map': {'six': 3,
                                          'sex': 3,
                                          'fimm': 2}}

        self.assertEqual(expected, dictator.dataclass_to_dict(dc1))

        dc2 = enums_dc.WithInternalEnum()
        dc2.my_internal_enum = enums_dc.WithInternalEnum.SIX

        dc2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FIVE)
        dc2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FOUR)

        dc2.my_internal_enum_map['no5'] = enums_dc.WithInternalEnum.FIVE
        dc2.my_internal_enum_map['no6'] = enums_dc.WithInternalEnum.SIX

        dc2.my_internal_alias_enum = enums_dc.WithInternalEnum.SEVEN

        dc2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.SJO)
        dc2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.ATTA)
        dc2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.EIGHT)

        dc2.my_internal_alias_enum_map['no9'] = enums_dc.WithInternalEnum.NIU
        dc2.my_internal_alias_enum_map['no9B'] = enums_dc.WithInternalEnum.NINE
        dc2.my_internal_alias_enum_map['default'] = enums_dc.WithInternalEnum.ZERO

        expected2 = {'my_internal_enum': 6,
                     'my_internal_alias_enum': 7,
                     'my_internal_enum_list': [5, 4],
                     'my_internal_alias_enum_list': [7, 8, 8],
                     'my_internal_enum_map': {'no5': 5,
                                              'no6': 6},
                     'my_internal_alias_enum_map': {'no9': 9,
                                                    'no9B': 9,
                                                    'default': 0}}

        self.assertEqual(expected2, dictator.dataclass_to_dict(dc2))
