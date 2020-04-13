class Kernel:
    """
    A simple class representing the kernel routing table.
    """

    def __init__(self):
        self.routes = {}

    def put_route(self, prefix, next_hops):
        self.routes[prefix] = "unreachable" if not next_hops else next_hops

    def delete_route(self, prefix):
        del self.routes[prefix]
