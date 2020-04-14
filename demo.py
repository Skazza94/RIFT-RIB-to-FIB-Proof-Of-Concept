from rib import Rib
from rib_route import RibRoute

default_prefix = "0.0.0.0/0"
default_next_hops = {'S1', 'S2', 'S3', 'S4'}

first_negative_disagg_prefix = "10.0.0.0/16"
first_negative_disagg_next_hops = {'S1'}

second_negative_disagg_prefix = "10.1.0.0/16"
second_negative_disagg_next_hops = {'S4'}

subnet_disagg_prefix = "10.0.10.0/24"
subnet_negative_disagg_next_hops = ['S2']

unreachable_prefix = "200.0.0.0/16"
unreachable_negative_next_hops = ['S1', 'S2', 'S3', 'S4']

leaf_prefix = "20.0.0.0/16"
leaf_prefix_positive_next_hops = ["M4"]
leaf_prefix_negative_next_hops = ["M3"]



N_SPF = 1
S_SPF = 2


rib = Rib()
print("Slide 55: Adding default route to RIB")
default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
rib.put_route(default_route)
print(rib)
input("Press Enter to continue...\n\n")


print("Slide 56: Adding negative disaggregation for %s via S1" % first_negative_disagg_prefix)
first_disagg_route = RibRoute(first_negative_disagg_prefix, S_SPF, [], first_negative_disagg_next_hops)
rib.put_route(first_disagg_route)
print(rib)
input("Press Enter to continue...\n\n")


print("Slide 57: Adding negative disaggregation for %s via S4" % second_negative_disagg_prefix)
second_disagg_route = RibRoute(second_negative_disagg_prefix, S_SPF, [], second_negative_disagg_next_hops)
rib.put_route(second_disagg_route)
print(rib)
input("Press Enter to continue...\n\n")

print("Slide 58: Removing S2 from default route")
default_route_fail = RibRoute(default_prefix, S_SPF, ['S1', 'S3', 'S4'])
rib.put_route(default_route_fail)
print(rib)
input("Press Enter to continue...\n\n")

print("Slide 58: Readding S2 to default route")
default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
rib.put_route(default_route)
print(rib)
input("Press Enter to continue...\n\n")

print("Slide 59: Adding negative disaggregation for %s via S2" % subnet_disagg_prefix)
subnet_disagg_route = RibRoute(subnet_disagg_prefix, S_SPF, [], subnet_negative_disagg_next_hops)
rib.put_route(subnet_disagg_route)
print(rib)
input("Press Enter to continue...\n\n")

print("Slide 60: Removing S3 from default route")
default_route_fail = RibRoute(default_prefix, S_SPF, ['S1', "S2", 'S4'])
rib.put_route(default_route_fail)
print(rib)
input("Press Enter to continue...\n\n")

print("Slide 60: Readding S3 to default route")
default_route = RibRoute(default_prefix, S_SPF, default_next_hops)
rib.put_route(default_route)
print(rib)
input("Press Enter to continue...\n\n")
