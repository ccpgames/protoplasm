import unittest
import datetime
import base64
import protoplasm.casting
from protoplasm.casting import castutils
import os
import sys
import shutil
import time

from sandbox.test import rainbow_pb2
from sandbox.test import rainbow_dc
from sandbox.test import enums_pb2
from sandbox.test import enums_dc

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

HERE = os.path.dirname(__file__)

PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')


class CastutilsTest(unittest.TestCase):
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

    def test_kwdict(self):
        self.assertEqual({}, castutils.kwdict())
        self.assertEqual({'foo': 'bar'}, castutils.kwdict(foo='bar'))
        self.assertEqual({'foo': 'bar', 'bar': 'foo'}, castutils.kwdict(foo='bar', bar='foo'))
        self.assertEqual({'bar': 1, 'foo': 'two', 'oof': None}, castutils.kwdict(oof=None, foo='two', bar=1))

        self.assertNotEqual({'bar': 1, 'foo': 'two'}, castutils.kwdict(oof=None, foo='two', bar=1))

    def test_nested_kwdict(self):
        self.assertEqual({'foo': 'bar', 'bar': {'one': 1, 'two': 2}}, castutils.kwdict(foo='bar', bar=castutils.kwdict(one=1, two=2)))
        self.assertEqual({'foo': 'bar', 'bar': {'one': 1, 'two': 2}}, castutils.kwdict(foo='bar', bar__one=1, bar__two=2))
        self.assertEqual({'foo': 'bar', 'bar': {'one': 1, 'two': {'more': 2, 'less': 3}}}, castutils.kwdict(foo='bar', bar__one=1, bar__two__more=2, bar__two__less=3))

        self.assertNotEqual({'foo': 'bar', 'bar': {'one': 1, 'two': {'more': 2, 'less': 3}}}, castutils.kwdict(foo='bar', bar__one=1, bar__two__more=2, bar__two_less=3))

    def test_big_kwdict(self):
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

        self.assertEqual(expected,
                         castutils.kwdict(simple_map__diego='Camera!',
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
                                          message_map__mickey__foo='mouse'))

    def test_mkproto(self):
        p1 = rainbow_pb2.SubMessage()
        p1.foo = 'Foo!'
        p1.bar = 'Bar!!!'

        self.assertEqual(p1, protoplasm.casting.mkproto(rainbow_pb2.SubMessage, foo='Foo!', bar='Bar!!!'))

        p2 = rainbow_pb2.SubMessage()
        p2.foo = 'Foo Two!'
        self.assertEqual(p2, protoplasm.casting.mkproto(rainbow_pb2.SubMessage, foo='Foo Two!'))

        p3 = rainbow_pb2.SubMessage()
        p3.foo = 'Not Foo!'
        self.assertNotEqual(p3, protoplasm.casting.mkproto(rainbow_pb2.SubMessage, foo='Foo You!'))

        p4 = rainbow_pb2.SubMessage()
        self.assertEqual(p4, protoplasm.casting.mkproto(rainbow_pb2.SubMessage))

    def test_nested_mkproto(self):
        p1 = rainbow_pb2.RainbowMessage()
        self.assertEqual(p1, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage))

        p2 = rainbow_pb2.RainbowMessage()
        p2.simple_field = 'Green'
        self.assertEqual(p2, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage, simple_field='Green'))
        self.assertNotEqual(p1, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage, simple_field='Green'))

        p3 = rainbow_pb2.RainbowMessage()
        p3.simple_field = 'Green'
        p3.message_field.foo = 'Blue'
        self.assertEqual(p3, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue'))
        p4 = rainbow_pb2.RainbowMessage()
        p4.simple_field = 'Green'
        p4.message_field.foo = 'Blue'
        p4.message_field.bar = 'Yellow'
        self.assertEqual(p4, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue',
                                                        message_field__bar='Yellow'))
        self.assertNotEqual(p3, p4)
        self.assertNotEqual(p4, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                           simple_field='Green',
                                                           message_field__foo='Blue',
                                                           message_field__bar='Red'))

        p5 = rainbow_pb2.RainbowMessage()
        p5.simple_field = 'Green'
        p5.message_field.foo = 'Blue'
        p5.message_field.bar = 'Yellow'
        p5.simple_list.append('Four')
        p5.simple_list.append('Seven')
        p5.simple_list.append('99')
        self.assertEqual(p5, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue',
                                                        message_field__bar='Yellow',
                                                        simple_list=['Four', 'Seven', '99']))

        p6 = rainbow_pb2.RainbowMessage()
        p6.simple_field = 'Green'
        p6.message_field.foo = 'Blue'
        p6.message_field.bar = 'Yellow'
        p6.simple_list.append('Four')
        p6.simple_list.append('Seven')
        p6.simple_list.append('98')
        self.assertNotEqual(p6, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                           simple_field='Green',
                                                           message_field__foo='Blue',
                                                           message_field__bar='Yellow',
                                                           simple_list=['Four', 'Seven', '100']))

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
        self.assertEqual(p7, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue',
                                                        message_field__bar='Yellow',
                                                        simple_list=['Four', 'Seven', '99'],
                                                        message_list=[castutils.kwdict(foo='Foo in a list',
                                                                              bar='Candybar'),
                                                             castutils.kwdict(foo='a Fool in a list',
                                                                              bar='Tequila bar')]))

        self.assertNotEqual(p7, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                           simple_field='Green',
                                                           message_field__foo='Blue',
                                                           message_field__bar='Yellow',
                                                           simple_list=['Four', 'Seven', '99'],
                                                           message_list=[castutils.kwdict(foo='a Fool in a list',
                                                                                 bar='Tequila bar')]))

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
        self.assertEqual(p8, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue',
                                                        message_field__bar='Yellow',
                                                        simple_list=['Four', 'Seven', '99'],
                                                        message_list=[castutils.kwdict(foo='Foo in a list',
                                                                              bar='Candybar'),
                                                             castutils.kwdict(foo='a Fool in a list',
                                                                              bar='Tequila bar')],
                                                        simple_map__dora='Imamap!',
                                                        simple_map__diego='Camera!'))

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
        self.assertEqual(p9, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
                                                        simple_field='Green',
                                                        message_field__foo='Blue',
                                                        message_field__bar='Yellow',
                                                        simple_list=['Four', 'Seven', '99'],
                                                        message_list=[castutils.kwdict(foo='Foo in a list',
                                                                              bar='Candybar'),
                                                             castutils.kwdict(foo='a Fool in a list',
                                                                              bar='Tequila bar')],
                                                        simple_map__dora='Imamap!',
                                                        simple_map__diego='Camera!',
                                                        message_map__donald__foo='duck',
                                                        message_map__donald__bar='trump',
                                                        message_map__mickey__foo='mouse'))

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

        self.assertEqual(p10, protoplasm.casting.mkproto(rainbow_pb2.RainbowMessage,
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
                                                         message_map__mickey__foo='mouse'))

    def test_mkdataclass(self):
        dc1 = rainbow_dc.SubMessage()
        dc1.foo = 'Foo!'
        dc1.bar = 'Bar!!!'

        self.assertEqual(dc1, protoplasm.casting.mkdataclass(rainbow_dc.SubMessage, foo='Foo!', bar='Bar!!!'))

        dc2 = rainbow_dc.SubMessage()
        dc2.foo = 'Foo Two!'
        self.assertEqual(dc2, protoplasm.casting.mkdataclass(rainbow_dc.SubMessage, foo='Foo Two!'))

        dc3 = rainbow_dc.SubMessage()
        dc3.foo = 'Not Foo!'
        self.assertNotEqual(dc3, protoplasm.casting.mkdataclass(rainbow_dc.SubMessage, foo='Foo You!'))

        dc4 = rainbow_dc.SubMessage()
        self.assertEqual(dc4, protoplasm.casting.mkdataclass(rainbow_dc.SubMessage))

    def test_nested_mkdataclass(self):
        dc1 = rainbow_dc.RainbowMessage()
        self.assertEqual(dc1, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage))

        dc2 = rainbow_dc.RainbowMessage()
        dc2.simple_field = 'Green'
        self.assertEqual(dc2, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage, simple_field='Green'))
        self.assertNotEqual(dc1,
                            protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage, simple_field='Green'))

        dc3 = rainbow_dc.RainbowMessage()
        dc3.simple_field = 'Green'
        dc3.message_field = rainbow_dc.SubMessage()
        dc3.message_field.foo = 'Blue'

        expected_dc3 = protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                      simple_field='Green',
                                                      message_field__foo='Blue')

        self.assertEqual(dc3, expected_dc3)

        dc4 = rainbow_dc.RainbowMessage()
        dc4.simple_field = 'Green'
        dc4.message_field = rainbow_dc.SubMessage()
        dc4.message_field.foo = 'Blue'
        dc4.message_field.bar = 'Yellow'
        self.assertEqual(dc4, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                             simple_field='Green',
                                                             message_field__foo='Blue',
                                                             message_field__bar='Yellow'))
        self.assertNotEqual(dc3, dc4)
        self.assertNotEqual(dc4, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                                simple_field='Green',
                                                                message_field__foo='Blue',
                                                                message_field__bar='Red'))

        dc5 = rainbow_dc.RainbowMessage()
        dc5.simple_field = 'Green'
        dc5.message_field = rainbow_dc.SubMessage('Blue', 'Yellow')
        dc5.simple_list.append('Four')
        dc5.simple_list.append('Seven')
        dc5.simple_list.append('99')
        self.assertEqual(dc5, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                             simple_field='Green',
                                                             message_field__foo='Blue',
                                                             message_field__bar='Yellow',
                                                             simple_list=['Four', 'Seven', '99']))

        dc6 = rainbow_dc.RainbowMessage()
        dc6.simple_field = 'Green'
        dc6.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc6.simple_list.append('Four')
        dc6.simple_list.append('Seven')
        dc6.simple_list.append('98')
        self.assertNotEqual(dc6, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                                simple_field='Green',
                                                                message_field__foo='Blue',
                                                                message_field__bar='Yellow',
                                                                simple_list=['Four', 'Seven', '100']))

        dc7 = rainbow_dc.RainbowMessage()
        dc7.simple_field = 'Green'
        dc7.message_field = rainbow_dc.SubMessage(foo='Blue', bar='Yellow')
        dc7.simple_list.append('Four')
        dc7.simple_list.append('Seven')
        dc7.simple_list.append('99')

        dc7.message_list.append(rainbow_dc.SubMessage(foo='Foo in a list', bar='Candybar'))
        dc7.message_list.append(rainbow_dc.SubMessage(foo='a Fool in a list', bar='Tequila bar'))

        self.assertEqual(dc7, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                             simple_field='Green',
                                                             message_field__foo='Blue',
                                                             message_field__bar='Yellow',
                                                             simple_list=['Four', 'Seven', '99'],
                                                             message_list=[castutils.kwdict(foo='Foo in a list',
                                                                                            bar='Candybar'),
                                                                           castutils.kwdict(foo='a Fool in a list',
                                                                                            bar='Tequila bar')]))

        self.assertNotEqual(dc7, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                                simple_field='Green',
                                                                message_field__foo='Blue',
                                                                message_field__bar='Yellow',
                                                                simple_list=['Four', 'Seven', '99'],
                                                                message_list=[castutils.kwdict(foo='a Fool in a list',
                                                                                               bar='Tequila bar')]))

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
        self.assertEqual(dc8, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                             simple_field='Green',
                                                             message_field__foo='Blue',
                                                             message_field__bar='Yellow',
                                                             simple_list=['Four', 'Seven', '99'],
                                                             message_list=[castutils.kwdict(foo='Foo in a list',
                                                                                            bar='Candybar'),
                                                                           castutils.kwdict(foo='a Fool in a list',
                                                                                            bar='Tequila bar')],
                                                             simple_map__dora='Imamap!',
                                                             simple_map__diego='Camera!'
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

        expected_dc9 = protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
                                                      simple_field='Green',
                                                      message_field__foo='Blue',
                                                      message_field__bar='Yellow',
                                                      simple_list=['Four', 'Seven', '99'],
                                                      message_list=[castutils.kwdict(foo='Foo in a list',
                                                                                     bar='Candybar'),
                                                                    castutils.kwdict(foo='a Fool in a list',
                                                                                     bar='Tequila bar')],
                                                      simple_map__dora='Imamap!',
                                                      simple_map__diego='Camera!',
                                                      message_map__donald__foo='duck',
                                                      message_map__donald__bar='trump',
                                                      message_map__mickey__foo='mouse'
                                                      )

        self.assertEqual(dc9, expected_dc9)

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

        self.assertEqual(dc10, protoplasm.casting.mkdataclass(rainbow_dc.RainbowMessage,
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
                                                              message_map__mickey__foo='mouse'
                                                             ))

    def test_import_dataclass(self):
        self.assertEqual(rainbow_dc.SubMessage, castutils.import_dataclass_by_proto(rainbow_pb2.SubMessage))
        self.assertEqual(rainbow_dc.SubMessage, castutils.import_dataclass_by_proto(rainbow_pb2.SubMessage()))
        self.assertEqual(rainbow_dc.RainbowMessage, castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage))
        self.assertEqual(rainbow_dc.RainbowMessage, castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage()))
        self.assertEqual(castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage()), castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage()))
        self.assertEqual(castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage), castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage()))
        self.assertNotEqual(castutils.import_dataclass_by_proto(rainbow_pb2.SubMessage), castutils.import_dataclass_by_proto(rainbow_pb2.RainbowMessage))

    def test_timestamp_mkproto(self):
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

        self.assertEqual(p_expect, protoplasm.casting.mkproto(rainbow_pb2.TimestampMessage, my_timestamp=ts1,
                                                                                            my_timestamp_list=[ts2, ts3],
                                                                                            my_timestamp_map__noon=ts4,
                                                                                            my_timestamp_map__midnight=ts5))

    def test_timestamp_mkdataclass(self):
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

        dc_expect = rainbow_dc.TimestampMessage()
        dc_expect.my_timestamp = dt1
        dc_expect.my_timestamp_list.append(dt2)
        dc_expect.my_timestamp_list.append(dt3)
        dc_expect.my_timestamp_map['noon'] = dt4
        dc_expect.my_timestamp_map['midnight'] = dt5

        self.assertEqual(dc_expect, protoplasm.casting.mkdataclass(rainbow_dc.TimestampMessage,
                                                                   my_timestamp=dt1,
                                                                   my_timestamp_list=[dt2, dt3],
                                                                   my_timestamp_map__noon=dt4,
                                                                   my_timestamp_map__midnight=dt5))

    def test_byte_mkproto(self):
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

        self.assertEqual(p_expect, protoplasm.casting.mkproto(rainbow_pb2.BytesMessage,
                                                              my_bytes=as_base64_1,
                                                              my_bytes_list=[as_base64_2, as_base64_3],
                                                              my_bytes_map__zero=as_base64_4,
                                                              my_bytes_map__one=as_base64_5))

    def test_byte_mkdataclass(self):
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

        dc_expect = rainbow_dc.BytesMessage()
        dc_expect.my_bytes = as_bytes_1
        dc_expect.my_bytes_list.append(as_bytes_2)
        dc_expect.my_bytes_list.append(as_bytes_3)
        dc_expect.my_bytes_map['zero'] = as_bytes_4
        dc_expect.my_bytes_map['one'] = as_bytes_5

        self.assertEqual(dc_expect, protoplasm.casting.mkdataclass(rainbow_dc.BytesMessage,
                                                                   my_bytes=as_bytes_1,
                                                                   my_bytes_list=[as_bytes_2, as_base64_3],
                                                                   my_bytes_map__zero=as_bytes_4,
                                                                   my_bytes_map__one=as_base64_5))

    def test_enum_mkproto(self):
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

        self.assertEqual(p_expect, protoplasm.casting.mkproto(enums_pb2.WithExternalEnum,
                                                              my_enum=2,
                                                              my_alias_enum=3,
                                                              my_enum_list=[1, 3],
                                                              my_alias_enum_list=[1, 2, 1],
                                                              my_enum_map__one=1,
                                                              my_enum_map__two=2,
                                                              my_alias_enum_map__six=3,
                                                              my_alias_enum_map__sex=3,
                                                              my_alias_enum_map__fimm=2))
        self.assertEqual(p_expect, protoplasm.casting.mkproto(enums_pb2.WithExternalEnum,
                                                              my_enum=enums_pb2.TWO,
                                                              my_alias_enum=enums_pb2.SIX,
                                                              my_enum_list=[enums_pb2.ONE, enums_pb2.THREE],
                                                              my_alias_enum_list=[enums_pb2.FOUR, enums_pb2.FIVE, enums_pb2.FJORIR],
                                                              my_enum_map__one=enums_pb2.ONE,
                                                              my_enum_map__two=enums_pb2.TWO,
                                                              my_alias_enum_map__six=enums_pb2.SIX,
                                                              my_alias_enum_map__sex=enums_pb2.SEX,
                                                              my_alias_enum_map__fimm=enums_pb2.FIMM))

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

        self.assertEqual(p_expect2, protoplasm.casting.mkproto(enums_pb2.WithInternalEnum,
                                                               my_internal_enum=enums_pb2.WithInternalEnum.SIX,
                                                               my_internal_alias_enum=enums_pb2.WithInternalEnum.SEVEN,
                                                               my_internal_enum_list=[enums_pb2.WithInternalEnum.FIVE,
                                                                                      enums_pb2.WithInternalEnum.FOUR],
                                                               my_internal_alias_enum_list=[enums_pb2.WithInternalEnum.SJO,
                                                                                            enums_pb2.WithInternalEnum.ATTA,
                                                                                            enums_pb2.WithInternalEnum.EIGHT],
                                                               my_internal_enum_map__no5=enums_pb2.WithInternalEnum.FIVE,
                                                               my_internal_enum_map__no6=enums_pb2.WithInternalEnum.SIX,
                                                               my_internal_alias_enum_map__no9=enums_pb2.WithInternalEnum.NIU,
                                                               my_internal_alias_enum_map__no9B=enums_pb2.WithInternalEnum.NINE,
                                                               my_internal_alias_enum_map__default=enums_pb2.WithInternalEnum.ZERO))

        self.assertEqual(p_expect2, protoplasm.casting.mkproto(enums_pb2.WithInternalEnum,
                                                               my_internal_enum=6,
                                                               my_internal_alias_enum=7,
                                                               my_internal_enum_list=[5, 4],
                                                               my_internal_alias_enum_list=[7, 8, 8],
                                                               my_internal_enum_map__no5=5,
                                                               my_internal_enum_map__no6=6,
                                                               my_internal_alias_enum_map__no9=9,
                                                               my_internal_alias_enum_map__no9B=9,
                                                               my_internal_alias_enum_map__default=0))

    def test_enum_mkdataclass(self):
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

        self.assertEqual(dc_expect, protoplasm.casting.mkdataclass(enums_dc.WithExternalEnum,
                                                                   my_enum=2,
                                                                   my_alias_enum=3,
                                                                   my_enum_list=[1, 3],
                                                                   my_alias_enum_list=[1, 2, 1],
                                                                   my_enum_map__one=1,
                                                                   my_enum_map__two=2,
                                                                   my_alias_enum_map__six=3,
                                                                   my_alias_enum_map__sex=3,
                                                                   my_alias_enum_map__fimm=2))
        self.assertEqual(dc_expect, protoplasm.casting.mkdataclass(enums_dc.WithExternalEnum,
                                                                   my_enum=enums_dc.TWO,
                                                                   my_alias_enum=enums_dc.SIX,
                                                                   my_enum_list=[enums_dc.ONE, enums_dc.THREE],
                                                                   my_alias_enum_list=[enums_dc.FOUR, enums_dc.FIVE,
                                                                                       enums_dc.FJORIR],
                                                                   my_enum_map__one=enums_dc.ONE,
                                                                   my_enum_map__two=enums_dc.TWO,
                                                                   my_alias_enum_map__six=enums_dc.SIX,
                                                                   my_alias_enum_map__sex=enums_dc.SEX,
                                                                   my_alias_enum_map__fimm=enums_dc.FIMM))

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

        self.assertEqual(dc_expect2, protoplasm.casting.mkdataclass(enums_dc.WithInternalEnum,
                                                                    my_internal_enum=enums_dc.WithInternalEnum.SIX,
                                                                    my_internal_alias_enum=enums_dc.WithInternalEnum.SEVEN,
                                                                    my_internal_enum_list=[enums_dc.WithInternalEnum.FIVE,
                                                                                           enums_dc.WithInternalEnum.FOUR],
                                                                    my_internal_alias_enum_list=[
                                                                        enums_dc.WithInternalEnum.SJO,
                                                                        enums_dc.WithInternalEnum.ATTA,
                                                                        enums_dc.WithInternalEnum.EIGHT],
                                                                    my_internal_enum_map__no5=enums_dc.WithInternalEnum.FIVE,
                                                                    my_internal_enum_map__no6=enums_dc.WithInternalEnum.SIX,
                                                                    my_internal_alias_enum_map__no9=enums_dc.WithInternalEnum.NIU,
                                                                    my_internal_alias_enum_map__no9B=enums_dc.WithInternalEnum.NINE,
                                                                    my_internal_alias_enum_map__default=enums_dc.WithInternalEnum.ZERO))

        self.assertEqual(dc_expect2, protoplasm.casting.mkdataclass(enums_dc.WithInternalEnum,
                                                                    my_internal_enum=6,
                                                                    my_internal_alias_enum=7,
                                                                    my_internal_enum_list=[5, 4],
                                                                    my_internal_alias_enum_list=[7, 8, 8],
                                                                    my_internal_enum_map__no5=5,
                                                                    my_internal_enum_map__no6=6,
                                                                    my_internal_alias_enum_map__no9=9,
                                                                    my_internal_alias_enum_map__no9B=9,
                                                                    my_internal_alias_enum_map__default=0))
