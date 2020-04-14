from kernel import Kernel
from fib_route import FibRoute


class Fib:
    """
    A simple FIB.
    """

    def __init__(self):
        self.routes = {}
        self.kernel = Kernel()

    def put_route(self, rte):
        if self._is_route_different(rte):
            fib_route = FibRoute(rte.prefix, rte.next_hops)
            self.routes[rte.prefix] = fib_route
            self.kernel.put_route(fib_route.prefix, fib_route.next_hops)

    def delete_route(self, prefix):
        del self.routes[prefix]
        self.kernel.delete_route(prefix)

    def _is_route_different(self, rte):
        if rte.prefix not in self.routes:
            return True

        return rte.next_hops != self.routes[rte.prefix].next_hops

    def __str__(self):
        repr_str = ""
        for prefix in self.routes:
            repr_str += "%s\n" % self.routes[prefix]
        return repr_str

    def __repr__(self):
        return str(self)
