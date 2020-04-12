DEST_TYPE_PREFIX = 2
DEST_TYPE_POS_DISAGG_PREFIX = 3
DEST_TYPE_NEG_DISAGG_PREFIX = 4


class Route:
    """
    An object that represents a prefix destination in the RIB.
    It keeps track of positive and negative next hops and it also computes the real next hops
    to install in the FIB.
    """

    def __init__(self, prefix, owner):
        self.prefix = prefix
        self.owner = owner
        self.destination = None
        self.stale = False

        self.positive_next_hops = set()
        self.negative_next_hops = set()

    @property
    def next_hops(self):
        """
        :return: the computed next hops for the Route ready to be installed in the FIB.
        """
        return self._compute_next_hops()

    def add_next_hops(self, next_hops):
        for next_hop, next_hop_type in next_hops:
            if next_hop_type == DEST_TYPE_PREFIX or next_hop_type == DEST_TYPE_POS_DISAGG_PREFIX:
                self._add_positive_next_hop(next_hop)
            elif next_hop_type == DEST_TYPE_NEG_DISAGG_PREFIX:
                self._add_negative_next_hop(next_hop)
            else:
                assert False

    def _add_positive_next_hop(self, next_hop):
        """
        Adds a positive next hop to the set of positive next hops for this prefix.
        :param next_hop: The positive next hop to add for this prefix
        :return:
        """
        self.positive_next_hops.add(next_hop)

    def _add_negative_next_hop(self, next_hop):
        """
        Adds a negative next hop to the set of negative next hops for this prefix.
        :param next_hop: The negative next hop to add for this prefix
        :return:
        """
        self.negative_next_hops.add(next_hop)

    def remove_positive_next_hop(self, next_hop):
        """
        Removes a positive next hop from the set of positive next hops for this prefix.
        If computed next hops set has been loaded, also deletes this next hop from it.
        :param next_hop: The positive next hop to remove for this prefix
        :return:
        """
        if next_hop in self.positive_next_hops:
            self.positive_next_hops.remove(next_hop)

    def remove_positive_next_hops(self, next_hops):
        """
        Removes a set of positive next hops from the set of positive next hops for this prefix.
        If computed next hops set has been loaded, also deletes these next hops from it.
        :param next_hops: The positive next hops set to remove for this prefix
        :return:
        """
        for next_hop in next_hops:
            self.remove_positive_next_hop(next_hop)

    def remove_negative_next_hop(self, next_hop):
        """
        Removes a single negative next hop from the set of negative next hops for this prefix.
        If computed next hops set has been loaded, also adds this next hop to it.
        (The removal of a negative disaggregation means adding a next hop)
        :param next_hop: The negative next hop to remove for this prefix
        :return:
        """
        if next_hop in self.negative_next_hops:
            self.negative_next_hops.remove(next_hop)

    def remove_negative_next_hops(self, next_hops):
        """
        Removes a negative next hops set from the set of negative next hops for this prefix.
        If computed next hops set has been loaded, also adds these next hops to it.
        (The removal of a negative disaggregation means adding a next hop)
        :param next_hops: The negative next hops set to remove for this prefix
        :return:
        """
        for next_hop in next_hops:
            self.remove_negative_next_hop(next_hop)

    def _compute_next_hops(self):
        """
        Computes the the real next hops set for this prefix.
        Real next hops set is the set of next hops that can be used to reach this prefix. (the ones
        to be installed in the FIB)
        :return: the set of real next hops
        """
        # If there are positive next hops, these are preferred.
        # Return the set of positive next hops.
        if self.positive_next_hops:
            return self.positive_next_hops

        # Get the parent prefix destination object from the RIB
        # If there are no parents for the current prefix, then return the positive next hops set.
        # This only occurs when the prefix is the default (0.0.0.0/0)
        parent_prefix_dest = self.destination.parent_prefix_dest
        if parent_prefix_dest is None:
            return self.positive_next_hops

        # Computes the next hops as the difference between the computed parent next hops and
        # the negative next hops.
        return parent_prefix_dest.best_route.next_hops - self.negative_next_hops

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
