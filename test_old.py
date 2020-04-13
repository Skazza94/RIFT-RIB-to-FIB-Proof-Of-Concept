from rib import Rib

default_prefix = "0.0.0.0/0"
default_next_hops = {'S1', 'S2', 'S3', 'S4'}

first_negative_disagg_prefix = "10.0.0.0/16"
first_negative_disagg_next_hops = {'S1'}

second_negative_disagg_prefix = "10.1.0.0/16"
second_negative_disagg_next_hops = {'S4'}

subnet_disagg_prefix = "10.0.10.0/24"
subnet_disagg_next_hops = {"S2"}

unreachable_prefix = "200.0.0.0/16"
unreachable_next_hops = default_next_hops

leaf_prefix = "20.0.0.0/16"
leaf_prefix_positive_next_hops = {"M4"}
leaf_prefix_negative_next_hops = {"M3"}


# Slide 55
def test_add_default_route():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    assert rib.destinations.get(default_prefix)._positive_next_hops == default_next_hops
    assert rib.destinations.get(default_prefix)._negative_next_hops == set()
    assert rib.destinations.get(default_prefix).get_next_hops == default_next_hops
    assert rib.fib.routes[default_prefix] == default_next_hops


# Slide 56
def test_add_negative_disaggregation():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix)._negative_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops
    assert rib.fib.routes[first_negative_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops


# Slide 57
def test_add_two_negative_disaggregation():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(second_negative_disagg_prefix, second_negative_disagg_next_hops,
                  disagg_type=False)
    assert rib.destinations.get(second_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix)._negative_next_hops == \
           second_negative_disagg_next_hops
    assert rib.destinations.get(second_negative_disagg_prefix).get_next_hops == \
           default_next_hops - second_negative_disagg_next_hops
    assert rib.fib.routes[second_negative_disagg_prefix] == \
           default_next_hops - second_negative_disagg_next_hops


# Slide 58
def test_remove_default_next_hop():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(second_negative_disagg_prefix, second_negative_disagg_next_hops,
                  disagg_type=False)
    failed_next_hop = {"S2"}
    rib.delete_route(default_prefix, failed_next_hop)
    # test for default
    assert rib.destinations.get(
        default_prefix)._positive_next_hops == default_next_hops - failed_next_hop
    assert rib.destinations.get(default_prefix)._negative_next_hops == set()
    assert rib.destinations.get(default_prefix).get_next_hops == default_next_hops - failed_next_hop
    assert rib.fib.routes[default_prefix] == default_next_hops - failed_next_hop
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix)._negative_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops - failed_next_hop
    assert rib.fib.routes[first_negative_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops - failed_next_hop
    # test for 10.1.0.0/16
    assert rib.destinations.get(second_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix)._negative_next_hops == \
           second_negative_disagg_next_hops
    assert rib.destinations.get(second_negative_disagg_prefix).get_next_hops == \
           default_next_hops - second_negative_disagg_next_hops - failed_next_hop
    assert rib.fib.routes[second_negative_disagg_prefix] == \
           default_next_hops - second_negative_disagg_next_hops - failed_next_hop


# Slide 59
def test_add_subnet_disagg_to_first_negative_disagg():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix)._negative_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops
    assert rib.fib.routes[first_negative_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops
    # test for disaggregated subnet
    assert rib.destinations.get(subnet_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix)._negative_next_hops == subnet_disagg_next_hops
    assert rib.destinations.get(subnet_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops - subnet_disagg_next_hops
    assert rib.fib.routes[subnet_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops - subnet_disagg_next_hops


# Slide 60
def test_remove_default_next_hop_with_subnet_disagg():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
    failed_next_hop = {"S3"}
    rib.delete_route(default_prefix, failed_next_hop)
    # test for default
    assert rib.destinations.get(
        default_prefix)._positive_next_hops == default_next_hops - failed_next_hop
    assert rib.destinations.get(default_prefix)._negative_next_hops == set()
    assert rib.destinations.get(default_prefix).get_next_hops == default_next_hops - failed_next_hop
    assert rib.fib.routes[default_prefix] == default_next_hops - failed_next_hop
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix)._negative_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops - failed_next_hop
    assert rib.fib.routes[first_negative_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops - failed_next_hop
    # test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix)._negative_next_hops == \
           subnet_disagg_next_hops
    assert rib.destinations.get(subnet_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops - subnet_disagg_next_hops - \
           failed_next_hop
    assert rib.fib.routes[subnet_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops - subnet_disagg_next_hops - \
           failed_next_hop


# Tests if a route becomes unreachable after all next hops are negatively disaggregated
def test_neg_disagg_fib_unreachable():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(unreachable_prefix, unreachable_next_hops, disagg_type=False)
    assert rib.destinations.get(unreachable_prefix)._positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix)._negative_next_hops == unreachable_next_hops
    assert rib.destinations.get(unreachable_prefix).get_next_hops == set()
    assert rib.fib.routes[unreachable_prefix] == "unreachable"


# Tests if an unreachable route becomes reachable after a negative disaggregation is removed
def test_neg_disagg_fib_unreachable_recover():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(unreachable_prefix, unreachable_next_hops, disagg_type=False)
    recovered_nodes = {"S3"}
    rib.delete_route(unreachable_prefix, recovered_nodes, disagg_type=False)
    assert rib.destinations.get(unreachable_prefix)._positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix)._negative_next_hops == \
           unreachable_next_hops - recovered_nodes
    assert rib.destinations.get(unreachable_prefix).get_next_hops == recovered_nodes
    assert rib.fib.routes[unreachable_prefix] == recovered_nodes


# Tests if a subnet of an unreachable route (negative disaggregated) is removed from the FIB
def test_add_subnet_disagg_recursive_unreachable():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
    unreachable_next_hops = default_next_hops - first_negative_disagg_next_hops
    rib.add_route(first_negative_disagg_prefix, unreachable_next_hops, disagg_type=False)
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(
        first_negative_disagg_prefix)._negative_next_hops == default_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == set()
    assert rib.fib.routes[first_negative_disagg_prefix] == "unreachable"
    assert not rib.destinations.has_key(subnet_disagg_prefix)
    assert subnet_disagg_prefix not in rib.fib.routes


# Slide 60 and recover of the failed next hops
def test_recursive_recover():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
    failed_next_hop = {"S3"}
    rib.delete_route(default_prefix, failed_next_hop)
    rib.add_route(default_prefix, failed_next_hop)
    # test for default
    assert rib.destinations.get(default_prefix)._positive_next_hops == default_next_hops
    assert rib.destinations.get(default_prefix)._negative_next_hops == set()
    assert rib.destinations.get(default_prefix).get_next_hops == default_next_hops
    assert rib.fib.routes[default_prefix] == default_next_hops
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix)._negative_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(first_negative_disagg_prefix).get_next_hops == \
           default_next_hops - first_negative_disagg_next_hops
    assert rib.fib.routes[first_negative_disagg_prefix] == \
           default_next_hops - first_negative_disagg_next_hops
    # test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix)._positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix)._negative_next_hops == subnet_disagg_next_hops
    assert rib.destinations.get(subnet_disagg_prefix).get_next_hops == default_next_hops - \
           first_negative_disagg_next_hops - subnet_disagg_next_hops
    assert rib.fib.routes[subnet_disagg_prefix] == default_next_hops - \
           first_negative_disagg_next_hops - subnet_disagg_next_hops


# Slide 61 from the perspective of L3
def test_pos_neg_disagg():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(leaf_prefix, leaf_prefix_positive_next_hops)
    rib.add_route(leaf_prefix, leaf_prefix_negative_next_hops, disagg_type=False)
    assert rib.destinations.get(leaf_prefix)._positive_next_hops == leaf_prefix_positive_next_hops
    assert rib.destinations.get(leaf_prefix)._negative_next_hops == leaf_prefix_negative_next_hops
    assert rib.destinations.get(leaf_prefix).get_next_hops == leaf_prefix_positive_next_hops
    assert rib.fib.routes[leaf_prefix] == leaf_prefix_positive_next_hops


# Given a prefix X with N negative next hops
# Given a prefix Y, subnet of X, with M negative next hops and a positive next hop L included in N
# Resulting next hops of Y include L
def test_pos_neg_disagg_recursive():
    rib = Rib()
    rib.add_route(default_prefix, default_next_hops)
    rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
    rib.add_route(subnet_disagg_prefix, first_negative_disagg_next_hops)
    assert rib.destinations.get(subnet_disagg_prefix)._positive_next_hops == \
           first_negative_disagg_next_hops
    assert rib.destinations.get(subnet_disagg_prefix)._negative_next_hops == \
           subnet_disagg_next_hops
    assert rib.destinations.get(subnet_disagg_prefix).get_next_hops == \
           default_next_hops - subnet_disagg_next_hops
    assert rib.fib.routes[subnet_disagg_prefix] == default_next_hops - subnet_disagg_next_hops
