from rib import Rib
from route import Route, DEST_TYPE_PREFIX, DEST_TYPE_POS_DISAGG_PREFIX, DEST_TYPE_NEG_DISAGG_PREFIX

N_SPF = 1
S_SPF = 2

default_prefix = "0.0.0.0/0"
default_next_hops = [('S1', DEST_TYPE_PREFIX), ('S2', DEST_TYPE_PREFIX), ('S3', DEST_TYPE_PREFIX),
                     ('S4', DEST_TYPE_PREFIX)]

first_negative_disagg_prefix = "10.0.0.0/16"
first_negative_disagg_next_hops = [('S1', DEST_TYPE_NEG_DISAGG_PREFIX)]

second_negative_disagg_prefix = "10.1.0.0/16"
second_negative_disagg_next_hops = [('S4', DEST_TYPE_NEG_DISAGG_PREFIX)]

subnet_disagg_prefix = "10.0.10.0/24"
subnet_disagg_next_hops = [('S2', DEST_TYPE_NEG_DISAGG_PREFIX)]

unreachable_prefix = "200.0.0.0/16"
unreachable_next_hops = [('S1', DEST_TYPE_NEG_DISAGG_PREFIX), ('S2', DEST_TYPE_NEG_DISAGG_PREFIX),
                         ('S3', DEST_TYPE_NEG_DISAGG_PREFIX), ('S4', DEST_TYPE_NEG_DISAGG_PREFIX)]

leaf_prefix = "20.0.0.0/16"
leaf_prefix_next_hops = [("M4", DEST_TYPE_POS_DISAGG_PREFIX), ("M3", DEST_TYPE_NEG_DISAGG_PREFIX)]


# Slide 55
def test_add_default_route():
    rib = Rib()
    route = Route(default_prefix, N_SPF)
    route.add_next_hops(default_next_hops)
    rib.put_route(route)
    assert rib.destinations.get(default_prefix).best_route == route
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix] == route
    assert rib.fib.kernel.routes[default_prefix] == route.next_hops


# Slide 56
def test_add_negative_disaggregation():
    rib = Rib()
    route = Route(default_prefix, N_SPF)
    route.add_next_hops(default_next_hops)
    rib.put_route(route)
    neg_route = Route(first_negative_disagg_prefix, N_SPF)
    neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(neg_route)
    assert rib.destinations.get(first_negative_disagg_prefix).best_route == neg_route
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3', 'S4'}
    assert rib.fib.routes[first_negative_disagg_prefix] == neg_route
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == neg_route.next_hops


# Slide 57
def test_add_two_negative_disaggregation():
    rib = Rib()
    route = Route(default_prefix, N_SPF)
    route.add_next_hops(default_next_hops)
    rib.put_route(route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    second_neg_route = Route(second_negative_disagg_prefix, N_SPF)
    second_neg_route.add_next_hops(second_negative_disagg_next_hops)
    rib.put_route(second_neg_route)
    assert rib.destinations.get(second_negative_disagg_prefix).best_route == second_neg_route
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.next_hops == {'S1', 'S2', 'S3'}
    assert rib.fib.routes[second_negative_disagg_prefix] == second_neg_route
    assert rib.fib.kernel.routes[second_negative_disagg_prefix] == second_neg_route.next_hops


# Slide 58
def test_remove_default_next_hop():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    second_neg_route = Route(second_negative_disagg_prefix, N_SPF)
    second_neg_route.add_next_hops(second_negative_disagg_next_hops)
    rib.put_route(second_neg_route)
    default_route_fail = Route(default_prefix, N_SPF)
    default_route_fail.add_next_hops([('S1', DEST_TYPE_PREFIX), ('S3', DEST_TYPE_PREFIX), ('S4', DEST_TYPE_PREFIX)])
    rib.put_route(default_route_fail)
    # test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_fail
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix] == default_route_fail
    assert rib.fib.kernel.routes[default_prefix] == default_route_fail.next_hops
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_neg_route.next_hops
    # test for 10.1.0.0/16
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.negative_next_hops == {'S4'}
    assert rib.destinations.get(second_negative_disagg_prefix).best_route.next_hops == {'S1', 'S3'}
    assert rib.fib.kernel.routes[second_negative_disagg_prefix] == second_neg_route.next_hops


