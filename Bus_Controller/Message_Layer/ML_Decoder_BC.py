import logging
import sys
logger = logging.getLogger()
from .Data_Link_Layer.Data_Link_Layer_Decoder_BC import DataLinkLayerDecoderBC


class MessageLayerDecoderBC:

    def __init__(self):
        self.DataLinkLayerDecoderBC = DataLinkLayerDecoderBC()

    def _deconstruct_status_word(self, recd_status_frame):
        logger.debug(recd_status_frame)
        recd_status_word = self.DataLinkLayerDecoderBC.decode_status_word(recd_status_frame)

        return recd_status_word

    def _deconstruct_data_word(self, receive_data_frame):
        logger.debug(receive_data_frame)
        recd_data_word = self.DataLinkLayerDecoderBC.decode_data_word(receive_data_frame)
        return recd_data_word

    def interprete_incoming_frame(self, received_frame):

        # Workaroud (maybe not necessary)
        if sys.version_info.major > 2:
            received_frame = received_frame.replace("b\'", "").replace("\'", "")
        logger.debug(received_frame)
        if received_frame[0:3] == "100":
            status_word = self._deconstruct_status_word(received_frame)
            logger.debug("BC incoming STATUS".format(received_frame))
            return status_word
        elif received_frame[0:3] == "001":
            received_frame = received_frame.encode("utf-8")
            data_word = self._deconstruct_data_word(received_frame)
            if sys.version_info.major > 2:
                data_word_dc = bytes.fromhex(data_word).decode('ascii')
            else:
                data_word_dc = data_word.decode("hex")
            logger.debug("BC incoming DATA".format(data_word_dc))
        else:
            raise Exception("Bad received frame frame")

        return data_word_dc
