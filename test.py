from rib import Rib
from rib_route import RibRoute

N_SPF = 1
S_SPF = 2

default_prefix = "0.0.0.0/0"
default_next_hops = ['S1', 'S2', 'S3', 'S4']

first_negative_disagg_prefix = "10.0.0.0/16"
first_negative_disagg_next_hops = ['S1']

second_negative_disagg_prefix = "10.1.0.0/16"
second_negative_disagg_next_hops = ['S4']

subnet_disagg_prefix = "10.0.10.0/24"
subnet_negative_disagg_next_hops = ['S2']

unreachable_prefix = "200.0.0.0/16"
unreachable_negative_next_hops = ['S1', 'S2', 'S3', 'S4']

leaf_prefix = "20.0.0.0/16"
leaf_prefix_positive_next_hops = ["M4"]
leaf_prefix_negative_next_hops = ["M3"]


# Slide 55
def test_add_default_route():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    assert rib.destinations.get(default_prefix).best_route == default_route
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route.next_hops


# Slide 56
def test_add_negative_disaggregation():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    neg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(neg_route)
    assert rib.destinations.get(first_negative_disagg_prefix).best_route == neg_route
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3', 'S4'}
    assert rib.fib.routes[first_negative_disagg_prefix].next_hops == neg_route.next_hops
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == neg_route.next_hops


# Slide 57
def test_add_two_negative_disaggregation():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    second_disagg_route = RibRoute(second_negative_disagg_prefix, S_SPF, [], second_negative_disagg_next_hops)
    rib.put_route(second_disagg_route)
    assert rib.destinations.get(second_negative_disagg_prefix).best_route == second_disagg_route
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.next_hops == {'S1', 'S2', 'S3'}
    assert rib.fib.routes[second_negative_disagg_prefix].next_hops == second_disagg_route.next_hops
    assert rib.fib.kernel.routes[second_negative_disagg_prefix] == second_disagg_route.next_hops


# Slide 58
def test_remove_default_next_hop():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    second_disagg_route = RibRoute(second_negative_disagg_prefix, S_SPF, [], second_negative_disagg_next_hops)
    rib.put_route(second_disagg_route)
    default_route_fail = RibRoute(default_prefix, S_SPF, ['S1', 'S3', 'S4'])
    rib.put_route(default_route_fail)
    # Test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_fail
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route_fail.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route_fail.next_hops
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_disagg_route.next_hops
    # Test for 10.1.0.0/16
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.next_hops == {'S1', 'S3'}
    assert rib.fib.kernel.routes[second_negative_disagg_prefix] == second_disagg_route.next_hops


# Slide 59
def test_add_subnet_disagg_to_first_negative_disagg():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == subnet_disagg_route.next_hops
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops


# Slide 60
def test_remove_default_next_hop_with_subnet_disagg():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    default_route_fail = RibRoute(default_prefix, S_SPF, ['S1', 'S2', 'S4'])
    rib.put_route(default_route_fail)
    # Test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_fail
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route_fail.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route_fail.next_hops
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_disagg_route.next_hops
    # Test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S4'}
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops


# Slide 60 and recover of the failed next hops
def test_recover_default_next_hop_with_subnet_disagg():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    default_route_fail = RibRoute(default_prefix, S_SPF, ['S1', 'S2', 'S4'])
    rib.put_route(default_route_fail)
    default_route_recover = RibRoute(default_prefix, S_SPF, ['S1', 'S2', 'S3', 'S4'])
    rib.put_route(default_route_recover)
    # Test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_recover
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route_recover.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route_recover.next_hops
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3', 'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_disagg_route.next_hops
    # Test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops


def test_remove_default_route():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    rib.del_route(default_prefix, S_SPF)
    # Test for default
    assert not rib.destinations.has_key(default_prefix)
    assert default_prefix not in rib.fib.routes
    assert default_prefix not in rib.fib.kernel.routes
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).parent_prefix_dest is None
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == set()
    assert rib.fib.routes[first_negative_disagg_prefix].next_hops == set()
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == "unreachable"
    # Test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == set()
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == set()
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == "unreachable"