# Slide 59
def test_add_subnet_disagg_to_first_negative_disagg():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    subnet_neg_route = Route(subnet_disagg_prefix, N_SPF)
    subnet_neg_route.add_next_hops(subnet_disagg_next_hops)
    rib.put_route(subnet_neg_route)
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.routes[subnet_disagg_prefix] == subnet_neg_route
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_neg_route.next_hops


# Slide 60
def test_remove_default_next_hop_with_subnet_disagg():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    subnet_neg_route = Route(subnet_disagg_prefix, N_SPF)
    subnet_neg_route.add_next_hops(subnet_disagg_next_hops)
    rib.put_route(subnet_neg_route)
    default_route_fail = Route(default_prefix, N_SPF)
    default_route_fail.add_next_hops([('S1', DEST_TYPE_PREFIX), ('S2', DEST_TYPE_PREFIX), ('S4', DEST_TYPE_PREFIX)])
    rib.put_route(default_route_fail)
    # test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_fail
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S4'}
    assert rib.fib.routes[default_prefix] == default_route_fail
    assert rib.fib.kernel.routes[default_prefix] == default_route_fail.next_hops
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_neg_route.next_hops
    # test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S4'}
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_neg_route.next_hops

# Slide 60 and recover of the failed next hops
def test_recover_default_next_hop_with_subnet_disagg():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    subnet_neg_route = Route(subnet_disagg_prefix, N_SPF)
    subnet_neg_route.add_next_hops(subnet_disagg_next_hops)
    rib.put_route(subnet_neg_route)
    default_route_fail = Route(default_prefix, N_SPF)
    default_route_fail.add_next_hops([('S1', DEST_TYPE_PREFIX), ('S2', DEST_TYPE_PREFIX), ('S4', DEST_TYPE_PREFIX)])
    rib.put_route(default_route_fail)
    default_route_fail.add_next_hops([('S3', DEST_TYPE_PREFIX)])
    rib.put_route(default_route_fail)
    # test for default
    assert rib.destinations.get(default_prefix).best_route == default_route_fail
    assert rib.destinations.get(default_prefix).best_route.positive_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(default_prefix).best_route.negative_next_hops == set()
    assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.fib.routes[default_prefix] == default_route_fail
    assert rib.fib.kernel.routes[default_prefix] == default_route_fail.next_hops
    # test for 10.0.0.0/16
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == {'S2', 'S3',  'S4'}
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == first_neg_route.next_hops
    # test for 10.0.10.0/24
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {'S2'}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {'S3', 'S4'}
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == subnet_neg_route.next_hops


