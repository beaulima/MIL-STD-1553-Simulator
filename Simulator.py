from Bus_Controller.BC_Simulator import Bus_Controller
from Remote_Terminal.RT_Simulator import Remote_Terminal
import threading
import time
import numpy as np

global bc_listener_thread
global rt_listener_thread

from random import uniform


def weather_cycle(BC, n_cycles, randomv=0.0, sleep=0.1):

    n_cycles = n_cycles

    if np.random.uniform(0.0, 1.0) > randomv:
        if randomv > 0:
            logging.info("--- Bypassing: weather_cycle")
        return
    tmp_sleep = BC.sleep
    BC.sleep = sleep
    while n_cycles > 0:
        rt_address = "01"
        sub_address_or_mode_code = "01"
        word_count = "01"

        for message in ["T0", "P0", "W0"]:
            logging.info("--- BC send_data_to_rt: {} {}".format(rt_address, sub_address_or_mode_code))
            BC.send_data_to_rt(rt_address=rt_address,
                               sub_address_or_mode_code=sub_address_or_mode_code, message=message)
            logging.info("--- BC receive_data_from_rt: {} {}".format(rt_address, sub_address_or_mode_code))
            BC.receive_data_from_rt(rt_address=rt_address,
                                    sub_address_or_mode_code=sub_address_or_mode_code,
                                    word_count=word_count)
            time.sleep(0.1)
        n_cycles -= 1
    BC.sleep = tmp_sleep


def check_cycle(BC, n_cycles, sleep=0.1, do_subcycles=0.0):

    n_cycles = n_cycles
    tmp_sleep = BC.sleep
    BC.sleep = sleep
    while n_cycles > 0:
        for rt_address in ["01", "02", "03"]:
            for sub_address_or_mode_code in ["01", "02", "03", "04"]:
                word_count = "00"
                message=""
                if int(sub_address_or_mode_code) > 2:
                    message = "OK"
                    word_count = "01"
                logging.info("--- BC send_data_to_rt: {} {}".format(rt_address, sub_address_or_mode_code))
                BC.send_data_to_rt(rt_address=rt_address, sub_address_or_mode_code=sub_address_or_mode_code, message=message)
                logging.info("--- BC receive_data_from_rt: {} {}".format(rt_address, sub_address_or_mode_code))
                BC.receive_data_from_rt(rt_address=rt_address, sub_address_or_mode_code=sub_address_or_mode_code,
                                        word_count=word_count)
                time.sleep(0.1)

                weather_cycle(BC, 1, randomv=do_subcycles)
        n_cycles -= 1
    BC.sleep = tmp_sleep

if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(filename)-20s %(module)-20s %(funcName)-30s %(lineno)-5s %(levelname)-8s %(message)s'

    FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
    import logging

    logging.basicConfig(format=FORMAT, level=logging.INFO)

    #random.seed(0)


    try:
        """ Use following threads if you are running all the 
            simulators on the same machine """
        sleep = 0.1
        BC = Bus_Controller(sleep=sleep)
        bc_listener_thread = threading.Thread(
             target=BC.start_listener)
        bc_listener_thread.start()
        RC = Remote_Terminal(sleep=sleep)
        rt_listener_thread = threading.Thread(
             target = RC.start_listener)
        rt_listener_thread.start()

        time.sleep(5)

        bContinue = True

        for sleep in [ 1.0, 0.5, 0.25, 0.1]:
            logging.warning("WARMUP: {}".format(sleep))
            check_cycle(BC, 1, sleep=sleep, do_subcycles=0.0)

        n_main_cycle = 5
        while n_main_cycle > 0:
            logging.warning("WEATHER")
            weather_cycle(BC, 4, randomv=1.0)
            sleep = np.random.uniform(0.09, 0.11)
            logging.warning("CHECK: {}".format(sleep))
            check_cycle(BC, 1, do_subcycles=0.5, sleep=sleep)
            n_main_cycle -= 1

        for sleep in [0.25, 0.5, 1.0]:
            logging.warning("Cooldown: {}".format(sleep))
            check_cycle(BC, 1, sleep=sleep, do_subcycles=1.0)


            #bContinue = False


    except KeyboardInterrupt:
        exit()
