import unittest
from protoplasm import casting
import os
import sys

import shutil
import time
HERE = os.path.dirname(__file__)
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def _get_sub():
    from sandbox.test import rainbow_dc
    return rainbow_dc.SubMessage.from_dict({'foo': 'Foo!', 'bar': 'Bar!'})


class DataclassTest(unittest.TestCase):
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
