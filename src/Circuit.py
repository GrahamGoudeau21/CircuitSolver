import uuid

import node.junction.Junction as Junction
import node.component.Component_Single_Prong as Component_Single_Prong
import node.component.Component_Two_Prongs as Component_Two_Prongs
import exception.Component_Exception as Component_Exception
import exception.JSON_Exception as JSON_Exception

from Component_Types import Two_Prong_Component_Types, Single_Prong_Component_Types

###############################################################################
class Circuit(object):
    """
    Representation of a circuit. Holds nodes (components and junctions) and 
    information about their connections and properties
    """
    ###########################################################################
    def __init__(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        self.node_map = {}

    ###########################################################################
    def debug_map(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        keys = self.node_map.keys()
        for key in keys:
            print "Node id: " + key + " is " + str(self.node_map[key])
            if not isinstance(self.node_map[key], Junction.Junction) and \
                not isinstance(self.node_map[key], Component_Single_Prong.Open):
                print "\tConnections: " + str(self.node_map[key].junctionA) + " " + str(self.node_map[key].junctionB)
            if isinstance(self.node_map[key], Component_Two_Prongs.Resistor):
                print "\tResistance: " + str(self.node_map[key].resistance)
            if isinstance(self.node_map[key], Junction.Junction):
                for c in self.node_map[key].connections:
                    print "\tjunction connection id: " + str(c.get_id())
            if isinstance(self.node_map[key], Component_Single_Prong.Open):
                print "\tConnection: " + str(self.node_map[key].junction)

    ###########################################################################
    def __get_unique_id(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        return uuid.uuid4()

    ###########################################################################
    def add_nodes_to_map(self, nodes):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        for node in nodes:
            self.node_map[str(node.get_id())] = node

    ###########################################################################
    def add_node_to_map(self, node):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        self.node_map[str(node.get_id())] = node

    ###########################################################################
    def remove_nodes_from_map(self, ids):
        ret = []
        for id in ids:
            try:
                node = self.node_map.pop(str(id))
                ret.append(node)
            except KeyError:
                continue

        return ret

    ###########################################################################
    def remove_node_from_map(self, id):
        try:
            return self.node_map.pop(str(id))
        except KeyError:
            return None

    ###########################################################################
    def get_node(self, id):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        return self.node_map.get(str(id), None)

    ###########################################################################
    # expects a member of the two prong type enum
    # creates new junctions and assigns IDs if not provided them
    def add_two_prong_component(self, component_type,
                        value, junction_id1=None, junction_id2=None):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        # raise exception if provided an id, but it is unrecognized
        if junction_id1 is not None and str(junction_id1) not in self.node_map:
            raise Component_Exception.UnrecognizedIdError(junction_id1)
        if junction_id2 is not None and str(junction_id2) not in self.node_map:
            raise Component_Exception.UnrecognizedIdError(junction_id2)

        component_id = self.__get_unique_id()
        if junction_id1 is None:
            junction_id1 = self.__get_unique_id()
        if junction_id2 is None:
            junction_id2 = self.__get_unique_id()

        if component_type == Two_Prong_Component_Types.RESISTOR:
            class_type = Component_Two_Prongs.Resistor
        elif component_type == Two_Prong_Component_Types.CAPACITOR:
            class_type = Component_Two_Prongs.Capacitor
        else:
            raise Component_Exception.UnknownComponentError()

        component = class_type(component_id, value, junction_id1, junction_id2)
        junction_node1 = self.get_node(junction_id1)
        if junction_node1 is None:
            junction_node1 = Junction.Junction(junction_id1)
        junction_node1.add_connection(component)

        junction_node2 = self.get_node(junction_id2)
        if junction_node2 is None:
            junction_node2 = Junction.Junction(junction_id2)
        junction_node2.add_connection(component)

        self.add_nodes_to_map([component, junction_node1, junction_node2])

        # return a tuple of the junctions that were used
        return (junction_id1, junction_id2)

    ###########################################################################
    # expects a member of the single prong type enum
    # creates a new junction and assigns an ID if not provided one
    def add_single_prong_component(self, component_type, junction_id=None):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        # raise exception if provided an id, but it is unrecognized
        if junction_id is not None and str(junction_id) not in self.node_map:
            raise Component_Exception.UnrecognizedIdError(junction_id)

        id = self.__get_unique_id()
        if junction_id is None:
            junction_id = self.__get_unique_id()

        if component_type == Single_Prong_Component_Types.OPEN:
            class_type = Component_Single_Prong.Open
        else:
            raise Component_Exception.UnknownComponentError()

        component = class_type(id, junction_id)
        junction_node = self.get_node(junction_id)
        if junction_node is None:
            junction_node = Junction(junction_id)
        junction_node.add_connection(component)

        self.add_nodes_to_map([component, junction_node])

        # return the ID of the junction that was used
        return junction_id

    ###########################################################################
    def connect_junction_to_node(self, junctionA, node):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        j1 = self.get_node(str(junctionA))
        if j1 is None:
            raise Component_Exception.UnrecognizedIdError(j1)
        j1.add_connection(node)

    ###########################################################################
    # expects the ids of both junctions, raises KeyException if an invalid ID
    def combine_junctions(self, junctionA, junctionB):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        j1 = self.get_node(junctionA)
        j2 = self.get_node(junctionB)

        if j1 is None:
            raise Component_Exception.UnrecognizedIdError(j1)
        if j2 is None:
            raise Component_Exception.UnrecognizedIdError(j2)

        j3 = Junction.Junction(self.__get_unique_id())
        j3.connections = j1.connections + j2.connections
        for node in j3.connections:
            if isinstance(node, Component_Two_Prongs.Component_Two_Prongs):
                if node.junctionA == junctionA or node.junctionB == junctionA:
                    node.junctionA = j3.get_id()
                if node.junctionA == junctionB or node.junctionB == junctionB:
                    node.junctionB = j3.get_id()
            elif isinstance(node, Component_Single_Prong.Component_Single_Prong):
                if node.junction == junctionA or node.junction == junctionB:
                    node.junction = j3.get_id()
            else:
                raise Component_Exception.UnknownComponentError()

        self.remove_nodes_from_map([j1, j2])
        self.add_node_to_map(j3)

        return j3.get_id()

    ###########################################################################
    def get_all_junctions(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURNS
        """
        keys = self.node_map.keys()
        return [self.node_map[x] for x in keys if isinstance(self.node_map[x], Junction)]

###############################################################################
# run the file as a standalone script to run the test
if __name__ == "__main__":
    circuit = Circuit()
    # returns the ids of the two junctions it creates
    j1, j2 = circuit.add_two_prong_component(Two_Prong_Component_Types.RESISTOR, 5)
    circuit.add_two_prong_component(Two_Prong_Component_Types.CAPACITOR, 10, j1, j2)
    _, y = circuit.add_two_prong_component(Two_Prong_Component_Types.RESISTOR, 100, j1)
    circuit.add_single_prong_component(Single_Prong_Component_Types.OPEN, y)
    circuit.debug_map()

