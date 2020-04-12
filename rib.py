import pytricia

from destination import Destination
from fib import Fib


class Rib:
    """
    Class representing the RIB of a node.
    Attributes of this class are:
        - destinations: a Patricia Trie. Keys are IP prefixes and values are Destination objects
        - fib: instance of the FIB of this node
    """

    def __init__(self):
        self.destinations = pytricia.PyTricia()
        self.fib = Fib()

    def put_route(self, route):
        # If there is no Destination object for the prefix, create a new Destination object
        # for the given prefix and insert it in the Trie
        if not self.destinations.has_key(route.prefix):
            prefix_dest = Destination(self, route.prefix)
            self.destinations.insert(route.prefix, prefix_dest)
        else:
            prefix_dest = self.destinations.get(route.prefix)
        # Insert desired route in destination object
        prefix_dest.put_route(route)

        children_prefixes = self.destinations.children(prefix_dest.prefix)
        update_fib = True
        # This condition is triggered only if all the next hops are added as negative next hops!
        if not route.positive_next_hops and route.negative_next_hops:
            if not prefix_dest.best_route.next_hops:
                # Since the given prefix is unreachable, remove superfluous children routes of the
                # prefix from the RIB and the FIB
                for child_prefix in children_prefixes:
                    self.destinations.delete(child_prefix)
                    self.fib.delete_route(child_prefix)

        # TODO: ask if this case can occur
        # if prefix_dest.parent_prefix_dest is not None and \
        #         prefix_dest.best_route.next_hops == prefix_dest.parent_prefix_dest.best_route.next_hops:
        #     del self.destinations[prefix_dest.prefix]
        #     self.fib.delete_route(prefix_dest.prefix)
        #     update_fib = False
        #
        # if update_fib:
        self.fib.put_route(prefix_dest.best_route)

        # Force recomputing of children next hops since they need to add new next hops in their
        # sets. After recomputing, reassign the child computed next hops to the FIB.
        # N.B.: self.destinations.get(child_prefix) contains all the children at each level of the current prefix, so
        # recursion is not needed
        for child_prefix in children_prefixes:
            child_prefix_dest = self.destinations.get(child_prefix)
            self.fib.put_route(child_prefix_dest.best_route)

    def del_route(self, prefix, owner):
        # Returns True if the route was present in the table and False if not.
        destination_deleted = False
        best_changed = False
        children_prefixes = None
        if self.destinations.has_key(prefix):
            children_prefixes = self.destinations.children(prefix)
            destination = self.destinations[prefix]
            deleted, best_changed = destination.del_route(owner)
            if not deleted:
                return
            if not destination.routes:
                del self.destinations[prefix]
                self.fib.delete_route(prefix)
                destination_deleted = True
            elif best_changed:
                self.fib.put_route(destination.best_route)
        else:
            deleted = False
        if deleted:
            for child_prefix in children_prefixes:
                if best_changed or destination_deleted:
                    child_destination = self.destinations[child_prefix]
                    self.fib.put_route(child_destination.best_route)

        return deleted

    def get_rib_fib_representation(self):
        print("--------------------- RIB ---------------------------")
        for prefix in self.destinations.keys():
            print(self.destinations.get(prefix))
        print("--------------------- FIB ---------------------------")
        for prefix, dests in self.fib.routes.items():
            print(prefix, "\t", dests)
        print("-----------------------------------------------------")
