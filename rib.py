import pytricia

from route import Route
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
        self.fib.put_route(prefix_dest.best_route)
        # This condition is triggered only if all the next hops are added as negative next hops!
        # if not prefix_dest.best_route.next_hops:
        #     # Assert that there are no positive next hops for the prefix
        #     assert not prefix_dest.best_route.positive_next_hops
        #     # Since the given prefix is unreachable, remove superfluous children routes of the
        #     # prefix from the RIB and the FIB
        #     for child_prefix in self.destinations.children(prefix_dest.prefix):
        #         self.destinations.delete(child_prefix)
        #         self.fib.delete_route(child_prefix)
        #     # We must not update the FIB for the children of this prefix, so return
        #     return
        # Force recomputing of children next hops since they need to add new next hops in their
        # sets. After recomputing, reassign the child computed next hops to the FIB.
        # N.B.: self.destinations.get(child_prefix) contains all the children at each level of the current prefix, so
        # recursion is not needed
        for child_prefix in self.destinations.children(prefix_dest.prefix):
            child_prefix_dest = self.destinations.get(child_prefix)
            self.fib.put_route(child_prefix_dest.best_route)

    def delete_route(self, prefix, next_hops, disagg_type=True):
        """
        Removes a set of next hops for a given prefix.
        :param prefix: IP prefix for which we want to remove next hops
        :param next_hops: set of next hops we want to remove for the given prefix
        :param disagg_type: True if positive disaggregation, False if negative disaggregation
        :return:
        """
        # Get the Destination object associated to the given prefix
        prefix_dest = self.destinations.get(prefix)
        if disagg_type:
            self._delete_pos_disagg(prefix_dest, next_hops)
        else:
            self._delete_neg_disagg(prefix_dest, next_hops)

    def _delete_pos_disagg(self, prefix_dest, next_hops):
        """
        Removes positive disaggregated next hops for the given Destination object
        :param prefix_dest: the Destination object of a prefix
        :param next_hops: set of next hops we want to remove for the given prefix
        :return:
        """
        # Remove positive disaggregated next hops from the positive next hops set of the given
        # Destination object
        prefix_dest.remove_positive_next_hops(next_hops)
        # Get all child prefixes
        children_prefixes = self.destinations.children(prefix_dest.prefix)
        # Remove superfluous routes if needed
        # A route is superfluous if the set of next hops is empty
        if not self._delete_pos_disagg_superfluous_prefix(prefix_dest):
            # If there are no superfluous routes, update the next hops in the FIB
            self.fib.routes[prefix_dest.prefix] = prefix_dest.get_next_hops
        # Update the next hops for each child
        for child_prefix in children_prefixes:
            child_prefix_dest = self.destinations.get(child_prefix)
            child_prefix_dest.remove_positive_next_hops(next_hops)
            if not self._delete_pos_disagg_superfluous_prefix(child_prefix_dest):
                self.fib.routes[child_prefix] = child_prefix_dest.get_next_hops

    def _delete_neg_disagg(self, prefix_dest, next_hops):
        """
        Removes negative disaggregated next hops for the given Destination object
        :param prefix_dest: the Destination object of a prefix
        :param next_hops: set of next hops we want to remove for the given prefix
        :return:
        """
        # Remove negative disaggregated next hops from the positive next hops set of the given
        # Destination object
        prefix_dest.remove_negative_next_hops(next_hops)
        # Get all child prefixes
        children_prefixes = self.destinations.children(prefix_dest.prefix)
        # Remove superfluous routes if needed
        # A route is superfluous if the set of next hops is equal to the set of next hops of the
        # parent prefix
        if not self._delete_neg_disagg_superfluous_prefix(prefix_dest):
            # If there are no superfluous routes, update the next hops in the FIB
            self.fib.routes[prefix_dest.prefix] = prefix_dest.get_next_hops
        # Update the next hops for each child
        for child_prefix in children_prefixes:
            child_prefix_dest = self.destinations.get(child_prefix)
            child_prefix_dest.remove_negative_next_hops(next_hops)
            if not self._delete_neg_disagg_superfluous_prefix(child_prefix_dest):
                self.fib.routes[prefix_dest.prefix] = prefix_dest.get_next_hops

    def _delete_pos_disagg_superfluous_prefix(self, prefix_dest):
        """
        Removes superfluous routes if needed. A route is superfluous if the set of next
        hops is empty
        :param prefix_dest: the Destination object of a prefix
        :return: True if the prefix is superfluous and has been removed, else False
        """
        if not prefix_dest.get_next_hops:
            self.destinations.delete(prefix_dest.prefix)
            del self.fib.routes[prefix_dest.prefix]
            return True

        return False

    def _delete_neg_disagg_superfluous_prefix(self, prefix_dest):
        """
        Removes superfluous routes if needed. A route is superfluous if the set of next hops is
        equal to the set of next hops of the parent prefix
        :param prefix_dest: the Destination object of a prefix
        :return: True if the prefix is superfluous and has been removed, else False
        """
        parent_prefix = self.destinations.parent(prefix_dest.prefix)
        assert parent_prefix is not None
        parent_prefix_dest = self.destinations.get(parent_prefix)
        if prefix_dest.get_next_hops == parent_prefix_dest.get_next_hops:
            self.destinations.delete(prefix_dest.prefix)
            del self.fib.routes[prefix_dest.prefix]
            return True

        return False

    def get_rib_fib_representation(self):
        print("--------------------- RIB ---------------------------")
        for prefix in self.destinations.keys():
            print(self.destinations.get(prefix))
        print("--------------------- FIB ---------------------------")
        for prefix, dests in self.fib.routes.items():
            print(prefix, "\t", dests)
        print("-----------------------------------------------------")
