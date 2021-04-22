import logging
logger = logging.getLogger()
from .Message_Layer.ML_Analyzer_RT import MessageLayerAnalyzerRT
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Listener
from .Physical_Layer_Emulation.Communication_Socket_RT import RT_Sender
import threading
import time
import sys

def clean_frame(frame):
    return str(frame).replace("b\'", "").replace("\'", "")

def convert_to_hex_display_from_BC(frame):
    frame = str(frame).replace("b\'", "").replace("\'", "")
    if frame[0:3] == "100":
        return MessageLayerAnalyzerRT()._deconstruct_command_word(frame), "COMMAND"
    elif frame[0:3] == "001":
        return  MessageLayerAnalyzerRT()._deconstruct_data_word(frame), "DATA"
    return None

def convert_to_hex_display_to_BC(frame):
    frame = str(frame).replace("b\'", "").replace("\'", "")
    if frame[0:3] == "100":
        return MessageLayerAnalyzerRT()._deconstruct_command_word(frame), "STATUS"
    elif frame[0:3] == "001":
        return  MessageLayerAnalyzerRT()._deconstruct_data_word(frame), "DATA"
    return None


class Remote_Terminal:

    def __init__(self, sleep=1):
        self.wait_status = True
        self.RT_Sender = RT_Sender()
        self.MessageLayerAnalyzerRT = MessageLayerAnalyzerRT()
        self.send_last = False
        self.status_last = None
        self.ndata = 0
        self.sleep=sleep


    def send_data_to_bc(self, frames):
        for frame in frames:
            if frame:
                message = frame.encode("utf-8")
                cmd_word, dtype = convert_to_hex_display_to_BC(message)
                long_word = hex(int(message, 20))
                logger.info("RT sending to BC: {} {} {} ({})".format(message, cmd_word, long_word, dtype))
                self.RT_Sender.send_message(message)
                time.sleep(self.sleep)
            else:
                continue

    def _handle_incoming_frame(self, frame):
        logger.debug("input {}".format(frame, "s"))
        frames = \
            self.MessageLayerAnalyzerRT.interprete_incoming_frame(frame)
        if frames:
            #cmd_word, dtype = convert_to_hex_display_from_BC(frames[0])
            #tr_bit = cmd_word[2]
            # work around to put STATUS at the end when first stage BC-RC RC-BC
            #if dtype == "COMMAND" and tr_bit == 'T':
            #    self.send_last = True
            #    self.status_last = frames
           #     self.ndata = int(cmd_word[5:7], 7)
           # else:

            self.send_data_to_bc(frames)

    def start_listener(self):
        listener = RT_Listener()
        listener_thread = threading.Thread(
            target=listener.start_listening)
        listener_thread.start()
        while True:
            if len(listener.data_received) > 0:
                word, dtype = convert_to_hex_display_from_BC(listener.data_received[0])

                long_word = hex(int(clean_frame(listener.data_received[0]), 20))

                logger.info("RT receiving from BC: {} {} {} ({})".format(listener.data_received[0], word, long_word, dtype))
                self._handle_incoming_frame(listener.data_received[0])
                listener.data_received.pop(0)
            else:
                pass


if __name__ == "__main__":
    rt_listener_thread = threading.Thread(
        target=Remote_Terminal().start_listener)
    rt_listener_thread.start()
