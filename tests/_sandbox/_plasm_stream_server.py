import sandbox
from sandbox.test import river_dc as dc
from sandbox.test.river_dc import *
from sandbox.test.river_api import StreamingServiceInterface
from sandbox.test.river_grpc_receiver import StreamingServiceGrpcServicer

from protoplasm.plasm import *

import random

import time
import logging
logging.basicConfig(level='DEBUG')
log = logging.getLogger(__name__)

sandbox.load_symbols()  # This is the old "from sandbox import __everything__"


class PlasmStreamingService(StreamingServiceInterface):
    def reverse_my_shit(self, shit: str = None) -> str:
        log.info(f'PlasmStreamingService.reverse_my_shit(shit={shit})')
        return shit[::-1]

    def marco_polo(self, request_iterator: Iterable[dc.MarcoPoloRequest]) -> Iterable[MarcoPoloResponse]:
        log.info(f'PlasmStreamingService.marco_polo(story={request_iterator})')
        i = 0
        for request in request_iterator:
            log.info(f'PlasmStreamingService.marco_polo()...request={request}')
            if request.question.lower().startswith('marco'):
                response = MarcoPoloResponse(answer=f'Polo! #{i}')
                log.info(f'PlasmStreamingService.marco_polo()...{response}')
                i += 1
                yield response
                s = random.randint(1, 5)
                log.info(f'PlasmStreamingService.marco_polo()... sleeping for {s}')

                if i >= 14:
                    log.info(f'PlasmStreamingService.marco_polo()... Im tired!!!')
                    break
                time.sleep(s)
            else:
                raise PostRequestError('that was not marco')

        log.info(f'PlasmStreamingService.marco_polo()... DONE!')

    def tell_me_a_story(self, story: str = None) -> Iterable[dc.TellMeAStoryResponse]:
        log.info(f'PlasmStreamingService.tell_me_a_story(story={story})')
        i = 0
        while i < 10:
            response = dc.TellMeAStoryResponse(line=f'This is line #{i} of the "{story}" story')
            log.info(f'PlasmStreamingService.tell_me_a_story()...{response}')
            i += 1
            yield response
            # yield f'This is line #{i} of the "{story}" story'
            log.info(f'PlasmStreamingService.tell_me_a_story()... sleeping')
            time.sleep(3)

        log.info(f'PlasmStreamingService.tell_me_a_story()... DONE!')

    def guess_the_number(self, request_iterator: Iterable[dc.GuessTheNumberRequest]) -> str:
        log.info(f'PlasmStreamingService.guess_the_number({request_iterator})')

        for request in request_iterator:
            log.info(f'PlasmStreamingService.guess_the_number()...request={request}')
            if request.number == 42:
                log.info(f'PlasmStreamingService.guess_the_number()...CORRECT!!!!')
                return 'YOU WON!!!'

            else:
                log.info(f'PlasmStreamingService.guess_the_number()...WRONG!')

        log.info(f'PlasmStreamingService.guess_the_number()... DONE!')


def forward_stuff(impl, stuff):
    return impl.tell_me_a_story(stuff)


def main():
    server = GrpcServer(port='[::]:50051', max_workers=10)
    server.add_servicer(StreamingServiceGrpcServicer(PlasmStreamingService()))
    server.serve()
    # impl = PlasmStreamingService()
    # for r in forward_stuff(impl, 'Odyssey'):
    #     print(r)


if __name__ == '__main__':
    main()
