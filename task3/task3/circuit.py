import re
from typing import Iterable, List, Optional

import networkx as nx
from networkx.algorithms.dag import lexicographical_topological_sort, topological_sort
import numpy as np

from task3.nodes import Node, Qubit, Gate
from task3.optimizers import rotation_optimizers, cancellation_optimizers
from task3.translators import translators, cnot_to_hczh

parser_regex = r'([a-zA-Z]+)(?:\(([0-9\.]+)\))? ([\d ]+)'

class Circuit(object):
    def __init__(self, dag: nx.DiGraph = None) -> None:
        self._dag = dag
    
    @staticmethod
    def from_quil(filename: str) -> 'Circuit':
        dag = nx.DiGraph()

        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                parsed_line = re.match(r'([a-zA-Z0-9]+)(?:\((.+)\))? ([\d ]+)', line)
                operator, argument, qubits = parsed_line.groups()

                qubits = tuple(int(qubit) for qubit in qubits.split(' '))

                # TODO: check values

                operator_node = Gate(operator, qubits, argument)

                for qubit in qubits:
                    out_qubit = Qubit(qubit, side='out')
                    if out_qubit not in dag:
                        dag.add_edge(Qubit(qubit, side='in'), out_qubit, qubit=qubit)
                
                    previous_node = next(dag.predecessors(out_qubit))
                    dag.remove_edge(previous_node, out_qubit)
                    dag.add_edge(previous_node, operator_node, qubit=qubit)
                    dag.add_edge(operator_node, out_qubit, qubit=qubit)

        return Circuit(dag=dag)

    def to_quil(self, filename: str = None) -> None:
        if filename:
            #write to file
            pass
        else:
            for node in lexicographical_topological_sort(self._dag, key=lambda node: node._qubits):
                if node.type != 'gate':
                    continue
                if node._args:
                    print(f"{node._gate}({','.join(node._args)}) {' '.join([str(qubit) for qubit in node._qubits])}")
                else:
                    print(f"{node._gate} {' '.join([str(qubit) for qubit in node._qubits])}")

    def replace_subgraph(self, nodes: Iterable[Node], replacement: nx.DiGraph) -> None:
        sorted_dag = list(topological_sort(self._dag))
        sorted_nodes = sorted(nodes, key=lambda node: sorted_dag.index(node))

        sorted_replacement = list(topological_sort(replacement))

        self._dag.update(replacement)

        predecessors = list(self._dag.predecessors(sorted_nodes[0]))
        
        for predecessor in predecessors:
            self._dag.add_edge(predecessor, sorted_replacement[0])
            self._dag.remove_edge(predecessor, sorted_nodes[0])
        
        successors = list(self._dag.successors(sorted_nodes[-1]))

        for successor in successors:
            self._dag.add_edge(sorted_replacement[-1], successor)
            self._dag.remove_edge(sorted_nodes[-1], successor)
        
        self._dag.remove_nodes_from(nodes)


    def compile(self, optimize: int = 0) -> None:
        previous_dag = nx.DiGraph()

        while not nx.is_isomorphic(previous_dag, self._dag):
            previous_dag = self._dag.copy()
            
            if optimize >= 1:
                self.translate([cnot_to_hczh])

            if optimize > 0:
                optzs = rotation_optimizers
                if optimize >= 2:
                    optzs += cancellation_optimizers
                self.optimize(optzs)
            
            self.translate(translators)

    def translate(self, translators: List) -> None:
        for node in topological_sort(self._dag):
            if node.type != 'gate':
                continue
            possible_translations = [f(node) for f in translators]
            possible_translations = list(filter(None, possible_translations))
            if possible_translations:
                self.replace_subgraph([node], possible_translations[0])
    
    def optimize(self, optimizers: List) -> None:
        #dag = self._dag.copy()

        for node in nx.classes.function.nodes(self._dag):
            for neighbour in self._dag.successors(node):
                if node.type != 'gate' or neighbour.type != 'gate':
                    continue

                possible_optimizations = [f(node, neighbour) for f in optimizers]
                possible_optimizations = list(filter(None, possible_optimizations))
                if possible_optimizations:
                    self.replace_subgraph([node, neighbour], possible_optimizations[0])
                    return
