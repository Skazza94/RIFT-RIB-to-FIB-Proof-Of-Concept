class Destination:
    # For each prefix, there can be up to one route per owner. This is also the order of preference
    # for the routes from different owners to the same destination (higher numerical value is more
    # preferred)
    def __init__(self, rib, prefix):
        self.rib = rib
        self.prefix = prefix
        # List of Route objects, in decreasing order or owner (= in decreasing order of preference)
        # For a given owner, at most one route is allowed to be in the list
        self.routes = []

    @property
    def parent_prefix_dest(self):
        """
        :return: the Destination object associated to the parent prefix of the current one
        """
        parent_prefix = self.rib.destinations.parent(self.prefix)
        if parent_prefix is None:
            return None

        return self.rib.destinations.get(parent_prefix)

    @property
    def best_route(self):
        """
        :return: the best Route for this prefix if present
        """
        return self.routes[0]

    def get_route(self, owner):
        for rte in self.routes:
            if rte.owner == owner:
                return rte
        return None

    def put_route(self, new_route):
        assert self.prefix == new_route.prefix
        added = False
        for index, existing_route in enumerate(self.routes):
            if existing_route.owner == new_route.owner:
                self.routes[index] = new_route
                added = True
                break
            elif existing_route.owner < new_route.owner:
                self.routes.insert(index, new_route)
                added = True
                break
        if not added:
            self.routes.append(new_route)
        # Update the Route Destination object instance with the current object
        new_route.destination = self

    def del_route(self, owner):
        index = 0
        best_changed = False
        for rte in self.routes:
            if rte.owner == owner:
                del self.routes[index]
                if index == 0:
                    best_changed = True
                return True, best_changed
            index += 1
        return False, best_changed

    def __repr__(self):
        parent_prefix = "(Parent: " + self.parent_prefix_dest.prefix + ")" if self.parent_prefix_dest else ""
        return "%s\n%s %s\nBest Computed: %s\n\n" % (self.prefix, parent_prefix, str(self.routes),
                                                     str(self.best_route.next_hops))

    @staticmethod
    def routes_significantly_different(route1, route2):
        assert route1.prefix == route2.prefix
        if route1.owner != route2.owner:
            return True
