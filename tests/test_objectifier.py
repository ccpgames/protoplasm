import unittest
import datetime
import base64

from protoplasm.casting import objectifier
import os
import sys

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import shutil
import time
HERE = os.path.dirname(__file__)
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')


class ObjectifierTest(unittest.TestCase):
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

    def test_dict_to_proto(self):
        from sandbox.test import rainbow_pb2

        p1 = rainbow_pb2.SubMessage()
        p1.foo = 'Foo!'
        p1.bar = 'Bar!!!'

        self.assertEqual(p1, objectifier.dict_to_proto(rainbow_pb2.SubMessage, {'foo': 'Foo!', 'bar': 'Bar!!!'}))

        p2 = rainbow_pb2.SubMessage()
        p2.foo = 'Foo Two!'
        self.assertEqual(p2, objectifier.dict_to_proto(rainbow_pb2.SubMessage, {'foo': 'Foo Two!'}))

        p3 = rainbow_pb2.SubMessage()
        p3.foo = '这是中国人'
        self.assertNotEqual(p3, objectifier.dict_to_proto(rainbow_pb2.SubMessage, {'foo': '这不是中国人'}))

        p4 = rainbow_pb2.SubMessage()
        self.assertEqual(p4, objectifier.dict_to_proto(rainbow_pb2.SubMessage))

    def test_nested_dict_to_proto(self):
        from sandbox.test import rainbow_pb2

        p1 = rainbow_pb2.RainbowMessage()
        self.assertEqual(p1, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage))

        p2 = rainbow_pb2.RainbowMessage()
        p2.simple_field = 'Green'
        self.assertEqual(p2, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage, {'simple_field': 'Green'}))
        self.assertNotEqual(p1, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage, {'simple_field': 'Green'}))

        p3 = rainbow_pb2.RainbowMessage()
        p3.simple_field = 'Green'
        p3.message_field.foo = 'Blue'
        self.assertEqual(p3, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green', 'message_field': {'foo': 'Blue'}}))
        p4 = rainbow_pb2.RainbowMessage()
        p4.simple_field = 'Green'
        p4.message_field.foo = 'Blue'
        p4.message_field.bar = 'Yellow'
        self.assertEqual(p4, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green',
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))
        self.assertNotEqual(p3, p4)
        self.assertNotEqual(p4, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'message_field': {'foo': 'Blue', 'bar': 'Red'}}))

        p5 = rainbow_pb2.RainbowMessage()
        p5.simple_field = 'Green'
        p5.message_field.foo = 'Blue'
        p5.message_field.bar = 'Yellow'
        p5.simple_list.append('Four')
        p5.simple_list.append('Seven')
        p5.simple_list.append('99')
        self.assertEqual(p5, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        p6 = rainbow_pb2.RainbowMessage()
        p6.simple_field = 'Green'
        p6.message_field.foo = 'Blue'
        p6.message_field.bar = 'Yellow'
        p6.simple_list.append('Four')
        p6.simple_list.append('Seven')
        p6.simple_list.append('98')
        self.assertNotEqual(p6, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'simple_list': ['Four', 'Seven', '100'],
                                                           'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        p7 = rainbow_pb2.RainbowMessage()
        p7.simple_field = 'Green'
        p7.message_field.foo = 'Blue'
        p7.message_field.bar = 'Yellow'
        p7.simple_list.append('Four')
        p7.simple_list.append('Seven')
        p7.simple_list.append('99')
        m1 = p7.message_list.add()
        m1.foo = 'Foo in a list'
        m1.bar = 'Candybar'
        m2 = p7.message_list.add()
        m2.foo = 'a Fool in a list'
        m2.bar = 'Tequila bar'
        self.assertEqual(p7, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        self.assertNotEqual(p7, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'simple_list': ['Four', 'Seven', '99'], 'message_list': [
                                                              {'foo': 'a Fool in a list', 'bar': 'Tequila bar'}],
                                                           'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        p8 = rainbow_pb2.RainbowMessage()
        p8.simple_field = 'Green'
        p8.message_field.foo = 'Blue'
        p8.message_field.bar = 'Yellow'
        p8.simple_list.append('Four')
        p8.simple_list.append('Seven')
        p8.simple_list.append('99')
        m3 = p8.message_list.add()
        m3.foo = 'Foo in a list'
        m3.bar = 'Candybar'
        m4 = p8.message_list.add()
        m4.foo = 'a Fool in a list'
        m4.bar = 'Tequila bar'
        p8.simple_map['dora'] = 'Imamap!'
        p8.simple_map['diego'] = 'Camera!'
        self.assertEqual(p8, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                        'simple_map': {'dora': 'Imamap!', 'diego': 'Camera!'}}
                                                       ))

        p9 = rainbow_pb2.RainbowMessage()
        p9.simple_field = 'Green'
        p9.message_field.foo = 'Blue'
        p9.message_field.bar = 'Yellow'
        p9.simple_list.append('Four')
        p9.simple_list.append('Seven')
        p9.simple_list.append('99')
        m5 = p9.message_list.add()
        m5.foo = 'Foo in a list'
        m5.bar = 'Candybar'
        m6 = p9.message_list.add()
        m6.foo = 'a Fool in a list'
        m6.bar = 'Tequila bar'
        p9.simple_map['dora'] = 'Imamap!'
        p9.simple_map['diego'] = 'Camera!'
        p9.message_map['donald'].foo = 'duck'
        p9.message_map['donald'].bar = 'trump'
        p9.message_map['mickey'].foo = 'mouse'
        self.assertEqual(p9, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                        'simple_map': {'dora': 'Imamap!', 'diego': 'Camera!'},
                                                        'message_map': {'donald': {'foo': 'duck', 'bar': 'trump'},
                                                                        'mickey': {'foo': 'mouse'}}}
                                                       ))

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

        self.assertEqual(p10, objectifier.dict_to_proto(rainbow_pb2.RainbowMessage,
                                                        {'simple_field': 'Green',
                                                         'simple_list': ['Four', 'Seven', '99'],
                                                         'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                          {'foo': 'a Fool in a list',
                                                                           'bar': 'Tequila bar'}],
                                                         'simple_map': {'diego': 'Camera!', 'dora': 'Imamap!'},
                                                         'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                         'message_map': {'donald': {'foo': 'duck', 'bar': 'trump'},
                                                                         'mickey': {'foo': 'mouse'}}}
                                                        ))

    def test_dict_to_dataclass(self):
        from sandbox.test import rainbow_dc

        dc1 = rainbow_dc.SubMessage()
        dc1.foo = 'Foo!'
        dc1.bar = 'Bar!!!'

        self.assertEqual(dc1, objectifier.dict_to_dataclass(rainbow_dc.SubMessage, {'foo': 'Foo!',
                                                                                    'bar': 'Bar!!!'}))

        dc2 = rainbow_dc.SubMessage()
        dc2.foo = 'Foo Two!'
        self.assertEqual(dc2, objectifier.dict_to_dataclass(rainbow_dc.SubMessage, {'foo': 'Foo Two!'}))

        dc3 = rainbow_dc.SubMessage()
        dc3.foo = '这是中国人'
        self.assertNotEqual(dc3, objectifier.dict_to_dataclass(rainbow_dc.SubMessage, {'foo': '这不是中国人'}))

        dc4 = rainbow_dc.SubMessage()
        self.assertEqual(dc4, objectifier.dict_to_dataclass(rainbow_dc.SubMessage))

    def test_nested_dict_to_dataclass(self):
        from sandbox.test import rainbow_dc

        dc1 = rainbow_dc.RainbowMessage()
        self.assertEqual(dc1, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage))

        dc2 = rainbow_dc.RainbowMessage()
        dc2.simple_field = 'Green'
        self.assertEqual(dc2, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage, {'simple_field': 'Green'}))
        self.assertNotEqual(dc1, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage, {'simple_field': 'Green'}))

        dc3 = rainbow_dc.RainbowMessage()
        dc3.simple_field = 'Green'
        dc3.message_field = rainbow_dc.SubMessage()
        dc3.message_field.foo = 'Blue'
        self.assertEqual(dc3, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green', 'message_field': {'foo': 'Blue'}}))
        dc4 = rainbow_dc.RainbowMessage()
        dc4.simple_field = 'Green'
        dc4.message_field = rainbow_dc.SubMessage()
        dc4.message_field.foo = 'Blue'
        dc4.message_field.bar = 'Yellow'
        self.assertEqual(dc4, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green',
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))
        self.assertNotEqual(dc3, dc4)
        self.assertNotEqual(dc4, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'message_field': {'foo': 'Blue', 'bar': 'Red'}}))

        dc5 = rainbow_dc.RainbowMessage()
        dc5.simple_field = 'Green'
        dc5.message_field = rainbow_dc.SubMessage('Blue', 'Yellow')
        dc5.simple_list.append('Four')
        dc5.simple_list.append('Seven')
        dc5.simple_list.append('99')
        self.assertEqual(dc5, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        dc6 = rainbow_dc.RainbowMessage()
        dc6.simple_field = 'Green'
        dc6.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc6.simple_list.append('Four')
        dc6.simple_list.append('Seven')
        dc6.simple_list.append('98')
        self.assertNotEqual(dc6, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'simple_list': ['Four', 'Seven', '100'],
                                                           'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        dc7 = rainbow_dc.RainbowMessage()
        dc7.simple_field = 'Green'
        dc7.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc7.simple_list.append('Four')
        dc7.simple_list.append('Seven')
        dc7.simple_list.append('99')

        dc7.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc7.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))

        self.assertEqual(dc7, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        self.assertNotEqual(dc7, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                          {'simple_field': 'Green',
                                                           'simple_list': ['Four', 'Seven', '99'], 'message_list': [
                                                              {'foo': 'a Fool in a list', 'bar': 'Tequila bar'}],
                                                           'message_field': {'foo': 'Blue', 'bar': 'Yellow'}}))

        dc8 = rainbow_dc.RainbowMessage()
        dc8.simple_field = 'Green'
        dc8.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc8.simple_list.append('Four')
        dc8.simple_list.append('Seven')
        dc8.simple_list.append('99')

        dc8.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc8.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))

        dc8.simple_map['dora'] = 'Imamap!'
        dc8.simple_map['diego'] = 'Camera!'
        self.assertEqual(dc8, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                        'simple_map': {'dora': 'Imamap!', 'diego': 'Camera!'}}
                                                       ))

        dc9 = rainbow_dc.RainbowMessage()
        dc9.simple_field = 'Green'
        dc9.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc9.simple_list.append('Four')
        dc9.simple_list.append('Seven')
        dc9.simple_list.append('99')
        dc9.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc9.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))
        dc9.simple_map['dora'] = 'Imamap!'
        dc9.simple_map['diego'] = 'Camera!'

        dc9.message_map['donald'] = rainbow_dc.SubMessage(foo='duck', bar='trump')

        dc9.message_map['mickey'] = rainbow_dc.SubMessage(foo='mouse')

        self.assertEqual(dc9, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                       {'simple_field': 'Green', 'simple_list': ['Four', 'Seven', '99'],
                                                        'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                         {'foo': 'a Fool in a list',
                                                                          'bar': 'Tequila bar'}],
                                                        'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                        'simple_map': {'dora': 'Imamap!', 'diego': 'Camera!'},
                                                        'message_map': {'donald': {'foo': 'duck', 'bar': 'trump'},
                                                                        'mickey': {'foo': 'mouse'}}}
                                                       ))

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

        self.assertEqual(dc10, objectifier.dict_to_dataclass(rainbow_dc.RainbowMessage,
                                                        {'simple_field': 'Green',
                                                         'simple_list': ['Four', 'Seven', '99'],
                                                         'message_list': [{'foo': 'Foo in a list', 'bar': 'Candybar'},
                                                                          {'foo': 'a Fool in a list',
                                                                           'bar': 'Tequila bar'}],
                                                         'simple_map': {'diego': 'Camera!', 'dora': 'Imamap!'},
                                                         'message_field': {'foo': 'Blue', 'bar': 'Yellow'},
                                                         'message_map': {'donald': {'foo': 'duck', 'bar': 'trump'},
                                                                         'mickey': {'foo': 'mouse'}}}
                                                        ))

    def test_timestamp_dict_to_proto(self):
        from sandbox.test import rainbow_pb2

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

        dict_data = {'my_timestamp': ts1,
                     'my_timestamp_list': [ts2, ts3],
                     'my_timestamp_map': {'noon': ts4,
                                          'midnight': ts5}}

        p_expect = rainbow_pb2.TimestampMessage()
        p_expect.my_timestamp.FromJsonString(ts1)
        p_expect.my_timestamp_list.add().FromJsonString(ts2)
        p_expect.my_timestamp_list.add().FromJsonString(ts3)
        p_expect.my_timestamp_map['noon'].FromJsonString(ts4)
        p_expect.my_timestamp_map['midnight'].FromJsonString(ts5)

        self.assertEqual(p_expect, objectifier.dict_to_proto(rainbow_pb2.TimestampMessage, dict_data))

    def test_timestamp_dict_to_dataclass(self):
        from sandbox.test import rainbow_dc

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

        dict_data = {'my_timestamp': ts1,
                     'my_timestamp_list': [ts2, ts3],
                     'my_timestamp_map': {'noon': ts4,
                                          'midnight': ts5}}

        dc_expect = rainbow_dc.TimestampMessage()
        dc_expect.my_timestamp = dt1
        dc_expect.my_timestamp_list.append(dt2)
        dc_expect.my_timestamp_list.append(dt3)
        dc_expect.my_timestamp_map['noon'] = dt4
        dc_expect.my_timestamp_map['midnight'] = dt5

        self.assertEqual(dc_expect, objectifier.dict_to_dataclass(rainbow_dc.TimestampMessage, dict_data))

    def test_byte_dict_to_proto(self):
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

        dict_data = {'my_bytes': as_base64_1,
                     'my_bytes_list': [as_base64_2, as_base64_3],
                     'my_bytes_map': {'zero': as_base64_4,
                                      'one': as_base64_5}}

        p_expect = rainbow_pb2.BytesMessage()
        p_expect.my_bytes = as_bytes_1
        p_expect.my_bytes_list.append(as_bytes_2)
        p_expect.my_bytes_list.append(as_bytes_3)
        p_expect.my_bytes_map['zero'] = as_bytes_4
        p_expect.my_bytes_map['one'] = as_bytes_5

        self.assertEqual(p_expect, objectifier.dict_to_proto(rainbow_pb2.BytesMessage, dict_data))

    def test_byte_dict_to_dataclass(self):
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

        dict_data = {'my_bytes': as_base64_1,
                     'my_bytes_list': [as_base64_2, as_base64_3],
                     'my_bytes_map': {'zero': as_base64_4,
                                      'one': as_base64_5}}

        dc_expect = rainbow_dc.BytesMessage()
        dc_expect.my_bytes = as_bytes_1
        dc_expect.my_bytes_list.append(as_bytes_2)
        dc_expect.my_bytes_list.append(as_bytes_3)
        dc_expect.my_bytes_map['zero'] = as_bytes_4
        dc_expect.my_bytes_map['one'] = as_bytes_5

        self.assertEqual(dc_expect, objectifier.dict_to_dataclass(rainbow_dc.BytesMessage, dict_data))

    def test_enum_dict_to_proto(self):
        from sandbox.test import enums_pb2

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

        dict_data = {'my_enum': 2,
                    'my_alias_enum': 3,
                    'my_enum_list': [1, 3],
                    'my_alias_enum_list': [1, 2, 1],
                    'my_enum_map': {'one': 1,
                                    'two': 2},
                    'my_alias_enum_map': {'six': 3,
                                          'sex': 3,
                                          'fimm': 2}}

        self.assertEqual(p_expect, objectifier.dict_to_proto(enums_pb2.WithExternalEnum, dict_data))

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

        dict_data2 = {'my_internal_enum': 6,
                      'my_internal_alias_enum': 7,
                      'my_internal_enum_list': [5, 4],
                      'my_internal_alias_enum_list': [7, 8, 8],
                      'my_internal_enum_map': {'no5': 5,
                                               'no6': 6},
                      'my_internal_alias_enum_map': {'no9': 9,
                                                     'no9B': 9,
                                                     'default': 0}}

        self.assertEqual(p_expect2, objectifier.dict_to_proto(enums_pb2.WithInternalEnum, dict_data2))

    def test_enum_dict_to_dataclass(self):
        from sandbox.test import enums_dc

        p_expect = enums_dc.WithExternalEnum()
        p_expect.my_enum = enums_dc.TWO

        p_expect.my_enum_list.append(enums_dc.ONE)
        p_expect.my_enum_list.append(enums_dc.THREE)

        p_expect.my_enum_map['one'] = enums_dc.ONE
        p_expect.my_enum_map['two'] = enums_dc.TWO

        p_expect.my_alias_enum = enums_dc.SIX

        p_expect.my_alias_enum_list.append(enums_dc.FOUR)
        p_expect.my_alias_enum_list.append(enums_dc.FIVE)
        p_expect.my_alias_enum_list.append(enums_dc.FJORIR)

        p_expect.my_alias_enum_map['six'] = enums_dc.SIX
        p_expect.my_alias_enum_map['sex'] = enums_dc.SEX
        p_expect.my_alias_enum_map['fimm'] = enums_dc.FIVE

        dict_data = {'my_enum': 2,
                    'my_alias_enum': 3,
                    'my_enum_list': [1, 3],
                    'my_alias_enum_list': [1, 2, 1],
                    'my_enum_map': {'one': 1,
                                    'two': 2},
                    'my_alias_enum_map': {'six': 3,
                                          'sex': 3,
                                          'fimm': 2}}

        self.assertEqual(p_expect, objectifier.dict_to_dataclass(enums_dc.WithExternalEnum, dict_data))

        p_expect2 = enums_dc.WithInternalEnum()
        p_expect2.my_internal_enum = enums_dc.WithInternalEnum.SIX

        p_expect2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FIVE)
        p_expect2.my_internal_enum_list.append(enums_dc.WithInternalEnum.FOUR)

        p_expect2.my_internal_enum_map['no5'] = enums_dc.WithInternalEnum.FIVE
        p_expect2.my_internal_enum_map['no6'] = enums_dc.WithInternalEnum.SIX

        p_expect2.my_internal_alias_enum = enums_dc.WithInternalEnum.SEVEN

        p_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.SJO)
        p_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.ATTA)
        p_expect2.my_internal_alias_enum_list.append(enums_dc.WithInternalEnum.EIGHT)

        p_expect2.my_internal_alias_enum_map['no9'] = enums_dc.WithInternalEnum.NIU
        p_expect2.my_internal_alias_enum_map['no9B'] = enums_dc.WithInternalEnum.NINE
        p_expect2.my_internal_alias_enum_map['default'] = enums_dc.WithInternalEnum.ZERO

        dict_data2 = {'my_internal_enum': 6,
                      'my_internal_alias_enum': 7,
                      'my_internal_enum_list': [5, 4],
                      'my_internal_alias_enum_list': [7, 8, 8],
                      'my_internal_enum_map': {'no5': 5,
                                               'no6': 6},
                      'my_internal_alias_enum_map': {'no9': 9,
                                                     'no9B': 9,
                                                     'default': 0}}

        self.assertEqual(p_expect2, objectifier.dict_to_dataclass(enums_dc.WithInternalEnum, dict_data2))
