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


class Frame:
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

    def frame_tuple(self):
        return (
            self.src_mac,
            self.dst_mac,
            self.proto.value,
            self.src_ip,
            self.src_port,
            self.dst_ip,
            self.dst_port,
        )


def gen_frames(c):
    return [Frame() for _ in range(c)]


def hash_src_dst_ip(frame: Frame):
    """Hash function for source ip and dest ip

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 1 and 256
    """
    src_ip = frame.src_ip
    dst_ip = frame.dst_ip
    # Strip '0b' from the front of these binary representations, and then
    # take the last n (least significant) bits and concatenate
    src_bin = bin(int(src_ip))[2:][-4:]
    dst_bin = bin(int(dst_ip))[2:][-4:]
    hash_bin = src_bin + dst_bin
    # convert to an integer from binary, and lets bump it up by one to start
    # like interface numbering. We don't start with interface 0, we start from 1.
    return int(hash_bin, base=2) + 1


def hash_src_dst_port_proto(frame: Frame):
    """Hash function for source port, dest port, and protocol

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 1 and 256
    """
    src_port = frame.src_port
    dst_port = frame.dst_port
    proto_num = frame.proto.value
    # Strip '0b' from the front of these binary representations, and then
    # take the last n (least significant) bits and concatenate
    bin(int(frame.dst_mac, 16))[2:].zfill(16)
    src_bin = bin(int(src_port))[2:].zfill(10)
    dst_bin = bin(int(dst_port))[2:].zfill(10)
    proto_bin = bin(int(proto_num))[2:].zfill(10)[-4:]
    hash_bin = src_bin + dst_bin + proto_bin
    # convert to an integer from binary, and lets bump it up by one to start
    # like interface numbering. We don't start with interface 0, we start from 1.
    return int(hash_bin, base=2) + 1


def hash_src_dst_mac(frame: Frame):
    """Hash function for source mac address and destination mac address.

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 1 and 256
    """
    # convert to binary, strip '0b', and zero-pad
    src_mac = bin(int(frame.src_mac, 16))[2:].zfill(16)
    dst_mac = bin(int(frame.dst_mac, 16))[2:].zfill(16)
    # take the last n (least significant) bits and concatenate
    src_bin = bin(int(src_mac))[::2][-4:]
    dst_bin = bin(int(dst_mac))[::2][-4:]
    hash_bin = src_bin + dst_bin
    # convert to an integer from binary, and lets bump it up by one to start
    # like interface numbering. We don't start with interface 0, we start from 1.
    return int(hash_bin, base=2) + 1


def hash_main(frame):
    """Main hashing parent function. Depending on the higher level packet
    content, will decide which actual hash function will be executed.

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 1 and 256
    """
    if frame.proto == Protocol.ICMP:
        # src_ip,dst_ip
        return hash_src_dst_ip(frame)
    elif frame.proto in [Protocol.TCP, Protocol.UDP]:
        # src_port,dst_port,proto
        return hash_src_dst_port_proto(frame)
    else:
        # src_mac,dst_mac
        return hash_src_dst_mac(frame)


def egress_intf_picker(number_of_up_intfs, max_supported_intfs, hash_value):
    """Function that uses the resulting frame hash and computes which up
    interface queue the frame will be put in. The system as a whole should then
    map these queues to actual egress interfaces.

    Args:
        number_of_up_intfs (int): Number of operational interfaces in the bundle
        max_supported_intfs (int): Maximum number of interfaces that can be supported in a bundle
        hash_value (int): Resulting frame hash from the hashing process

    Raises:
        NoAvailableInterfaces: If there are no available interfaces in the bundle, just raise an exception

    Returns:
        int: Egress queue to dump the frame into. This will be picked up by an egress interface in the bundle
    """
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
    num_frames = int(sys.argv[3])

    frames = gen_frames(num_frames)
    interface_queues = {i: [] for i in range(1, num_up_links + 1)}

    # Run a lot of frames into the system
    for frame in frames:
        resulting_hash = hash_main(frame)
        picked_interface = egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        interface_queues[picked_interface].append(frame.frame_tuple())
        # print("-" * 50)
        # print(f"frame: {frame}")
        # print(f"resulting_hash: {resulting_hash}")
        # print(f"picked_interface: {picked_interface}")

    # print queues
    print("=" * 50)
    for k, v in interface_queues.items():
        print(f"Interface {k}: {len(v)} frames")
    print("=" * 50)

    # Lets simulate lots of frames for certain flows. This is normal in networking.
    # A flow has thousands of frames...not just one. This will show the
    # behavior of load-balancing flows does not necessarily ensure uniform interface
    # utilization in a bundle. We will set 2 flows to be elephant flows.
    more_frames = []
    for _ in range(2):
        selected_frame = random.choice(frames)
        for _ in range(10000):
            more_frames.append(selected_frame)

    for frame in more_frames:
        resulting_hash = hash_main(frame)
        picked_interface = egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        interface_queues[picked_interface].append(frame.frame_tuple())

    # print queues again
    print("=" * 50)
    for k, v in interface_queues.items():
        print(f"Interface {k}: {len(v)} frames")
    print("=" * 50)
