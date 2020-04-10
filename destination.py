class Destination:
    """
    An object that represents a prefix destination in the RIB.
    It keeps track of positive and negative next hops and it also computes the real next hops
    to install in the FIB.
    """

    def __init__(self, rib, prefix):
        self.prefix = prefix
        self.rib = rib

        self._positive_next_hops = set()
        self._negative_next_hops = set()
        self._computed_next_hops = None

    @property
    def next_hops(self):
        """
        Lazy loaded property.
        If the next hops are not already computed, it computes the next hops.
        Else it uses the precomputed result.
        :return: the computed next hops ready to be installed in the FIB.
        """
        if self._computed_next_hops is None:
            self._computed_next_hops = self._compute_next_hops()

        return self._computed_next_hops

    def add_positive_next_hop(self, next_hop):
        """
        Adds a single positive next hop to the set of positive next hops for this prefix.
        If the computed next hops set has been loaded, it also updates it. Else, it will be
        computed to the next reference to `self.next_hops`.
        :param next_hop: The positive next hop to add for this prefix
        :return:
        """
        self._positive_next_hops.add(next_hop)
        if self._computed_next_hops is not None:
            self._computed_next_hops.add(next_hop)

    def add_positive_next_hops(self, next_hops):
        """
        Adds a set of positive next hops to the set of positive next hops for this prefix.
        If the computed next hops set has been loaded, it also updates it. Else, it will be
        computed to the next reference to `self.next_hops`.
        :param next_hops: The set of positive next hops to add for this prefix
        :return:
        """
        self._positive_next_hops.update(next_hops)
        if self._computed_next_hops is not None:
            self._computed_next_hops.update(next_hops)

    def add_negative_next_hop(self, next_hop):
        """
        Adds a single negative next hop to the set of negative next hops for this prefix.
        If computed next hops set has been loaded, also deletes this next hop from it.
        A negative next hop is a next hop for which a negative disaggregation has been received.
        :param next_hop: The negative next hop to add for this prefix
        :return:
        """
        self._negative_next_hops.add(next_hop)
        if self._computed_next_hops is not None and next_hop in self._computed_next_hops:
            self._computed_next_hops.remove(next_hop)

    def add_negative_next_hops(self, next_hops):
        """
        Adds a set of negative next hops to the set of negative next hops for this prefix.
        If computed next hops set has been loaded, deletes each next hop of the set from it.
        A negative next hop is a next hop for which a negative disaggregation has been received.
        :param next_hops: The negative next hops set to add for this prefix
        :return:
        """
        for next_hop in next_hops:
            self.add_negative_next_hop(next_hop)

    def remove_positive_next_hop(self, next_hop):
        """
        Removes a positive next hop from the set of positive next hops for this prefix.
        If computed next hops set has been loaded, also deletes this next hop from it.
        :param next_hop: The positive next hop to remove for this prefix
        :return:
        """
        if next_hop in self._positive_next_hops:
            self._positive_next_hops.remove(next_hop)
        if self._computed_next_hops is not None and next_hop in self._computed_next_hops:
            self._computed_next_hops.remove(next_hop)

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
        if next_hop in self._negative_next_hops:
            self._negative_next_hops.remove(next_hop)
        if self._computed_next_hops is not None and next_hop not in self._computed_next_hops:
            self.next_hops.add(next_hop)

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

    def refresh(self):
        """
        Force recomputing the computed next hops set at the next reference of `self.next_hops`.
        :return:
        """
        self._computed_next_hops = None

    def _compute_next_hops(self):
        """
        Computes the the real next hops set for this prefix.
        Real next hops set is the set of next hops that can be used to reach this prefix. (the ones
        to be installed in the FIB)
        :return: the set of real next hops
        """
        # If there are positive next hops, these are preferred.
        # Return the set of positive next hops.
        if self._positive_next_hops:
            return self._positive_next_hops

        # Get the parent prefix destination object from the RIB
        # If there are no parents for the current prefix, then return the positive next hops set.
        # This only occurs when the prefix is the default (0.0.0.0/0)
        parent_prefix = self.rib.destinations.parent(self.prefix)
        if parent_prefix is None:
            return self._positive_next_hops

        parent_prefix_dest = self.rib.destinations.get(parent_prefix)

        # Computes the next hops as the difference between the computed parent next hops and
        # the negative next hops.
        return parent_prefix_dest.next_hops - self._negative_next_hops

    def __str__(self):
        parent_prefix = self.rib.destinations.parent(self.prefix)
        parent_str = "(parent: %s)" % parent_prefix if parent_prefix else ""
        return "%s %s\n\tPositive: %s\n\tNegative: %s" \
               "\n\tComputed: %s" % (self.prefix, parent_str,
                                     str(self._positive_next_hops),
                                     str(self._negative_next_hops),
                                     str(self.next_hops))

    def __repr__(self):
        parent_prefix = self.rib.destinations.parent(self.prefix)
        parent_str = "(parent: %s)" % parent_prefix if parent_prefix else ""
        return "%s %s\n\tPositive: %s\n\tNegative: %s" \
               "\n\tComputed: %s" % (self.prefix, parent_str,
                                     str(self._positive_next_hops),
                                     str(self._negative_next_hops),
                                     str(self.next_hops))
