import pytest
from linkagg_hash import linkagg_hash
from linkagg_hash import __version__
import statistics


def test_version():
    assert __version__ == "0.0.1"


@pytest.fixture
def frames():
    return linkagg_hash.gen_frames(100)


def test_frames(frames):
    assert len(frames) == 100


def test_one_intf(frames):
    num_supported = 256
    num_up_links = 1
    for frame in frames:
        resulting_hash = linkagg_hash.hash_main(frame)
        picked_intf = linkagg_hash.egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        assert picked_intf == 1


def test_link_distribution():
    num_supported = 256
    num_up_links = 64
    num_frames = 10000
    frames = linkagg_hash.gen_frames(num_frames)
    interface_queues = {i: 0 for i in range(1, num_up_links + 1)}
    for frame in frames:
        resulting_hash = linkagg_hash.hash_main(frame)
        picked_interface = linkagg_hash.egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        interface_queues[picked_interface] += 1
    values = [v for k, v in interface_queues.items()]
    print("=" * 50)
    for k, v in interface_queues.items():
        print(f"Interface {k}: {v} frames")
    print("=" * 50)

    # testing to see how "spread out" our values are.
    # this is not a great measurement of uniform distribution, but its
    # good enough for this toy code
    assert 10 < statistics.stdev(values) < 100


def test_hashes_are_deterministic(frames):
    for frame in frames:
        last_hash = linkagg_hash.hash_main(frame)
        for _ in range(10):
            assert linkagg_hash.hash_main(frame) == last_hash
