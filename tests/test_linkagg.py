import pytest
from linkagg_hash import linkagg_hash
from linkagg_hash import __version__
import statistics


def test_version():
    assert __version__ == "0.0.1"


@pytest.fixture
def flows():
    return linkagg_hash.gen_flows(10)


def test_flows(flows):
    assert len(flows) == 10


def test_one_intf(flows):
    num_supported = 256
    num_up_links = 1
    for flow in flows:
        resulting_hash = linkagg_hash.hash_main(flow)
        picked_intf = linkagg_hash.egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        assert picked_intf == 1


def test_link_distribution():
    num_supported = 256
    num_up_links = 64
    num_flows = 10000
    flows = linkagg_hash.gen_flows(num_flows)
    interface_queues = {i: 0 for i in range(1, num_up_links + 1)}
    for flow in flows:
        resulting_hash = linkagg_hash.hash_main(flow)
        picked_interface = linkagg_hash.egress_intf_picker(
            num_up_links, num_supported, resulting_hash
        )
        interface_queues[picked_interface] += 1
    values = [v for k, v in interface_queues.items()]
    # testing to see how "spread out" our values are.
    # this is not a great measurement of uniform distribution, but its
    # good enough for this toy code
    assert statistics.stdev(values) > 10
