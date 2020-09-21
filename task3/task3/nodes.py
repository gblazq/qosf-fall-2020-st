from typing import Iterable, Optional
import uuid

import numpy as np

class Node(object):
    def __init__(self):
        self._type = None
        self._params = None

    def __eq__(self, other: 'Node') -> bool:
        return self._params == other._params
    
    @property
    def type(self):
        return self._type

    def __hash__(self):
        return hash(self._params)


class Gate(Node):
    def __init__(self, gate: str, qubits: Iterable[int], args: Optional[Iterable[np.float_]] = None) -> None:
        self._type = 'gate'
        self._gate = gate
        self._qubits = tuple(qubits)
        self._id = uuid.uuid4()
        
        if args:
            self._args = (args,)
        else:
            self._args = args
        
        self._params = (self._type, self._gate, self._qubits, self._args, self._id)
    

class Qubit(Node):
    def __init__(self, q: int, side: str):
        self._type = 'qubit'
        self._qubits = (q,)
        self._side = side

        self._params = (self._type, self._qubits, self._side)
