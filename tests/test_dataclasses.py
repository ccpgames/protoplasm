import unittest
from protoplasm import casting
import os
import sys
import shutil
import time

from tests.testutils import *

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DataclassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_new_protos()
        # Add build root to path to access its modules
        sys.path.append(BUILD_ROOT)

    def test_args(self):
        from sandbox.test import rainbow_dc

        dc1 = rainbow_dc.RainbowMessage()
        dc1.simple_field = 'I iz string'
        dc1.message_field = rainbow_dc.SubMessage.from_dict({'foo': 'Foo!', 'bar': 'Bar!'})
        dc1.simple_list = ['one', 'two', "Freddy's coming for you!"]
        dc1.message_list = [rainbow_dc.SubMessage(foo='Foo1!', bar='Bar1!'),
                            rainbow_dc.SubMessage(foo='Foo2!', bar='Bar2!'),
                            rainbow_dc.SubMessage(foo='Foo3!', bar='Bar3!')]
        dc1.simple_map = {'uno': 'einn', 'dos': 'tveir'}
        dc1.message_map = {'ein': rainbow_dc.SubMessage(foo='Foo11!', bar='Bar11!'),
                           'zwei': rainbow_dc.SubMessage(foo='Foo22!', bar='Bar22!')}

        dc2 = rainbow_dc.RainbowMessage('I iz string',
                                        rainbow_dc.SubMessage(foo='Foo!', bar='Bar!'),
                                        ['one', 'two', "Freddy's coming for you!"],
                                        [rainbow_dc.SubMessage(foo='Foo1!', bar='Bar1!'),
                                         rainbow_dc.SubMessage(foo='Foo2!', bar='Bar2!'),
                                         rainbow_dc.SubMessage(foo='Foo3!', bar='Bar3!')],
                                        {'uno': 'einn', 'dos': 'tveir'},
                                        {'ein': rainbow_dc.SubMessage(foo='Foo11!', bar='Bar11!'),
                                         'zwei': rainbow_dc.SubMessage(foo='Foo22!', bar='Bar22!')})

        self.assertEqual(dc1, dc2)

    def test_shortcut_args(self):
        from sandbox.test import rainbow_dc

        dc1 = rainbow_dc.RainbowMessage('I iz string', 'Foo!')
        dc2 = rainbow_dc.RainbowMessage('I iz string', rainbow_dc.SubMessage(foo='Foo!'))

        dc2b = rainbow_dc.RainbowMessage.from_kwdict(simple_field='I iz string', message_field='Foo!')

        self.assertEqual(dc1, dc2)
        self.assertEqual(dc1, dc2b)

        dc3 = rainbow_dc.RainbowMessage('I iz string', ('Foo!', 'Bar!'))
        dc4 = rainbow_dc.RainbowMessage('I iz string', {'foo': 'Foo!', 'bar': 'Bar!'})
        dc5 = rainbow_dc.RainbowMessage('I iz string', rainbow_dc.SubMessage(foo='Foo!', bar='Bar!'))
        dc5b = rainbow_dc.RainbowMessage.from_kwdict(simple_field='I iz string', message_field=('Foo!', 'Bar!'))

        self.assertEqual(dc3, dc4)
        self.assertEqual(dc3, dc5)
        self.assertEqual(dc3, dc5b)
        self.assertNotEqual(dc1, dc3)

    def test_shortcut_list_args(self):
        from sandbox.test import rainbow_dc
        dc1 = rainbow_dc.RainbowMessage(message_list=['Foo!', 'Foo2!'])
        dc2 = rainbow_dc.RainbowMessage(message_list=[rainbow_dc.SubMessage(foo='Foo!'),
                                                      rainbow_dc.SubMessage(foo='Foo2!')])

        self.assertEqual(dc1, dc2)

        dc3 = rainbow_dc.RainbowMessage(message_list=[('Foo!', 'Bar!'), ('Foo2!', 'Bar2!')])
        dc4 = rainbow_dc.RainbowMessage(message_list=[{'foo': 'Foo!', 'bar': 'Bar!'}, {'foo': 'Foo2!', 'bar': 'Bar2!'}])
        dc5 = rainbow_dc.RainbowMessage(message_list=[rainbow_dc.SubMessage(foo='Foo!', bar='Bar!'),
                                                      rainbow_dc.SubMessage(foo='Foo2!', bar='Bar2!')])
        dc6 = rainbow_dc.RainbowMessage(message_list=[('Foo!', 'Bar!'), ('Foo2!', 'Bar2!')])
        dc7 = rainbow_dc.RainbowMessage(message_list=[('Foo!', 'Bar!'), {'foo': 'Foo2!', 'bar': 'Bar2!'}])
        dc8 = rainbow_dc.RainbowMessage(message_list=[rainbow_dc.SubMessage(foo='Foo!', bar='Bar!'), {'foo': 'Foo2!', 'bar': 'Bar2!'}])
        self.assertEqual(dc3, dc4)
        self.assertEqual(dc3, dc5)
        self.assertEqual(dc3, dc6)
        self.assertEqual(dc3, dc7)
        self.assertEqual(dc3, dc8)
        self.assertNotEqual(dc1, dc3)

    def test_shortcut_dict_args(self):
        from sandbox.test import rainbow_dc
        dc1 = rainbow_dc.RainbowMessage(message_map={'one': 'Foo!', 'two': 'Foo2!'})
        dc2 = rainbow_dc.RainbowMessage(message_map={'one': rainbow_dc.SubMessage(foo='Foo!'),
                                                     'two': rainbow_dc.SubMessage(foo='Foo2!')})
        dc2b = rainbow_dc.RainbowMessage.from_kwdict(message_map={'one': 'Foo!', 'two': 'Foo2!'})

        self.assertEqual(dc1, dc2)
        self.assertEqual(dc1, dc2b)

        dc3 = rainbow_dc.RainbowMessage(message_map={'one': ('Foo!', 'Bar!'), 'two': ('Foo2!', 'Bar2!')})
        dc4 = rainbow_dc.RainbowMessage(message_map={'one': {'foo': 'Foo!', 'bar': 'Bar!'}, 'two': {'foo': 'Foo2!', 'bar': 'Bar2!'}})
        dc5 = rainbow_dc.RainbowMessage(message_map={'one': rainbow_dc.SubMessage(foo='Foo!', bar='Bar!'),
                                                     'two': rainbow_dc.SubMessage(foo='Foo2!', bar='Bar2!')})
        self.assertEqual(dc3, dc4)
        self.assertEqual(dc3, dc5)
        self.assertNotEqual(dc1, dc3)

    def test_load_symbols(self):
        import sandbox
        sandbox.load_symbols()

    def test_import_collision(self):
        from protoplasm import plasm
        from typing import Type as typing_Type
        from sandbox.test.importcollision_dc import Type
        self.assertNotEqual(typing_Type, Type)
        self.assertTrue(issubclass(Type, plasm.DataclassBase))

        from sandbox.test.importcollision_dc import Collection
        from typing import Collection as typing_Collection
        self.assertNotEqual(typing_Collection, Collection)
        self.assertTrue(issubclass(Collection, plasm.DataclassBase))

    def test_import_collision_via_string(self):
        from protoplasm import plasm
        from ccptools.tpu import strimp
        from typing import Type as typing_Type
        Type = strimp.get_class('sandbox.test.importcollision_dc.Type')
        self.assertNotEqual(typing_Type, Type)
        self.assertTrue(issubclass(Type, plasm.DataclassBase))

        Collection = strimp.get_class('sandbox.test.importcollision_dc.Collection')
        from typing import Collection as typing_Collection
        self.assertNotEqual(typing_Collection, Collection)
        self.assertTrue(issubclass(Collection, plasm.DataclassBase))
