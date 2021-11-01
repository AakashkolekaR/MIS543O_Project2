import random
import time 

from .BasicTest import *

"""
This tests random delays.
"""
class RandomDelayTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            if random.choice([True, False]):
                delay = random.randint(0,1)
                time.sleep(delay)
            self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []
