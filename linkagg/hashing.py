from linkagg.frames import Frame, Protocol
from functools import wraps
import time


def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):

        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()

        # print(
        #     '"{}" took {:.3f} ms to execute\n'.format(
        #         my_func.__name__, (tend - tstart) * 1000
        #     )
        # )
        return output, (tend - tstart) * 1000

    return timed


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


@timeit
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
