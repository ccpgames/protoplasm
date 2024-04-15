import unittest
import base64
from protoplasm.casting import castutils

import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

TEXT_BLARG = '''In computer programming, Base64 is a group of binary-to-text encoding schemes that represent binary data (more specifically, a sequence of 8-bit bytes) in sequences of 24 bits that can be represented by four 6-bit Base64 digits.

Common to all binary-to-text encoding schemes, Base64 is designed to carry data stored in binary formats across channels that only reliably support text content. Base64 is particularly prevalent on the World Wide Web[1] where one of its uses is the ability to embed image files or other binary assets inside textual assets such as HTML and CSS files.[2]

Base64 is also widely used for sending e-mail attachments. This is required because SMTP – in its original form – was designed to transport 7-bit ASCII characters only. This encoding causes an overhead of 33–37% (33% by the encoding itself; up to 4% more by the inserted line breaks).'''


class Base64StuffTest(unittest.TestCase):
    def test_padd_fixer(self):
        for i in range(len(TEXT_BLARG)):
            part = TEXT_BLARG[0:i]
            part_enc = part.encode()
            raw64 = base64.encodebytes(part.encode())
            stripped = castutils.base64_stripper(raw64)

            a = castutils.fuzzy_base64_to_bytes(raw64)
            self.assertEqual(a, part_enc, msg=f'A failed with length={i}')
            b = castutils.fuzzy_base64_to_bytes(stripped)
            self.assertEqual(b, part_enc, msg=f'B failed with length={i}')

