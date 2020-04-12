from kernel import Kernel


class Fib:
    """
    A simple FIB.
    """
    def __init__(self):
        self.routes = {}
        self.kernel = Kernel()

    def put_route(self, rte):
        self.routes[rte.prefix] = rte
        self.kernel.put_route(rte.prefix, rte.next_hops)

    def delete_route(self, prefix):
        del self.routes[prefix]
        self.kernel.delete_route(prefix)
