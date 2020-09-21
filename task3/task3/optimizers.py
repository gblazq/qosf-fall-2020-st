from typing import Optional

from networkx import DiGraph

from task3.nodes import Gate

def consecutive_rzs(gate1: Gate, gate2: Gate) -> Optional[DiGraph]:
    if not ((gate1._gate == gate2._gate) and (gate1._qubits == gate2._qubits) and (gate1._gate in ('RX', 'RY', 'RZ'))):
        return None
    else:
        gate = gate1._gate
        arg = gate1._args[0] + ' + ' + gate2._args[0]

        graph = DiGraph()
        graph.add_node(Gate(gate, gate1._qubits, arg))
        return graph

def consecutive_hs(gate1: Gate, gate2: Gate) -> Optional[DiGraph]:
    if not ((gate1._gate == gate2._gate) and (gate1._qubits == gate2._qubits) and (gate1._gate == 'H')):
        return None
    else:
        graph = DiGraph()
        graph.add_node(Gate('I', gate1._qubits))
        return graph

rotation_optimizers = [consecutive_rzs]
cancellation_optimizers = [consecutive_hs]
