from rib import Rib

rib = Rib()

print("*** Add 0.0.0.0/0 -> [nh1, nh2, nh3] ****\n")
rib.add_route("0.0.0.0/0", ["nh1", "nh2", "nh3"])
rib.get_rib_fib_representation()
print()

print("*** Add 1.0.0.0/8 -> [nh1] ****\n")
rib.add_route("1.0.0.0/8", ["nh1"])
rib.get_rib_fib_representation()
print()

print("Incorrect:")
print("  1.0.0.0/8 should not have next-hops [nh1, nh2, nh3]")
print("  It should not have inherited positive next-hops nh2 and nh3 from 0.0.0.0/8")