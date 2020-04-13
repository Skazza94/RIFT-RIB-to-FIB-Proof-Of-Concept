DEST_TYPE_PREFIX = 2
DEST_TYPE_POS_DISAGG_PREFIX = 3
DEST_TYPE_NEG_DISAGG_PREFIX = 4


class Route:
    """
    An object that represents a prefix route for a Destination.
    It keeps track of positive and negative next hops and it also computes the real next hops
    to install in the kernel.
    Attributes of this class are:
        - prefix: prefix associated to this route
        - owner: owner of this route
        - destination: Destination object which contains this route
        - stale: boolean that marks the route as stale
        - positive_next_hops: set of positive next hops for the prefix
        - negative_next_hops: set of negative next hops for the prefix
    """

    def __init__(self, prefix, owner, positive_next_hops, negative_next_hops=None):
        self.prefix = prefix
        self.owner = owner
        self.destination = None
        self.stale = False

        self.positive_next_hops = set(positive_next_hops)
        self.negative_next_hops = set(negative_next_hops) if negative_next_hops else set()

    @property
    def next_hops(self):
        """
        :return: the computed next hops for the Route ready to be installed in the kernel.
        """
        return self._compute_next_hops()

    def _compute_next_hops(self):
        """
        Computes the the real next hops set for this prefix.
        Real next hops set is the set of next hops that can be used to reach this prefix. (the ones
        to be installed in the kernel)
        :return: the set of real next hops
        """
        # The route does not have any negative nexthops; there is no disaggregation to be done.
        if not self.negative_next_hops:
            return self.positive_next_hops

        # Get the parent prefix destination object from the RIB
        # If there are no parents for the current prefix, then return the positive next hops set.
        # This only occurs when the prefix is the default (0.0.0.0/0)
        parent_prefix_dest = self.destination.parent_prefix_dest
        if parent_prefix_dest is None:
            return self.positive_next_hops

        # Compute the complementary nexthops of the negative nexthops.
        complementary_next_hops = parent_prefix_dest.best_route.next_hops - self.negative_next_hops
        return self.positive_next_hops.union(complementary_next_hops)

    def __str__(self):
        owner = "N_SPF" if self.owner == 1 else "S_SPF"
        return "\n\tOwner: %s\n\tPositive: %s\n\tNegative: %s\n" % (owner,
                                                                    str(self.positive_next_hops),
                                                                    str(self.negative_next_hops))

    def __repr__(self):
        owner = "N_SPF" if self.owner == 1 else "S_SPF"
        return "\n\tOwner: %s\n\tPositive: %s\n\tNegative: %s\n" % (owner,
                                                                    str(self.positive_next_hops),
                                                                    str(self.negative_next_hops))