# Tests if a route becomes unreachable after all next hops are negatively disaggregated
def test_neg_disagg_fib_unreachable():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    unreachable_route = RibRoute(unreachable_prefix, S_SPF, [], unreachable_negative_next_hops)
    rib.put_route(unreachable_route)
    assert rib.destinations.get(unreachable_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(unreachable_prefix).best_route.next_hops == set()
    assert rib.fib.routes[unreachable_prefix].next_hops == unreachable_route.next_hops
    assert rib.fib.kernel.routes[unreachable_prefix] == "unreachable"


# Tests if an unreachable route becomes reachable after a negative disaggregation is removed
def test_neg_disagg_fib_unreachable_recover():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    unreachable_route = RibRoute(unreachable_prefix, S_SPF, [], unreachable_negative_next_hops)
    rib.put_route(unreachable_route)
    unreachable_route_recover = RibRoute(unreachable_prefix, S_SPF, [], ['S1', 'S2', 'S4'])
    rib.put_route(unreachable_route_recover)
    assert rib.destinations.get(unreachable_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S4'}
    assert rib.destinations.get(unreachable_prefix).best_route.next_hops == {'S3'}
    assert rib.fib.routes[unreachable_prefix].next_hops == unreachable_route_recover.next_hops
    assert rib.fib.kernel.routes[unreachable_prefix] == {'S3'}


# Tests if a subnet of an unreachable route (negative disaggregated) is removed from the FIB
def test_add_subnet_disagg_recursive_unreachable():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    first_neg_unreach = RibRoute(first_negative_disagg_prefix, S_SPF, [], unreachable_negative_next_hops)
    rib.put_route(first_neg_unreach)
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == set()
    assert rib.fib.routes[first_negative_disagg_prefix].next_hops == first_neg_unreach.next_hops
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == "unreachable"
    assert not rib.destinations.has_key(subnet_disagg_prefix)
    assert subnet_disagg_prefix not in rib.fib.routes


# Slide 61 from the perspective of L3
def test_pos_neg_disagg():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    leaf_route = RibRoute(leaf_prefix, S_SPF, leaf_prefix_positive_next_hops, leaf_prefix_negative_next_hops)
    rib.put_route(leaf_route)
    assert rib.destinations.get(leaf_prefix).best_route.positive_next_hops == {"M4"}
    assert rib.destinations.get(leaf_prefix).best_route.negative_next_hops == {"M3"}
    assert rib.destinations.get(leaf_prefix).best_route.next_hops == {"S4", "S3", "M4", "S2", "S1"}
    assert rib.fib.routes[leaf_prefix].next_hops == leaf_route.next_hops
    assert rib.fib.kernel.routes[leaf_prefix] == {"S4", "S3", "M4", "S2", "S1"}


# Given a prefix X with N negative next hops
# Given a prefix Y, subnet of X, with M negative next hops and a positive next hop L included in N
# Results that next hops of Y include L
def test_pos_neg_disagg_recursive():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, ["S1"], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == {"S1"}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {"S2"}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {"S1", "S3", "S4"}
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == subnet_disagg_route.next_hops
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == {"S1", "S3", "S4"}


# Add two destination with different owner to the same destination, test that the S_SPF route is preferred
def test_add_two_route_same_destination():
    rib = Rib()
    default_route = RibRoute(default_prefix, N_SPF, default_next_hops)
    rib.put_route(default_route)
    best_default_route = RibRoute(default_prefix, S_SPF, ['S1'])
    rib.put_route(best_default_route)
    assert rib.destinations.get(default_prefix).best_route == best_default_route
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1'}
    assert rib.fib.routes[default_prefix].next_hops == best_default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == best_default_route.next_hops


# Add two destination with different owner to the same destination, then remove the best route (S_SPF),
# test that the S_SPF is now preferred
def test_remove_best_route():
    rib = Rib()
    default_route = RibRoute(default_prefix, N_SPF, default_next_hops)
    rib.put_route(default_route)
    best_default_route = RibRoute(default_prefix, S_SPF, ['S1'])
    rib.put_route(best_default_route)
    rib.del_route(default_prefix, S_SPF)
    assert rib.destinations.get(default_prefix).best_route == default_route
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route.next_hops


# Add two destination with different owner to the same destination, test that the S_SPF route is preferred.
# Then add subnet destination and check that they inherits the preferred one
def test_add_two_route_same_destination_with_subnet():
    rib = Rib()
    default_route = RibRoute(default_prefix, N_SPF, default_next_hops)
    rib.put_route(default_route)
    best_default_route = RibRoute(default_prefix, S_SPF, ["S1", "S2", "S3"])
    rib.put_route(best_default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    # Test for default
    assert rib.destinations.get(default_prefix).best_route == best_default_route
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S3'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3'}
    assert rib.fib.routes[default_prefix].next_hops == best_default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == best_default_route.next_hops
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route == first_disagg_route
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3'}
    assert rib.fib.routes[first_negative_disagg_prefix].next_hops == first_disagg_route.next_hops
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_disagg_route.next_hops
    # Test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route == subnet_disagg_route
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3'}
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == subnet_disagg_route.next_hops
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops


# Add two destination with different owner to the default destination, check that the S_SPF route is preferred.
# Then add subnet destination and check that they inherits the preferred one
# Delete the best route from the default and check that the subnets changes consequently
def test_add_two_route_same_destination_with_subnet_and_remove_one():
    rib = Rib()
    default_route = RibRoute(default_prefix, N_SPF, default_next_hops)
    rib.put_route(default_route)
    best_default_route = RibRoute(default_prefix, S_SPF, ["S1", "S2", "S3"])
    rib.put_route(best_default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    rib.del_route(default_prefix, S_SPF)
    # Test for default
    assert rib.destinations.get(default_prefix).best_route == default_route
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix].next_hops == default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == default_route.next_hops
    # Test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route == first_disagg_route
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3', 'S4'}
    assert rib.fib.routes[first_negative_disagg_prefix].next_hops == first_disagg_route.next_hops
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_disagg_route.next_hops
    # Test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route == subnet_disagg_route
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == subnet_disagg_route.next_hops
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops


# Test that a subnet that becomes equal to its parent destination is removed
def test_remove_superfluous_subnet():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    rib.del_route(subnet_disagg_prefix, S_SPF)
    assert not rib.destinations.has_key(subnet_disagg_prefix)
    assert subnet_disagg_prefix not in rib.fib.routes
    assert subnet_disagg_prefix not in rib.fib.kernel.routes


# Test that a subnet X that becomes equal to its parent destination is removed and that its child subnet Y changes
# the parent destination to the one of X
def test_remove_superfluous_subnet_recursive():
    rib = Rib()
    default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
    rib.put_route(default_route)
    first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
    rib.put_route(first_disagg_route)
    subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    rib.del_route(first_negative_disagg_prefix, S_SPF)
    assert not rib.destinations.has_key(first_negative_disagg_prefix)
    assert first_negative_disagg_prefix not in rib.fib.routes
    assert first_negative_disagg_prefix not in rib.fib.kernel.routes
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S1', 'S3', 'S4'}
    assert rib.fib.routes[subnet_disagg_prefix].next_hops == subnet_disagg_route.next_hops
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_disagg_route.next_hops
    assert rib.destinations.get(subnet_disagg_prefix).parent_prefix_dest == rib.destinations.get(default_prefix)


def test_prop_deep_nesting():
    # Deep nesting of more specific routes: parent, child, grand child, grand-grand child, ...
    rib = Rib()
    # Default route
    new_default_next_hops = ['S1', 'S2', 'S3', 'S4', 'S5']
    new_default_route = RibRoute(default_prefix, S_SPF, new_default_next_hops)
    rib.put_route(new_default_route)
    # Child route
    child_prefix = '1.0.0.0/8'
    child_route = RibRoute(child_prefix, S_SPF, [], ['S1'])
    rib.put_route(child_route)
    # Grand child route
    g_child_prefix = '1.128.0.0/9'
    g_child_route = RibRoute(g_child_prefix, S_SPF, [], ['S2'])
    rib.put_route(g_child_route)
    # Grand-grand child route
    gg_child_prefix = '1.192.0.0/10'
    gg_child_route = RibRoute(gg_child_prefix, S_SPF, [], ['S3'])
    rib.put_route(gg_child_route)
    # Grand-grand-grand child route
    ggg_child_prefix = '1.224.0.0/11'
    ggg_child_route = RibRoute(ggg_child_prefix, S_SPF, [], ['S4'])
    rib.put_route(ggg_child_route)
    # Grand-grand-grand-grand child route
    gggg_child_prefix = '1.240.0.0/12'
    gggg_child_route = RibRoute(gggg_child_prefix, S_SPF, [], ['S5'])
    rib.put_route(gggg_child_route)

    # Default route asserts
    assert rib.destinations.get(default_prefix).best_route == new_default_route
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4', 'S5'}
    assert rib.fib.routes[default_prefix].next_hops == new_default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == new_default_route.next_hops
    # Child route asserts
    assert rib.destinations.get(child_prefix).best_route == child_route
    assert rib.destinations.get(child_prefix).best_route.next_hops == {'S2', 'S3', 'S4', 'S5'}
    assert rib.fib.routes[child_prefix].next_hops == child_route.next_hops
    assert rib.fib.kernel.routes[child_prefix] == child_route.next_hops
    # Grand-child route asserts
    assert rib.destinations.get(g_child_prefix).best_route == g_child_route
    assert rib.destinations.get(g_child_prefix).best_route.next_hops == {'S3', 'S4', 'S5'}
    assert rib.fib.routes[g_child_prefix].next_hops == g_child_route.next_hops
    assert rib.fib.kernel.routes[g_child_prefix] == g_child_route.next_hops
    # Grand-grand child route asserts
    assert rib.destinations.get(gg_child_prefix).best_route == gg_child_route
    assert rib.destinations.get(gg_child_prefix).best_route.next_hops == {'S4', 'S5'}
    assert rib.fib.routes[gg_child_prefix].next_hops == gg_child_route.next_hops
    assert rib.fib.kernel.routes[gg_child_prefix] == gg_child_route.next_hops
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == {'S5'}
    assert rib.fib.routes[ggg_child_prefix].next_hops == ggg_child_route.next_hops
    assert rib.fib.kernel.routes[ggg_child_prefix] == ggg_child_route.next_hops
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == gggg_child_route.next_hops
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    # Delete S3 from default route
    new_default_route = RibRoute(default_prefix, S_SPF, ['S1', 'S2', 'S4', 'S5'])
    rib.put_route(new_default_route)

    # Default route asserts
    assert rib.destinations.get(default_prefix).best_route == new_default_route
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S4', 'S5'}
    assert rib.fib.routes[default_prefix].next_hops == new_default_route.next_hops
    assert rib.fib.kernel.routes[default_prefix] == new_default_route.next_hops
    # Child route asserts
    assert rib.destinations.get(child_prefix).best_route == child_route
    assert rib.destinations.get(child_prefix).best_route.next_hops == {'S2', 'S4', 'S5'}
    assert rib.fib.routes[child_prefix].next_hops == child_route.next_hops
    assert rib.fib.kernel.routes[child_prefix] == child_route.next_hops
    # Grand-child route asserts
    assert rib.destinations.get(g_child_prefix).best_route == g_child_route
    assert rib.destinations.get(g_child_prefix).best_route.next_hops == {'S4', 'S5'}
    assert rib.fib.routes[g_child_prefix].next_hops == g_child_route.next_hops
    assert rib.fib.kernel.routes[g_child_prefix] == g_child_route.next_hops
    # Grand-grand child route asserts
    assert rib.destinations.get(gg_child_prefix).best_route == gg_child_route
    assert rib.destinations.get(gg_child_prefix).best_route.next_hops == {'S4', 'S5'}
    assert rib.fib.routes[gg_child_prefix].next_hops == gg_child_route.next_hops
    assert rib.fib.kernel.routes[gg_child_prefix] == gg_child_route.next_hops
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == {'S5'}
    assert rib.fib.routes[ggg_child_prefix].next_hops == ggg_child_route.next_hops
    assert rib.fib.kernel.routes[ggg_child_prefix] == ggg_child_route.next_hops
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == gggg_child_route.next_hops
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(default_prefix, S_SPF)
    # Default route asserts
    assert not rib.destinations.has_key(default_prefix)
    # Child route asserts
    assert rib.destinations.get(child_prefix).best_route == child_route
    assert rib.destinations.get(child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[child_prefix] == 'unreachable'
    # Grand-child route asserts
    assert rib.destinations.get(g_child_prefix).best_route == g_child_route
    assert rib.destinations.get(g_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[g_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[g_child_prefix] == 'unreachable'
    # Grand-grand child route asserts
    assert rib.destinations.get(gg_child_prefix).best_route == gg_child_route
    assert rib.destinations.get(gg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gg_child_prefix].next_hops ==  set()
    assert rib.fib.kernel.routes[gg_child_prefix] == 'unreachable'
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[ggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[ggg_child_prefix] == 'unreachable'
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(child_prefix, S_SPF)
    # Child route asserts
    assert not rib.destinations.has_key(child_prefix)
    # Grand-child route asserts
    assert rib.destinations.get(g_child_prefix).best_route == g_child_route
    assert rib.destinations.get(g_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[g_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[g_child_prefix] == 'unreachable'
    # Grand-grand child route asserts
    assert rib.destinations.get(gg_child_prefix).best_route == gg_child_route
    assert rib.destinations.get(gg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gg_child_prefix].next_hops ==  set()
    assert rib.fib.kernel.routes[gg_child_prefix] == 'unreachable'
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[ggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[ggg_child_prefix] == 'unreachable'
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(g_child_prefix, S_SPF)
    # Grand-child route asserts
    assert not rib.destinations.has_key(g_child_prefix)
    # Grand-grand child route asserts
    assert rib.destinations.get(gg_child_prefix).best_route == gg_child_route
    assert rib.destinations.get(gg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gg_child_prefix].next_hops ==  set()
    assert rib.fib.kernel.routes[gg_child_prefix] == 'unreachable'
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[ggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[ggg_child_prefix] == 'unreachable'
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(gg_child_prefix, S_SPF)
    # Grand-child route asserts
    assert not rib.destinations.has_key(gg_child_prefix)
    # Grand-grand-grand child route asserts
    assert rib.destinations.get(ggg_child_prefix).best_route == ggg_child_route
    assert rib.destinations.get(ggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[ggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[ggg_child_prefix] == 'unreachable'
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(ggg_child_prefix, S_SPF)
    # Grand-child route asserts
    assert not rib.destinations.has_key(ggg_child_prefix)
    # Grand-grand-grand-grand child route asserts
    assert rib.destinations.get(gggg_child_prefix).best_route == gggg_child_route
    assert rib.destinations.get(gggg_child_prefix).best_route.next_hops == set()
    assert rib.fib.routes[gggg_child_prefix].next_hops == set()
    assert rib.fib.kernel.routes[gggg_child_prefix] == 'unreachable'

    rib.del_route(gggg_child_prefix, S_SPF)
    # Grand-grand-grand-grand child route asserts
    assert not rib.destinations.has_key(gggg_child_prefix)

    assert not rib.destinations.keys()
    assert not rib.fib.routes.keys()
    assert not rib.fib.kernel.routes.keys()

def test_prop_nesting_with_siblings():

    # Deep nesting of more specific routes using the following tree:
    #
    #   1.0.0.0/8 -> S1, S2, S3, S4, S5, S6, S7
    #    |
    #    +--- 1.1.0.0/16 -> ~S1
    #    |     |
    #    |     +--- 1.1.1.0/24 -> ~S2
    #    |     |
    #    |     +--- 1.1.2.0/24 -> ~S3
    #    |
    #    +--- 1.2.0.0/16 -> ~S4
    #          |
    #          +--- 1.2.1.0/24 -> ~S5
    #          |
    #          +--- 1.2.2.0/24 -> ~S6
    #
    # Note: we add the routes in a random order

    rib = Rib()

    rib.put_route(RibRoute("1.2.1.0/24", S_SPF, [], ["S5"]))
    rib.put_route(RibRoute("1.1.2.0/24", S_SPF, [], ["S3"]))
    rib.put_route(RibRoute("1.1.0.0/16", S_SPF, [], ['S1']))
    rib.put_route(RibRoute("1.1.1.0/24", S_SPF, [], ['S2']))
    rib.put_route(RibRoute("1.2.0.0/16", S_SPF, [], ['S4']))
    rib.put_route(RibRoute("1.0.0.0/8", S_SPF, ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7']))
    rib.put_route(RibRoute("1.2.2.0/24", S_SPF, [], ['S6']))

    # Testing only rib, fib and kernel next hops
    assert rib.destinations.get('1.0.0.0/8').best_route.next_hops == {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.0.0.0/8'].next_hops == {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.0.0.0/8'] == {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.1.0.0/16').best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get('1.1.0.0/16').best_route.next_hops == {'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.0.0/16'].next_hops == {'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.0.0/16'] == {'S2', 'S3', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.1.1.0/24').best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get('1.1.1.0/24').best_route.next_hops == {'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.1.0/24'].next_hops == {'S3', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.1.0/24'] == {'S3', 'S4', 'S5', 'S6', 'S7'}


    assert rib.destinations.get('1.1.2.0/24').best_route.negative_next_hops == {'S3'}
    assert rib.destinations.get('1.1.2.0/24').best_route.next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.2.0/24'].next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.2.0/24'] == {'S2', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.2.0.0/16').best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get('1.2.0.0/16').best_route.next_hops == {'S1', 'S2', 'S3', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.2.0.0/16'].next_hops == {'S1', 'S2', 'S3', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.2.0.0/16'] == {'S1', 'S2', 'S3', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.2.1.0/24').best_route.negative_next_hops == {'S5'}
    assert rib.destinations.get('1.2.1.0/24').best_route.next_hops == {'S1', 'S2', 'S3', 'S6', 'S7'}
    assert rib.fib.routes['1.2.1.0/24'].next_hops == {'S1', 'S2', 'S3', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.2.1.0/24'] == {'S1', 'S2', 'S3', 'S6', 'S7'}

    assert rib.destinations.get('1.2.2.0/24').best_route.negative_next_hops == {'S6'}
    assert rib.destinations.get('1.2.2.0/24').best_route.next_hops == {'S1', 'S2', 'S3', 'S5', 'S7'}
    assert rib.fib.routes['1.2.2.0/24'].next_hops == {'S1', 'S2', 'S3', 'S5', 'S7'}
    assert rib.fib.kernel.routes['1.2.2.0/24'] == {'S1', 'S2', 'S3', 'S5', 'S7'}

    # Delete nexthop S3 from the parent route 0.0.0.0/0.
    rib.put_route(RibRoute('1.0.0.0/8', S_SPF, ['S1', 'S2', 'S4', 'S5', 'S6', 'S7']))

    # Testing only rib, fib and kernel next hops
    assert rib.destinations.get('1.0.0.0/8').best_route.next_hops == {'S1', 'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.0.0.0/8'].next_hops == {'S1', 'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.0.0.0/8'] == {'S1', 'S2', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.1.0.0/16').best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get('1.1.0.0/16').best_route.next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.0.0/16'].next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.0.0/16'] == {'S2', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.1.1.0/24').best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get('1.1.1.0/24').best_route.next_hops == {'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.1.0/24'].next_hops == {'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.1.0/24'] == {'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.1.2.0/24').best_route.negative_next_hops == {'S3'}
    assert rib.destinations.get('1.1.2.0/24').best_route.next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.1.2.0/24'].next_hops == {'S2', 'S4', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.1.2.0/24'] == {'S2', 'S4', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.2.0.0/16').best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get('1.2.0.0/16').best_route.next_hops == {'S1', 'S2', 'S5', 'S6', 'S7'}
    assert rib.fib.routes['1.2.0.0/16'].next_hops == {'S1', 'S2', 'S5', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.2.0.0/16'] == {'S1', 'S2', 'S5', 'S6', 'S7'}

    assert rib.destinations.get('1.2.1.0/24').best_route.negative_next_hops == {'S5'}
    assert rib.destinations.get('1.2.1.0/24').best_route.next_hops == {'S1', 'S2', 'S6', 'S7'}
    assert rib.fib.routes['1.2.1.0/24'].next_hops == {'S1', 'S2', 'S6', 'S7'}
    assert rib.fib.kernel.routes['1.2.1.0/24'] == {'S1', 'S2', 'S6', 'S7'}

    assert rib.destinations.get('1.2.2.0/24').best_route.negative_next_hops == {'S6'}
    assert rib.destinations.get('1.2.2.0/24').best_route.next_hops == {'S1', 'S2', 'S5', 'S7'}
    assert rib.fib.routes['1.2.2.0/24'].next_hops == {'S1', 'S2', 'S5', 'S7'}
    assert rib.fib.kernel.routes['1.2.2.0/24'] == {'S1', 'S2', 'S5', 'S7'}

    # Delete all routes from the RIB.
    rib.del_route("1.0.0.0/8", S_SPF)
    rib.del_route("1.1.0.0/16", S_SPF)
    rib.del_route("1.1.1.0/24", S_SPF)
    rib.del_route("1.1.2.0/24", S_SPF)
    rib.del_route("1.2.0.0/16", S_SPF)
    rib.del_route("1.2.1.0/24", S_SPF)
    rib.del_route("1.2.2.0/24", S_SPF)

    assert not rib.destinations.keys()
    assert not rib.fib.routes.keys()
    assert not rib.fib.kernel.routes.keys()