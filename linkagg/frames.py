import random
import socket
import struct
from enum import Enum
from ipaddress import IPv4Address


class NoAvailableInterfaces(Exception):
    pass


# This defines and maps protocol name to protocol number
class Protocol(Enum):
    TCP = 6
    UDP = 17
    ICMP = 1
    OSPF = 89


class Frame:
    """Models an Ethernet frame, with either ICMP, TCP, or UDP packet header"""

    def __init__(self):
        self.proto = self.gen_proto()
        if self.proto in [Protocol.TCP, Protocol.UDP]:  # TCP or UDP
            self.src_mac = self.gen_mac()
            self.dst_mac = self.gen_mac()
            self.src_ip = self.gen_ip()
            self.src_port = self.gen_port()
            self.dst_ip = self.gen_ip()
            self.dst_port = self.gen_port()
        elif self.proto == Protocol.OSPF:  # OSPF
            self.src_mac = self.gen_mac()
            self.dst_mac = "01005e000005"
            self.src_ip = self.gen_ip()
            self.dst_ip = "224.0.0.5"
            self.src_port = None
            self.dst_port = None
        else:  # ICMP
            self.src_mac = self.gen_mac()
            self.dst_mac = self.gen_mac()
            self.src_ip = self.gen_ip()
            self.src_port = None
            self.dst_ip = self.gen_ip()
            self.dst_port = None

    def __str__(self):
        return str(self.frame_tuple())

    def __repr__(self):
        return str(self.frame_tuple())

    @staticmethod
    def gen_ip():
        """Generates a random IP address

        Returns:
            IPv4Address: IPv4 address object
        """
        ip_str = socket.inet_ntoa(struct.pack(">I", random.randint(1, 0xFFFFFFFF)))
        return IPv4Address(ip_str)

    @staticmethod
    def gen_mac():
        """Generates an Ethernet MAC address.

        Returns:
            str: MAC address (e.g. 001122aabbcc)
        """
        return "%02x%02x%02x%02x%02x%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    @staticmethod
    def gen_port():
        """Generate a random port number.

        Returns:
            int: Integer range 1-65535
        """
        return random.randint(1, 65535)

    @staticmethod
    def gen_proto():
        """Generate a random IP protocol number.

        Returns:
            Protocol: Returns a random Protocol Enum
        """
        protos = (1, 6, 17, 89)  # ICMP, TCP, UDP, OSPF respectively
        return Protocol(protos[random.randint(0, 3)])

    def frame_tuple(self):
        """Generate tuple for the frame.

        Returns:
            tuple: Frame tuple e.g. ('e0a1183e26f8', 'e6d1d19b940c', 17,
                                      IPv4Address('122.164.22.239'), 12878,
                                      IPv4Address('20.222.93.187'), 35191)
        """
        return (
            self.src_mac,
            self.dst_mac,
            self.proto.value,
            self.src_ip,
            self.src_port,
            self.dst_ip,
            self.dst_port,
        )
