import sys
import random
import socket
import struct
from enum import Enum
from ipaddress import IPv4Address
from types import MappingProxyType


NUM_SUPPORTED_LINKS = 256


class NoAvailableInterfaces(Exception):
    pass


class Protocol(Enum):
    TCP = 6
    UDP = 17
    ICMP = 1
    OSPF = 89


class Flow:
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
            self.src_mac = "aabbcc000420"
            self.dst_mac = "01005e000005"
            self.src_ip = "10.3.4.4"
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
        return str(self.flow_tuple())

    def __repr__(self):
        return str(self.flow_tuple())

    @staticmethod
    def gen_ip():
        ip_str = socket.inet_ntoa(struct.pack(">I", random.randint(1, 0xFFFFFFFF)))
        return IPv4Address(ip_str)

    @staticmethod
    def gen_mac():
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
        return random.randint(1, 65535)

    @staticmethod
    def gen_proto():
        protos = (1, 6, 17, 89)  # ICMP, TCP, UDP, OSPF respectively
        return Protocol(protos[random.randint(0, 3)])

    def flow_tuple(self):
        return (
            self.src_mac,
            self.dst_mac,
            self.proto.value,
            self.src_ip,
            self.src_port,
            self.dst_ip,
            self.dst_port,
        )


def gen_flows(c):
    return [Flow() for _ in range(c)]


def hash_src_dst_ip(flow: Flow):
    src_ip = flow.src_ip
    dst_ip = flow.dst_ip
    # Take the last four (least significant) bits from src and dst and concatenate
    src_bin = bin(int(src_ip))[-4:]
    dst_bin = bin(int(dst_ip))[-4:]
    hash_bin = src_bin + dst_bin
    # convert to an integer from binary, and lets bump it up by one to start
    # like interface numbering. We don't start with interface 0, we start from 1.
    return int(hash_bin, base=2) + 1


def hash_src_dst_port_proto():
    return random.randint(1, 256)


def hash_src_dst_mac():
    return random.randint(1, 256)


def hash_main(flow):
    if flow.proto == Protocol.ICMP:
        # src_ip,dst_ip
        return hash_src_dst_ip(flow)
    elif flow.proto in [Protocol.TCP, Protocol.UDP]:
        # src_port,dst_port,proto
        return hash_src_dst_port_proto()
    else:
        # src_mac,dst_mac
        return hash_src_dst_mac()


def egress_intf_picker(number_of_up_intfs, max_supported_intfs, hash_value):
    # calculate windows for what hashes go into which egress interface "bucket"
    # short-circuit if no interfaces are up
    if number_of_up_intfs == 0:
        raise NoAvailableInterfaces(
            "There are currently no up egres interfaces in the bundle"
        )
    window_width = max_supported_intfs // number_of_up_intfs
    for i in range(number_of_up_intfs):
        idx = i + 1
        lower = window_width * (idx - 1)
        upper = window_width * idx
        if lower < hash_value <= upper:
            return idx

    # failsafe, we must always pick an interface
    return random.randint(1, number_of_up_intfs)


if __name__ == "__main__":
    num_supported = int(sys.argv[1])
    num_up_links = int(sys.argv[2])
    num_flows = int(sys.argv[3])

    flows = gen_flows(num_flows)
    interface_queues = {i: [] for i in range(1, num_up_links + 1)}
    for flow in flows:
        resulting_hash = hash_main(flow)
        picked_interface = egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        interface_queues[picked_interface].append(flow.flow_tuple())
        # print("-" * 50)
        # print(f"flow: {flow}")
        # print(f"resulting_hash: {resulting_hash}")
        # print(f"picked_interface: {picked_interface}")

    print("=" * 50)
    for k, v in interface_queues.items():
        print(f"Interface {k}: {len(v)} flows")
    print("=" * 50)
