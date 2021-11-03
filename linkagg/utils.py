import sys
import random
from linkagg.frames import Frame, NoAvailableInterfaces
from linkagg.hashing import hash_main


def gen_frames(c):
    """Frame generator

    Args:
        c (int): Number of frames to generate

    Returns:
        list: List of Frame objects
    """
    return [Frame() for _ in range(c)]


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
            "There are currently no up egress interfaces in the bundle"
        )
    window_width = max_supported_intfs // number_of_up_intfs
    for i in range(number_of_up_intfs):
        idx = i + 1
        lower = window_width * (idx - 1)
        upper = window_width * idx
        if lower <= hash_value < upper:
            return idx
