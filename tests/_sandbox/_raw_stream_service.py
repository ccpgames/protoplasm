from sandbox.test import river_pb2
from sandbox.test import river_pb2_grpc
import grpc
from concurrent import futures
from typing import *
import time
import random

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level='DEBUG')


class RiverServicer(river_pb2_grpc.StreamingServiceServicer):

    def ReverseMyShit(self,
                      request: river_pb2.ReverseMyShitRequest,
                      context: grpc.ServicerContext) -> river_pb2.ReverseMyShitResponse:
        log.info(f'RiverServicer.ReverseMyShit({request}, {context})')
        log.info(f'RiverServicer.ReverseMyShit(request.shit={request.shit})')

        return river_pb2.ReverseMyShitResponse(tihs=request.shit[::-1])

    def MarcoPolo(self,
                  request_iterator: Iterable[river_pb2.MarcoPoloRequest],
                  context: grpc.ServicerContext) -> Iterable[river_pb2.MarcoPoloResponse]:
        log.info(f'RiverServicer.MarcoPolo({request_iterator}, {context})')
        i = 0
        for request in request_iterator:
            log.info(f'RiverServicer.MarcoPolo()...request={request}')
            if request.question.lower().startswith('marco'):
                response = river_pb2.MarcoPoloResponse(answer=f'Polo! #{i}')
                log.info(f'RiverServicer.MarcoPolo()...{response}')
                i += 1
                yield response
                s = random.randint(1, 5)
                log.info(f'RiverServicer.MarcoPolo()... sleeping for {s}')

                if i >= 14:
                    log.info(f'RiverServicer.MarcoPolo()... Im tired!!!')
                    break
                time.sleep(s)
            else:
                raise ValueError('that was not marco')

        log.info(f'RiverServicer.MarcoPolo()... DONE!')

    def TellMeAStory(self,
                     request: river_pb2.TellMeAStoryRequest,
                     context: grpc.ServicerContext) -> Iterable[river_pb2.TellMeAStoryResponse]:
        log.info(f'RiverServicer.TellMeAStory({request}, {context})')
        i = 0
        while i < 10:
            response = river_pb2.TellMeAStoryResponse(line=f'This is line #{i}')
            log.info(f'RiverServicer.TellMeAStory()...{response}')
            i += 1
            yield response
            log.info(f'RiverServicer.TellMeAStory()... sleeping')
            time.sleep(3)

        log.info(f'RiverServicer.TellMeAStory()... DONE!')

    def GuessTheNumber(self,
                       request_iterator: Iterable[river_pb2.GuessTheNumberRequest],
                       context: grpc.ServicerContext) -> river_pb2.GuessTheNumberResponse:
        log.info(f'RiverServicer.GuessTheNumber({request_iterator}, {context})')

        for request in request_iterator:
            log.info(f'RiverServicer.GuessTheNumber()...request={request}')
            if request.number == 42:
                response = river_pb2.GuessTheNumberResponse(did_i_win=f'YOU WON!!!')
                log.info(f'RiverServicer.GuessTheNumber()...CORRECT!!!! {response}')
                return response

            else:
                log.info(f'RiverServicer.GuessTheNumber()...WRONG!')

        log.info(f'RiverServicer.GuessTheNumber()... DONE!')


def serve():
    log.info(f'Beginning...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    river_pb2_grpc.add_StreamingServiceServicer_to_server(RiverServicer(), server)
    server.add_insecure_port('[::]:50051')
    log.info(f'Starting...')
    server.start()
    log.info(f'Started! Waiting...')
    server.wait_for_termination()


def main():
    serve()


if __name__ == '__main__':
    main()

