class Destination:
    """
    Class that contains all routes for a given prefix destination
    Attributes of this class are:
        - rib: reference to the RIB
        - prefix: prefix associated to this destination
        - routes: list of Route objects, in decreasing order or owner (= in decreasing order of preference, higher
                  numerical value is more preferred). For a given owner, at most one route is allowed to be in the list
    """

    def __init__(self, rib, prefix):
        self.rib = rib
        self.prefix = prefix
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
        :return: the best Route for this prefix
        """
        return self.routes[0]

    def get_route(self, owner):
        """
        Get Route object for a given owner if present
        :param owner: (int) owner of the route
        :return: (Route|None) desired Route object if present, else None
        """
        for rte in self.routes:
            if rte.owner == owner:
                return rte
        return None

    def put_route(self, new_route):
        """
        Add a new Route object in the list of routes for the current prefix. Route is added with proper priority.
        :param new_route: (Route) route to add to the list
        :return:
        """
        assert self.prefix == new_route.prefix
        added = False
        best_changed = False
        index = 0
        for existing_route in self.routes:
            if existing_route.owner == new_route.owner:
                self.routes[index] = new_route
                added = True
                break
            elif existing_route.owner < new_route.owner:
                self.routes.insert(index, new_route)
                added = True
                break
            index += 1
        if not added:
            self.routes.append(new_route)
        # Update the Route Destination object instance with the current object
        if index == 0:
            best_changed = True
        new_route.destination = self
        return best_changed

    def del_route(self, owner):
        """
        Delete a Route object for the given owner
        :param owner: (int) owner of the route
        :return: (tuple) first element is a boolean that indicates if the route has been deleted, second element is a
                         boolean that indicates if the best route changed
        """
        best_changed = False
        for index, rte in enumerate(self.routes):
            if rte.owner == owner:
                del self.routes[index]
                if index == 0:
                    best_changed = True
                return True, best_changed
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
