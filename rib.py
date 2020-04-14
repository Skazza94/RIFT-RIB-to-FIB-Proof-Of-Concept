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
        """
        Add a RibRoute object to the Destination object associated to the prefix.
        :param route: (RibRoute) the object to add to the Destination associated to the prefix
        :return:
        """
        # If there is no Destination object for the prefix, create a new Destination object
        # for the given prefix and insert it in the Trie
        if not self.destinations.has_key(route.prefix):
            prefix_destination = Destination(self, route.prefix)
            self.destinations.insert(route.prefix, prefix_destination)
        else:
            prefix_destination = self.destinations.get(route.prefix)
        # Insert desired route in destination object
        best_changed = prefix_destination.put_route(route)
        # Get children prefixes before performing actions on the prefix (it can be deleted from the Trie)
        children_prefixes = self.destinations.children(prefix_destination.prefix)

        # TODO: ask if this case can occur
        # update_fib = True
        # if prefix_dest.parent_prefix_dest is not None and \
        #         prefix_dest.best_route.next_hops == prefix_dest.parent_prefix_dest.best_route.next_hops:
        #     del self.destinations[prefix_dest.prefix]
        #     self.fib.delete_route(prefix_dest.prefix)
        #     update_fib = False
        #
        # if update_fib:

        # If best route changed in Destination object
        if best_changed:
            # Update prefix in the fib
            self.fib.put_route(prefix_destination.best_route)
            # Try to delete superfluous children
            if not self._delete_superfluous_children(prefix_destination, children_prefixes):
                # If children have not been deleted, update them
                self._update_prefix_children(children_prefixes)

    def del_route(self, prefix, owner):
        """
        Delete given prefix and owner RibRoute object.
        If no more RibRoute objects are available, also delete Destination from trie and from the FIB.
        :param prefix: (string) prefix to delete
        :param owner: (int) owner of the prefix
        :return: (boolean) if the route has been deleted or not
        """
        destination_deleted = False
        best_changed = False
        children_prefixes = None
        # Check if the prefix is stored in the trie
        if self.destinations.has_key(prefix):
            # Get children prefixes before performing actions on the prefix (it can be deleted from the Trie)
            children_prefixes = self.destinations.children(prefix)
            destination = self.destinations.get(prefix)
            # Delete route from the Destination object
            deleted, best_changed = destination.del_route(owner)
            # Route was not present in Destination object, nothing to do
            if not deleted:
                return
            if not destination.routes:
                # No more routes available for current prefix, delete it from trie and FIB
                self.destinations.delete(prefix)
                self.fib.delete_route(prefix)
                destination_deleted = True
            elif best_changed:
                # Best route changed, push it in the FIB
                self.fib.put_route(destination.best_route)
        else:
            deleted = False
        if deleted and (best_changed or destination_deleted):
            # If route has been deleted and an event occurred (best changed or destination deleted), update children
            self._update_prefix_children(children_prefixes)
        return deleted

    def _update_prefix_children(self, children_prefixes):
        """
        Refresh children next hops
        :param children_prefixes: (list) all the children at each level of a given prefix
        :return:
        """
        for child_prefix in children_prefixes:
            child_prefix_dest = self.destinations.get(child_prefix)
            self.fib.put_route(child_prefix_dest.best_route)

    def _delete_superfluous_children(self, prefix_dest, children_prefixes):
        """
        Delete superfluous children of the given prefix from the RIB and the FIB when it is unreachable
        :param prefix_dest: (Destination) object to check for superfluous children
        :param children_prefixes: (list) children of given prefix
        :return: (boolean) if children of the given prefix have been removed or not
        """
        best_route = prefix_dest.best_route
        if (not best_route.positive_next_hops and best_route.negative_next_hops) and not best_route.next_hops:
            for child_prefix in children_prefixes:
                self.destinations.delete(child_prefix)
                self.fib.delete_route(child_prefix)
            return True

        return False

    def __str__(self):
        rep_str = ""
        for prefix in self.destinations:
            rep_str += str(self.destinations.get(prefix))
        return "RIB:\n%s\n\nFIB:\n%s" % (rep_str, str(self.fib))

    def __repr__(self):
        return str(self)