# Tests if a route becomes unreachable after all next hops are negatively disaggregated
def test_neg_disagg_fib_unreachable():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    unreachable_route = Route(unreachable_prefix, N_SPF)
    unreachable_route.add_next_hops(unreachable_next_hops)
    rib.put_route(unreachable_route)
    assert rib.destinations.get(unreachable_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(unreachable_prefix).best_route.next_hops == set()
    assert rib.fib.routes[unreachable_prefix] == unreachable_route
    assert rib.fib.kernel.routes[unreachable_prefix] == "unreachable"


# Tests if an unreachable route becomes reachable after a negative disaggregation is removed
def test_neg_disagg_fib_unreachable_recover():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    unreachable_route = Route(unreachable_prefix, N_SPF)
    unreachable_route.add_next_hops(unreachable_next_hops)
    rib.put_route(unreachable_route)
    unreachable_route_recover = Route(unreachable_prefix, N_SPF)
    unreachable_route_recover.add_next_hops([('S1', DEST_TYPE_NEG_DISAGG_PREFIX), ('S2', DEST_TYPE_NEG_DISAGG_PREFIX),
                                             ('S4', DEST_TYPE_NEG_DISAGG_PREFIX)])
    rib.put_route(unreachable_route_recover)
    assert rib.destinations.get(unreachable_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(unreachable_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S4'}
    assert rib.destinations.get(unreachable_prefix).best_route.next_hops == {'S3'}
    assert rib.fib.routes[unreachable_prefix] == unreachable_route_recover
    assert rib.fib.kernel.routes[unreachable_prefix] == {'S3'}


# Tests if a subnet of an unreachable route (negative disaggregated) is removed from the FIB
def test_add_subnet_disagg_recursive_unreachable():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    subnet_neg_route = Route(subnet_disagg_prefix, N_SPF)
    subnet_neg_route.add_next_hops(subnet_disagg_next_hops)
    rib.put_route(subnet_neg_route)
    first_neg_unreach = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_unreach.add_next_hops(unreachable_next_hops)
    rib.put_route(first_neg_unreach)
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.positive_next_hops == set()
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.negative_next_hops == {'S1', 'S2', 'S3', 'S4'}
    assert rib.destinations.get(first_negative_disagg_prefix).best_route.next_hops == set()
    assert rib.fib.routes[first_negative_disagg_prefix] == first_neg_unreach
    assert rib.fib.kernel.routes[first_negative_disagg_prefix] == "unreachable"
    assert not rib.destinations.has_key(subnet_disagg_prefix)
    assert subnet_disagg_prefix not in rib.fib.routes


# Slide 61 from the perspective of L3
def test_pos_neg_disagg():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    leaf_route = Route(leaf_prefix, N_SPF)
    leaf_route.add_next_hops(leaf_prefix_next_hops)
    rib.put_route(leaf_route)
    assert rib.destinations.get(leaf_prefix).best_route.positive_next_hops == {"M4"}
    assert rib.destinations.get(leaf_prefix).best_route.negative_next_hops == {"M3"}
    assert rib.destinations.get(leaf_prefix).best_route.next_hops == {"M4"}
    assert rib.fib.routes[leaf_prefix] == leaf_route
    assert rib.fib.kernel.routes[leaf_prefix] == {"M4"}

# Given a prefix X with N negative next hops
# Given a prefix Y, subnet of X, with M negative next hops and a positive next hop L included in N
# Results that next hops of Y include L
def test_pos_neg_disagg_recursive():
    rib = Rib()
    default_route = Route(default_prefix, N_SPF)
    default_route.add_next_hops(default_next_hops)
    rib.put_route(default_route)
    first_neg_route = Route(first_negative_disagg_prefix, N_SPF)
    first_neg_route.add_next_hops(first_negative_disagg_next_hops)
    rib.put_route(first_neg_route)
    subnet_disagg_route = Route(subnet_disagg_prefix, N_SPF)
    subnet_disagg_next_hops.append(('S1', DEST_TYPE_POS_DISAGG_PREFIX))
    subnet_disagg_route.add_next_hops(subnet_disagg_next_hops)
    rib.put_route(subnet_disagg_route)
    assert rib.destinations.get(subnet_disagg_prefix).best_route.positive_next_hops == {"S1"}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.negative_next_hops == {"S2"}
    assert rib.destinations.get(subnet_disagg_prefix).best_route.next_hops == {"S1"}
    assert rib.fib.routes[subnet_disagg_prefix] == subnet_disagg_route
    assert rib.fib.kernel.routes[subnet_disagg_prefix] == {"S1"}


# def test_add_two_route_same_destination():
#     rib = Rib()
#     best_default_route = Route(default_prefix, N_SPF)
#     best_default_route.add_next_hops(default_next_hops)
#     rib.put_route(best_default_route)
#     second_default_route = Route(default_prefix, S_SPF)
#     second_default_route.add_next_hops([('S1', DEST_TYPE_PREFIX)])
#     rib.put_route(second_default_route)
#     assert rib.destinations.get(default_prefix).best_route == best_default_route
#     assert rib.destinations.get(default_prefix).best_route.next_hops == {'S1', 'S2', 'S3', 'S4'}
#     assert rib.fib.routes[default_prefix] == best_default_route
#     assert rib.fib.kernel.routes[default_prefix] == best_default_route.next_hops
