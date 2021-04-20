import logging
logger = logging.getLogger()
from .Message_Layer.ML_Analyzer_RT import MessageLayerAnalyzerRT
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Listener
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Sender
import threading
import time


class Remote_Terminal:

    def __init__(self):
        self.wait_status = True
        self.RT_Sender = RT_Sender()
        self.MessageLayerAnalyzerRT = MessageLayerAnalyzerRT()
        pass

    def send_data_to_bc(self, frames):
        for frame in frames:
            if frame:
                message = frame.encode("utf-8")
                logger.info("RT sending to BC: {}".format(message))
                self.RT_Sender.send_message(message)
                time.sleep(1)
            else:
                continue

    def _handle_incoming_frame(self, frame):
        logger.debug("input {}".format(frame, "s"))
        frames = \
            self.MessageLayerAnalyzerRT.interprete_incoming_frame(frame)
        if frames:
            self.send_data_to_bc(frames)


    def start_listener(self):
        listener = RT_Listener()
        listener_thread = threading.Thread(
            target=listener.start_listening)
        listener_thread.start()
        while True:
            if len(listener.data_received) > 0:
                logger.info("RT receiving from BC: {}".format(listener.data_received[0]))
                self._handle_incoming_frame(listener.data_received[0])
                listener.data_received.pop(0)
            else:
                pass


if __name__ == "__main__":
    rt_listener_thread = threading.Thread(
        target=Remote_Terminal().start_listener)
    rt_listener_thread.start()
