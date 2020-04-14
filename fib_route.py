class FibRoute:
    def __init__(self, prefix, next_hops):
        self.prefix = prefix
        self.next_hops = set(next_hops)

    def __str__(self):
        sorted_next_hops = sorted(self.next_hops)
        return "%s -> %s" % (self.prefix, ", ".join(sorted_next_hops))

    def __repr__(self):
        return str(self)
