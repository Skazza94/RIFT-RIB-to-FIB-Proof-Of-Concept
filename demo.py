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

rib = Rib()

print("Slide 55: Adding default route to RIB")
rib.add_route(default_prefix, default_next_hops)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 56: Adding negative disaggregation for %s via S1" % first_negative_disagg_prefix)
rib.add_route(first_negative_disagg_prefix, first_negative_disagg_next_hops, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")


print("Slide 57: Adding negative disaggregation for %s via S4" % second_negative_disagg_prefix)
rib.add_route(second_negative_disagg_prefix, second_negative_disagg_next_hops, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 58: Removing S2 from default route")
failed_next_hop = {"S2"}
rib.delete_route(default_prefix, failed_next_hop)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 58: Readding S2 to default route")
rib.add_route(default_prefix, failed_next_hop)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 59: Adding negative disaggregation for %s via S2" % subnet_disagg_prefix)
rib.add_route(subnet_disagg_prefix, subnet_disagg_next_hops, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 60: Removing S3 from default route")
failed_next_hop = {"S3"}
rib.delete_route(default_prefix, failed_next_hop)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Slide 60: Readding S3 to default route")
rib.add_route(default_prefix, failed_next_hop)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if 200.0.0.0/16 becomes unreachable after all next hops are negatively disaggregated")
rib.add_route(unreachable_prefix, unreachable_next_hops, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if 200.0.0.0/16 becomes reachable after a negative disaggregation is removed, readding S3")
recovered_nodes = {"S3"}
rib.delete_route(unreachable_prefix, recovered_nodes, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if 200.0.0.0/16 is removed for RIB/FIB after all next hops are restored")
recovered_nodes = {"S1", "S2", "S4"}
rib.delete_route(unreachable_prefix, recovered_nodes, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if 10.0.10.0/24 is removed from the FIB after 10.0.0.0/16 becomes unreachable")
unreachable_next_hops = default_next_hops - first_negative_disagg_next_hops
rib.add_route(first_negative_disagg_prefix, unreachable_next_hops, disagg_type=False)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if adding a positive disaggregation for 10.0.10.0/24 via S1, this subnet becomes reachable even if "
      "10.0.0.0/16 (parent prefix) is unreachable")
rib.add_route(subnet_disagg_prefix, first_negative_disagg_next_hops)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")

print("Test if removing positive disaggregation for 10.0.10.0/24 via S1, the subnet is removed from RIB/FIB")
rib.delete_route(subnet_disagg_prefix, first_negative_disagg_next_hops)
rib.get_rib_fib_representation()
input("Press Enter to continue...\n\n")
