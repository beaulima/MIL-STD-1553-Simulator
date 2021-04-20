import logging
logger = logging.getLogger()
from .Message_Layer.ML_Encoder_BC import MessageLayerEncoderBC
from .Message_Layer.ML_Decoder_BC import MessageLayerDecoderBC
from .Physical_Layer_Emulation.Communication_Socket_BC import BC_Listener
from .Physical_Layer_Emulation.Communication_Socket_BC import BC_Sender
import threading
import time


class Bus_Controller:

    def __init__(self):
        self.BC_Sender = BC_Sender()
        self.MessageLayerEncoderBC = MessageLayerEncoderBC()
        pass

    def _send_data(self, frames):
        for frame in frames:
            if frame:
                message = frame.encode("utf-8")
                logger.info("BC sending to RT: {}".format(message))
                self.BC_Sender.send_message(message)
                time.sleep(1)
            else:
                continue

    def _handle_incoming_frame(self, frame):
        decoded_frame = MessageLayerDecoderBC().interprete_incoming_frame(frame)
        logger.debug(decoded_frame)

    def start_listener(self):
        listener = BC_Listener()
        listener_thread = threading.Thread(target=listener.start_listening)
        listener_thread.start()
        while True:
            if len(listener.data_received) > 0:
                logger.info("BC receiving from RT: {}".format(listener.data_received[0]))
                self._handle_incoming_frame(listener.data_received[0])
                listener.data_received.pop(0)

    def send_data_to_rt(self, rt_address, sub_address_or_mode_code, message):
        logger.debug(rt_address)
        frames = self.MessageLayerEncoderBC.send_message_to_RT(rt_address, sub_address_or_mode_code, message)
        self._send_data(frames)

    def receive_data_from_rt(
            self, rt_address, sub_address_or_mode_code, word_count):
        logger.debug(rt_address)
        frames = self.MessageLayerEncoderBC.receive_message_from_RT(
            rt_address, sub_address_or_mode_code, word_count)
        self._send_data(frames)


if __name__ == "__main__":
    bc_listener_thread = threading.Thread(
        target=Bus_Controller().start_listener)
    bc_listener_thread.start()
