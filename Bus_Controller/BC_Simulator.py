import logging
logger = logging.getLogger()
from .Message_Layer.ML_Encoder_BC import MessageLayerEncoderBC
from .Message_Layer.ML_Decoder_BC import MessageLayerDecoderBC
from .Physical_Layer_Emulation.Communication_Socket_BC import BC_Listener
from .Physical_Layer_Emulation.Communication_Socket_BC import BC_Sender
import threading
import time

from Remote_Terminal.Message_Layer.ML_Analyzer_RT import MessageLayerAnalyzerRT

def clean_frame(frame):
    return str(frame).replace("b\'", "").replace("\'", "")

def convert_to_hex(frame):
    if isinstance(frame, str):
        frame = int(frame, 20)
        return hex(frame)
    elif  isinstance(frame, bytes):
        frame = int(frame, 20)
        return hex(frame)


def convert_to_hex_display_from_RC(frame):
    frame = str(frame).replace("b\'", "").replace("\'", "")
    if frame[0:3] == "100":
        return MessageLayerAnalyzerRT()._deconstruct_command_word(frame), "STATUS"
    elif frame[0:3] == "001":
        return  MessageLayerAnalyzerRT()._deconstruct_data_word(frame), "DATA"
    return None

def convert_to_hex_display_to_RC(frame):
    frame = str(frame).replace("b\'", "").replace("\'", "")
    if frame[0:3] == "100":
        return MessageLayerAnalyzerRT()._deconstruct_command_word(frame), "COMMAND"
    elif frame[0:3] == "001":
        return  MessageLayerAnalyzerRT()._deconstruct_data_word(frame), "DATA"
    return None


class Bus_Controller:

    def __init__(self, sleep=1):
        self.BC_Sender = BC_Sender()
        self.MessageLayerEncoderBC = MessageLayerEncoderBC()
        self.sleep = sleep


    def _send_data(self, frames):
        for frame in frames:
            if frame:
                message = frame.encode("utf-8")
                word, dtype = convert_to_hex_display_to_RC(message)
                long_word = hex(int(frame, 20))
                logger.info("BC sending to RT: {} {} {} ({}) {}".format(message, word, long_word, dtype, self.sleep))
                self.BC_Sender.send_message(message)
                time.sleep(self.sleep)
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
                word, dtype = convert_to_hex_display_from_RC(listener.data_received[0])
                long_word = hex(int(clean_frame(listener.data_received[0]), 20))
                logger.info("BC receiving from RT: {} {}  {} ({})".format(listener.data_received[0], word, long_word, dtype))
                self._handle_incoming_frame(listener.data_received[0])
                listener.data_received.pop(0)

    def send_data_to_rt(self, rt_address, sub_address_or_mode_code, message):
        logger.debug(rt_address)
        frames = self.MessageLayerEncoderBC.send_message_to_RT(rt_address, sub_address_or_mode_code, message)
        self._send_data(frames)

    def receive_data_from_rt(
            self, rt_address, sub_address_or_mode_code, word_count):
        logger.debug(rt_address)
        frames = self.MessageLayerEncoderBC.receive_message_from_RT(rt_address, sub_address_or_mode_code, word_count)
        self._send_data(frames)

if __name__ == "__main__":
    bc_listener_thread = threading.Thread(
        target=Bus_Controller().start_listener)
    bc_listener_thread.start()
