from typing import Optional

from networkx import DiGraph

from task3.nodes import Gate

def h_to_rzrxrz(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'H':
        return None
    else:
        first = Gate('RZ', gate._qubits, 'pi/2')
        second = Gate('RX', gate._qubits, 'pi/2')
        third = Gate('RZ', gate._qubits, 'pi/2')
        return DiGraph([(first, second), (second, third)])

def x_to_rx(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'X':
        return None
    else:
        graph = DiGraph()
        graph.add_node(Gate('RX', gate._qubits, 'pi'))
        return graph

def y_to_ry(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'Y':
        return None
    else:
        graph = DiGraph()
        graph.add_node(Gate('RY', gate._qubits, 'pi'))
        return graph

def z_to_rz(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'Z':
        return None
    else:
        graph = DiGraph()
        graph.add_node(Gate('RZ', gate._qubits, 'pi'))
        return graph

def ry_to_rxrzrx(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'RY':
        return None
    else:
        first = Gate('RX', gate._qubits, 'pi/2')
        second = Gate('RZ', gate._qubits, *gate._args)
        third = Gate('RX', gate._qubits, '-pi/2')
        return DiGraph([(first, second), (second, third)])

def cnot_to_hczh(gate: Gate) -> Optional[DiGraph]:
    if gate._gate != 'CNOT':
        return None
    else:
        first = Gate('H', gate._qubits[1:])
        second = Gate('CZ', gate._qubits)
        third = Gate('H', gate._qubits[1:])
        return DiGraph([(first, second), (second, third)])

translators = [h_to_rzrxrz, x_to_rx, y_to_ry, z_to_rz, ry_to_rxrzrx, cnot_to_hczh]
