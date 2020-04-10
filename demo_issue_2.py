from rib import Rib

rib = Rib()

print("*** Add 0.0.0.0/0 -> [nh1, nh2, nh3, nh4] ****\n")
rib.add_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4"]);

print("*** Add 1.0.0.0/8 -> [~nh1] ****\n")
rib.add_route("1.0.0.0/8", ["nh1"], False);

print("*** Add 1.1.0.0/16 -> [~nh2] ****\n")
rib.add_route("1.1.0.0/16", ["nh2"], False);

rib.get_rib_fib_representation()
print()

print("*** Add 1.0.0.0/8 -> [~nh3] ****\n")
rib.add_route("1.0.0.0/8", ["nh3"], False);

rib.get_rib_fib_representation()
print()

print("Incorrect:")
print()
print("  1.1.0.0/16 should not have next-hops [nh3, nh4]")
print("  nh3 should be removed as a result of 'Add 1.0.0.0/8 -> [~nh3]'")