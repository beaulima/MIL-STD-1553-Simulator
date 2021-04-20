import logging
logger = logging.getLogger()
import sys
from .Data_Link_Layer.Data_Link_Layer_Decoder_RT import DataLinkLayerDecoderRT
from .Data_Link_Layer.Data_Link_Layer_Encoder_RT import DataLinkLayerEncoderRT


LOOKUP_MEMORY_RT1 = {"01": "AA", "02": "AB", "03": "AC", "04": "AD",
                     "05": "AE", "06": "AF", "07": "AG", "08": "AH",
                     "09": "AI", "0A": "AJ", "0B": "AK", "0C": "AL",
                     "0D": "AM", "0E": "AN", "0F": "AO", "10": "AP",
                     "11": "AQ", "12": "AR", "13": "AS", "14": "AT",
                     "15": "AU", "16": "AV", "17": "AW", "18": "AX",
                     "19": "AY", "1A": "AZ", "1B": "BA", "1C": "BB",
                     "1D": "BC", "1E": "BD", "1F": "BE"}


LOOKUP_MEMORY_RT2 = {"01": "BC", "02": "BD", "03": "BE", "04": "BB",
                     "05": "AY", "06": "AZ", "07": "BA", "08": "AX",
                     "09": "AU", "0A": "AV", "0B": "AW", "0C": "AT",
                     "0D": "AQ", "0E": "AR", "0F": "AS", "10": "AP",
                     "11": "AM", "12": "AN", "13": "AO", "14": "AL",
                     "15": "AI", "16": "AJ", "17": "AK", "18": "AH",
                     "19": "AE", "1A": "AF", "1B": "AG", "1C": "AD",
                     "1D": "AA", "1E": "AB", "1F": "AC"}


LOOKUP_MEMORY_RT3 = {"01": "AD", "02": "AC", "03": "AB", "04": "AA",
                     "05": "AH", "06": "AG", "07": "AF", "08": "AE",
                     "09": "AL", "0A": "AK", "0B": "AJ", "0C": "AI",
                     "0D": "AP", "0E": "AO", "AR": "AO", "10": "AQ",
                     "11": "AQ", "12": "AR", "13": "AS", "14": "AT",
                     "15": "AX", "16": "AW", "17": "AW", "18": "AX",
                     "19": "BB", "1A": "BA", "1B": "AZ", "1C": "AY",
                     "1D": "BE", "1E": "BD", "1F": "BC"}

LOOKUP_MEMORY_RTS = {"01": LOOKUP_MEMORY_RT1, "02": LOOKUP_MEMORY_RT2, "03": LOOKUP_MEMORY_RT2}

class MessageLayerAnalyzerRT:

    def __init__(self):
        self.DataLinkLayerDecoderRT = DataLinkLayerDecoderRT()
        self.DataLinkLayerEncoderRT = DataLinkLayerEncoderRT()

    def _construct_data_word(self, data_wd_part):
        data_part_frame = \
            self.DataLinkLayerEncoderRT.build_data_word(data_wd_part)
        # future implementation of checksum here
        return data_part_frame

    def _deconstruct_command_word(self, recd_command_frame):
        recd_command_word = \
            self.DataLinkLayerDecoderRT.decode_cmd_word(recd_command_frame)
        return recd_command_word

    def _deconstruct_data_word(self, recd_data_frame):
        recd_data_word = \
            self.DataLinkLayerDecoderRT.decode_data_word(recd_data_frame)
        return recd_data_word

    def _construct_status_word(self, rt_address):
        status_word_frame = \
            self.DataLinkLayerEncoderRT.build_status_word(rt_address)
        return status_word_frame

    def _analyze_command_word(self, cmd_word):
        rt_address = cmd_word[0:2]
        if rt_address in LOOKUP_MEMORY_RTS.keys():
            lookup_memory = LOOKUP_MEMORY_RTS[rt_address]
            tr_bit = cmd_word[2]
            if tr_bit == "R":
                return [self._construct_status_word(rt_address)]
            elif tr_bit == "T":
                communication_frames = list()
                communication_frames.append(
                    self._construct_status_word(rt_address))
                data_count = int(cmd_word[-2:], 16)
                for i in range(data_count):
                    if sys.version_info.major > 2:
                        word = lookup_memory["{0:02x}".format(int(cmd_word[3:5], 16) + i)].encode("utf-8").hex()
                    else:
                        word = lookup_memory["{0:02x}".format(int(cmd_word[3:5], 16)+i)].encode("hex")
                    communication_frames.append(
                        self._construct_data_word(word))
                return communication_frames
        else:
            return 0

    def interprete_incoming_frame(self, incoming_frame):

        if sys.version_info.major > 2:
            incoming_frame=incoming_frame.replace("b\'", "").replace("\'", "")
        if incoming_frame[0:3] == "100":
            logger.info("RT incoming COMMAND".format(incoming_frame))
            command_word = self._deconstruct_command_word(incoming_frame)
            return self._analyze_command_word(command_word)
        elif incoming_frame[0:3] == "001":
            logger.info("RT incoming DATA".format(incoming_frame))
            data_word = self._deconstruct_data_word(incoming_frame)
            if sys.version_info.major > 2:
                logger.debug(bytes.fromhex(data_word).decode('utf-8'))
            else:
                logger.debug(data_word.decode("hex"))
        else:
            raise Exception("Bad incoming frame")
