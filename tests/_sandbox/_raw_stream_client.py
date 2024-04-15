from sandbox.test import river_pb2
from sandbox.test import river_pb2_grpc
import grpc
from concurrent import futures
from typing import *
import asyncio
import time
import random
from grpc._channel import _MultiThreadedRendezvous


import logging
log = logging.getLogger(__name__)

logging.basicConfig(level='DEBUG')

_I_AM_WAITING = False


def _guess_a_lot() -> Iterable[river_pb2.GuessTheNumberRequest]:
    for i in range(35, 45):
        r = river_pb2.GuessTheNumberRequest(number=i)
        log.info(f'yielding {r}')
        yield r
        time.sleep(2)


def guess():
    log.info(f'Opening channel...')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = river_pb2_grpc.StreamingServiceStub(channel)
        results: river_pb2.GuessTheNumberResponse = stub.GuessTheNumber(
            _guess_a_lot()
        )
        log.info(f'results={results}')
        log.info(f'results={results.did_i_win}')
        log.info(f'Done!')


def reverse_shit():  # Direct Request/Response
    log.info(f'Opening channel...')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = river_pb2_grpc.StreamingServiceStub(channel)
        results: river_pb2.ReverseMyShitResponse = stub.ReverseMyShit(river_pb2.ReverseMyShitRequest(
            shit='this is not an anagram'
        ))
        log.info(f'results={results}')
        log.info(f'results={results.tihs}')

        log.info(f'Done!')


def story():  # Direct Request, Streaming Response
    log.info(f'Opening channel...')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = river_pb2_grpc.StreamingServiceStub(channel)
        results: Iterable[river_pb2.TellMeAStoryResponse] = stub.TellMeAStory(
            river_pb2.TellMeAStoryRequest(story='odyssey')
        )
        # TODO(thordurm@ccpgames.com) 2022-06-02: How should we "hang up" from the Client side?
        # TODO(thordurm@ccpgames.com) 2022-06-02: How should we handle hang-ups from the server side (and how do they manifest)?
        for response in results:
            log.info(f'response={response}')
        log.info(f'Done!')


def _get_a_bunch_of_marcos() -> Iterable[river_pb2.MarcoPoloRequest]:
    for i in range(0, 100):
        r = river_pb2.MarcoPoloRequest(question=f'Marco! #{i}')
        log.info(f'yielding {r}')
        yield r
        time.sleep(random.randint(1, 5))


def marco():  # Dual-side streaming!
    log.info(f'Opening channel...')
    with grpc.insecure_channel('localhost:50051') as channel:

        marco_iterator: Iterable[river_pb2.MarcoPoloRequest] = _get_a_bunch_of_marcos()

        stub = river_pb2_grpc.StreamingServiceStub(channel)
        result_iterator: Iterable[river_pb2.MarcoPoloResponse] = stub.MarcoPolo(
            marco_iterator
        )

        for response in result_iterator:
            log.info(f'response={response}')

        log.info(f'Done!')



async def _do_marco(stub):
    async for response in stub.MarcoPolo(_get_a_bunch_of_marcos()):
        yield response


async def aio_marco():  # Dual-side streaming!
    global _I_AM_WAITING
    log.info(f'Opening channel...')
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = river_pb2_grpc.StreamingServiceStub(channel)
        log.info(f'foo')
        async for response in _do_marco(stub):
            log.info(f'response={response}')
            _I_AM_WAITING = False
        log.info(f'Done!')


def main():
    log.info(f'Beginning...')
    marco()
    # guess()
    reverse_shit()
    # try:
    #     story()
    # except Exception as ex:
    #     log.exception(f'Damnit! {ex!r}')
    # reverse_shit()
    log.info(f'Done...')


async def aio_main():
    log.info(f'Beginning...')
    await aio_marco()


if __name__ == '__main__':
    main()
    # asyncio.get_event_loop().run_until_complete(aio_main())

