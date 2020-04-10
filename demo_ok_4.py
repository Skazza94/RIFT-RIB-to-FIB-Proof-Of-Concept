from rib import Rib

rib = Rib()

print("*** Add 0.0.0.0/0 -> [nh1, nh2, nh3, nh4, nh5, nh6] ****\n")
rib.add_route("0.0.0.0/0", ["nh1", "nh2", "nh3", "nh4", "nh5", "nh6"]);

print("*** Add 1.0.0.0/8 -> [~nh1] ****\n")
rib.add_route("1.0.0.0/8", ["nh1"], False);

print("*** Add 1.1.0.0/16 -> [~nh2] ****\n")
rib.add_route("1.1.0.0/16", ["nh2"], False);

print("*** Add 1.1.1.0/24 -> [~nh3] ****\n")
rib.add_route("1.1.1.0/24", ["nh3"], False);

print("*** Add 1.1.1.1/32 -> [~nh4] ****\n")
rib.add_route("1.1.1.1/32", ["nh4"], False);

rib.get_rib_fib_representation()
print()

print("*** Add 0.0.0.0/0 -> [nh7] ****\n")
rib.add_route("0.0.0.0/0", ["nh7"]);

rib.get_rib_fib_representation()
print()
