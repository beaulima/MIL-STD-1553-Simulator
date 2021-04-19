import socket
import threading
import logging
logger = logging.getLogger()


class RT_Sender:

    def __init__(self):
        self.destination_ip = "255.255.255.255"
        self.destination_port = 2000

    def send_message(self, message):
        socket_variable = \
            socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_variable.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        socket_variable.sendto(message, (self.destination_ip, self.destination_port))


class RT_Listener:

    def __init__(self):
        self.port = 2001

    data_received = list()

    def start_listening(self):
        socket_variable = \
            socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_variable.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        socket_variable.bind(("", self.port))
        while True:
            data, addr = socket_variable.recvfrom(1024)
            self.data_received.append(str(data))


if __name__ == "__main__":
    listener = RT_Listener()
    listener_thread = threading.Thread(
        target=listener.start_listening)
    listener_thread.start()
    while True:
        if listener.data_received:
            logger.debug(listener.data_received)
            listener.data_received = ""
