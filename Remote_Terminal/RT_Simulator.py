import logging
logger = logging.getLogger()
import sys
from .Message_Layer.ML_Analyzer_RT import MessageLayerAnalyzerRT
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Listener
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Sender
import threading
import time


class Remote_Terminal:

    def __init__(self):
        pass

    def send_data_to_bc(self, frames):
        for frame in frames:
            if frame:
                message = frame.encode("utf-8")
                RT_Sender().send_message(message)
                time.sleep(1)
                logger.debug(message)
            else:
                continue

    def _handle_incoming_frame(self, frame):
        logger.debug("input {}".format(frame, "s"))
        frames = \
            MessageLayerAnalyzerRT().interprete_incoming_frame(frame)
        logger.debug("output {}".format(frame, "s"))
        if frames:
            self.send_data_to_bc(frames)

    def start_listener(self):
        listener = RT_Listener()
        listener_thread = threading.Thread(
            target=listener.start_listening)
        listener_thread.start()
        while True:
            if not len(listener.data_received) == 0:
                # threading.Thread(
                #     target=self._handle_incoming_frame,
                #     args=(listener.data_received,)).start()
                logger.debug(listener.data_received[0])
                self._handle_incoming_frame(listener.data_received[0])
                listener.data_received.pop(0)


if __name__ == "__main__":
    rt_listener_thread = threading.Thread(
        target=Remote_Terminal().start_listener)
    rt_listener_thread.start()
