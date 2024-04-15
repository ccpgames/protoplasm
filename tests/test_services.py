import unittest

import os
import sys
import shutil
import time

import grpc

from protoplasm import errors

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

HERE = os.path.dirname(__file__)

PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')


class ServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Remove old stuff...
        build_package = os.path.join(BUILD_ROOT, 'unittesting')
        if os.path.exists(build_package):
            shutil.rmtree(build_package)
            time.sleep(0.1)

        from neobuilder.neobuilder import NeoBuilder

        # Build stuff...
        builder = NeoBuilder(package='unittesting',
                             protopath=PROTO_ROOT,
                             build_root=BUILD_ROOT)
        builder.build()

        # Add build root to path to access its modules
        sys.path.append(BUILD_ROOT)

    def test_raw_server_and_raw_client(self):
        port = '50042'
        log.info(f'Beginning...')
        from tests.servicetestutils.raw_server import UnaryServiceServer
        server = UnaryServiceServer()
        server.start(f'[::]:{port}')

        from tests.servicetestutils import raw_client
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 0)
        raw_client.call_WithNoData(f'localhost:{port}')
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 1)
        raw_client.call_WithNoData(f'localhost:{port}')
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithInput'], 0)
        raw_client.call_WithInput(f'localhost:{port}', unnamed_input='did I win?')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 0)
        res = raw_client.call_WithOutput(f'localhost:{port}')
        self.assertEqual(res, 'you win')
        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 0)
        res = raw_client.call_WithBoth(f'localhost:{port}', some_input='reverse me please')
        self.assertEqual(res, 'esaelp em esrever')
        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 0)
        raw_client.call_WithManyInputs(f'localhost:{port}', first_input='yay', second_input=42, third_input=True)
        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 0)
        res_a, res_b, res_c = raw_client.call_WithManyOutputs(f'localhost:{port}')
        self.assertEqual(res_a, 'snorlax')
        self.assertEqual(res_b, 7)
        self.assertTrue(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 0)
        res_a, res_b, res_c = raw_client.call_WithManyBoths(f'localhost:{port}',
                                                            another_first_input='bar',
                                                            another_second_input=42,
                                                            another_third_input=True)
        self.assertEqual(res_a, 'BAR')
        self.assertEqual(res_b, 21)
        self.assertFalse(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 1)

        # Now lets break it...
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)
        with self.assertRaises(grpc.RpcError) as cm:
            raw_client.call_WithInput(f'localhost:{port}', unnamed_input='explode')
        self.assertEqual(cm.exception.code(), grpc.StatusCode.NOT_FOUND)  # noqa
        self.assertEqual(cm.exception.details(), 'totally fake not found error')  # noqa
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 2)

        raw_client.call_WithInput(f'localhost:{port}', unnamed_input='nevermind')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 3)

        server.stop()

    def test_raw_server_and_protoplasm_client(self):
        port = '50043'
        log.info(f'Beginning...')
        from tests.servicetestutils.raw_server import UnaryServiceServer
        server = UnaryServiceServer()
        server.start(f'[::]:{port}')

        from unittesting.unary.unaryservice_grpc_sender import UnaryService
        client = UnaryService(f'localhost:{port}')

        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 0)
        client.with_no_data()
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 1)
        client.with_no_data()
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithInput'], 0)
        client.with_input('did I win?')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)
        with self.assertRaises(errors.NotFound) as cm:
            client.with_input('explode')
        self.assertEqual(cm.exception.status_code, grpc.StatusCode.NOT_FOUND)
        self.assertEqual(cm.exception.details, 'totally fake not found error')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 0)
        res = client.with_output()
        self.assertEqual(res, 'you win')
        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 0)
        res = client.with_both('reverse me please')
        self.assertEqual(res, 'esaelp em esrever')
        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 0)
        client.with_many_inputs(first_input='yay', second_input=42, third_input=True)
        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 0)
        res_a, res_b, res_c = client.with_many_outputs()
        self.assertEqual(res_a, 'snorlax')
        self.assertEqual(res_b, 7)
        self.assertTrue(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 0)
        res_a, res_b, res_c = client.with_many_boths(another_first_input='bar',
                                                     another_second_input=42,
                                                     another_third_input=True)
        self.assertEqual(res_a, 'BAR')
        self.assertEqual(res_b, 21)
        self.assertFalse(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 1)

        server.stop()

    def test_protoplasm_server_and_raw_client(self):
        port = '50041'
        log.info(f'Beginning...')
        from tests.servicetestutils.plasm_server import UnaryProtoplasmServer
        server = UnaryProtoplasmServer()
        server.start(f'[::]:{port}')

        from tests.servicetestutils import raw_client
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 0)
        raw_client.call_WithNoData(f'localhost:{port}')
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 1)
        raw_client.call_WithNoData(f'localhost:{port}')
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithInput'], 0)
        raw_client.call_WithInput(f'localhost:{port}', unnamed_input='did I win?')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 0)
        res = raw_client.call_WithOutput(f'localhost:{port}')
        self.assertEqual(res, 'you win')
        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 0)
        res = raw_client.call_WithBoth(f'localhost:{port}', some_input='reverse me please')
        self.assertEqual(res, 'esaelp em esrever')
        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 0)
        raw_client.call_WithManyInputs(f'localhost:{port}', first_input='yay', second_input=42, third_input=True)
        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 0)
        res_a, res_b, res_c = raw_client.call_WithManyOutputs(f'localhost:{port}')
        self.assertEqual(res_a, 'snorlax')
        self.assertEqual(res_b, 7)
        self.assertTrue(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 0)
        res_a, res_b, res_c = raw_client.call_WithManyBoths(f'localhost:{port}',
                                                            another_first_input='bar',
                                                            another_second_input=42,
                                                            another_third_input=True)
        self.assertEqual(res_a, 'BAR')
        self.assertEqual(res_b, 21)
        self.assertFalse(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 1)

        # Now lets break it...
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)
        with self.assertRaises(grpc.RpcError) as cm:
            raw_client.call_WithInput(f'localhost:{port}', unnamed_input='explode')
        self.assertEqual(cm.exception.code(), grpc.StatusCode.NOT_FOUND)  # noqa
        self.assertEqual(cm.exception.details(), 'totally fake not found error')  # noqa
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 2)

        raw_client.call_WithInput(f'localhost:{port}', unnamed_input='nevermind')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 3)

        server.stop()

    def test_protoplasm_server_and_protoplasm_client(self):
        port = '50044'
        log.info(f'Beginning...')
        from tests.servicetestutils.plasm_server import UnaryProtoplasmServer
        server = UnaryProtoplasmServer()
        server.start(f'[::]:{port}')

        from unittesting.unary.unaryservice_grpc_sender import UnaryService
        client = UnaryService(f'localhost:{port}')

        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 0)
        client.with_no_data()
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 1)
        client.with_no_data()
        self.assertEqual(server.servicer_implementation.calls['WithNoData'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithInput'], 0)
        client.with_input('did I win?')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 1)
        with self.assertRaises(errors.NotFound) as cm:
            client.with_input('explode')
        self.assertEqual(cm.exception.status_code, grpc.StatusCode.NOT_FOUND)
        self.assertEqual(cm.exception.details, 'totally fake not found error')
        self.assertEqual(server.servicer_implementation.calls['WithInput'], 2)

        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 0)
        res = client.with_output()
        self.assertEqual(res, 'you win')
        self.assertEqual(server.servicer_implementation.calls['WithOutput'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 0)
        res = client.with_both('reverse me please')
        self.assertEqual(res, 'esaelp em esrever')
        self.assertEqual(server.servicer_implementation.calls['WithBoth'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 0)
        client.with_many_inputs(first_input='yay', second_input=42, third_input=True)
        self.assertEqual(server.servicer_implementation.calls['WithManyInputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 0)
        res_a, res_b, res_c = client.with_many_outputs()
        self.assertEqual(res_a, 'snorlax')
        self.assertEqual(res_b, 7)
        self.assertTrue(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyOutputs'], 1)

        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 0)
        res_a, res_b, res_c = client.with_many_boths(another_first_input='bar',
                                                     another_second_input=42,
                                                     another_third_input=True)
        self.assertEqual(res_a, 'BAR')
        self.assertEqual(res_b, 21)
        self.assertFalse(res_c)
        self.assertEqual(server.servicer_implementation.calls['WithManyBoths'], 1)

        server.stop()
