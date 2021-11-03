from linkagg.frames import Frame, Protocol
from functools import wraps
import time
import cython


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
        int: Returns integer between 0 and 255
    """
    cdef long src_ip, dst_ip
    cdef int proto, keep

    src_ip = int(frame.src_ip)
    dst_ip = int(frame.dst_ip)
    proto = frame.proto.value
    keep = 255
    # Convert IPv4Address to int, take XOR and keep only the 8-most least significant bits
    return (src_ip ^ dst_ip ^ proto) & keep


def hash_src_dst_port_proto(frame: Frame):
    """Hash function for source ip, source port, dest ip, dest port, and protocol

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 0 and 255
    """

    cdef long src_ip, dst_ip, src_mac, dst_mac
    cdef int proto, src_port, dst_port, keep

    src_ip = int(frame.src_ip)
    src_port = frame.src_port
    dst_ip = int(frame.dst_ip)
    dst_port = frame.dst_port
    proto = frame.proto.value
    keep = 255
    # Convert IPv4Address to int, take XOR everything and keep only the 8-most least significant bits
    return (
        src_ip
        ^ src_port
        ^ dst_ip
        ^ dst_port
        ^ proto
    ) & keep


def hash_src_dst_mac(frame: Frame):
    """Hash function for source mac address and destination mac address.

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 0 and 255
    """
    cdef long src_mac, dst_mac
    cdef int keep

    src_mac = int(frame.src_mac, 16)
    dst_mac = int(frame.dst_mac, 16)
    keep = 255
    # Convert hex str to int, take XOR and keep only the 8-most least significant bits
    return (src_mac ^ dst_mac) & keep


@timeit
def hash_main(frame):
    """Main hashing parent function. Depending on the higher level packet
    content, will decide which actual hash function will be executed.

    Args:
        frame (Frame): Network Frame object

    Returns:
        int: Returns integer between 0 and 255
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
