from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library.standard_gates import RXGate, RYGate, RZGate, U1Gate, U2Gate, U3Gate, PhaseGate

gate_mapping = {'rx': {'gate': RXGate,
                       'nparams': 1},
                'ry': {'gate': RYGate,
                       'nparams': 1},
                'rz': {'gate': RZGate,
                       'nparams': 1},
                'u1': {'gate': U1Gate,
                       'nparams': 1},
                'u2': {'gate': U2Gate,
                       'nparams': 2},
                'u3': {'gate': U3Gate,
                       'nparams': 3},
                'phase': {'gate': PhaseGate,
                          'nparams': 1}}

def subcircuit_odd(i: int, gate_id: str) -> QuantumCircuit:
    """Create a quantum circuit corresponding to an odd layer:
    
         ┌─────────────┐
    q_0: ┤ Gate(θ_i,1) ├
         ├─────────────┤
    q_1: ┤ Gate(θ_i,2) ├
         ├─────────────┤
    q_2: ┤ Gate(θ_i,3) ├
         ├─────────────┤
    q_3: ┤ Gate(θ_i,4) ├
         └─────────────┘
​    
    Where the gates depend on the gate_id parameter and the θ's are
    vectors of parameters
    
    Args:
        i: the layer number, to name the circuit and the parameters
        gate_id: an identifier of the gate to be used in the layer
    
    Returns:
        The quantum circuit
    """
    circuit = QuantumCircuit(4, name=f'U_{2*i - 1}')
    
    gate = gate_mapping[gate_id]['gate']
    nparams = gate_mapping[gate_id]['nparams']

    params = ParameterVector(name=f'U_{2*i - 1}', length = nparams * 4)
    
    for j in range(4):
        circuit.append(gate(*params[(j * nparams):((j + 1) * nparams)]), [j], [])
    
    return circuit

def subcircuit_even(i: int, gate_id: str) -> QuantumCircuit:
    """Create a quantum circuit corresponding to an even layer:
    
         ┌─────────────┐
    q_0: ┤ Gate(θ_i,1) ├─■──■──■──────────
         ├─────────────┤ │  │  │          
    q_1: ┤ Gate(θ_i,2) ├─■──┼──┼──■──■────
         ├─────────────┤    │  │  │  │    
    q_2: ┤ Gate(θ_i,3) ├────■──┼──■──┼──■─
         ├─────────────┤       │     │  │ 
    q_3: ┤ Gate(θ_i,4) ├───────■─────■──■─
         └─────────────┘

    where the gates depend on the gate_id parameter and the θ's are
    vectors of parameters
    
    Args:
        i: the layer number, to name the circuit and the parameters
        gate_id: an identifier of the gate to be used in the layer
    
    Returns:
        The quantum circuit
    """
    circuit = QuantumCircuit(4, name=f'U_{2*i}')

    gate = gate_mapping[gate_id]['gate']
    nparams = gate_mapping[gate_id]['nparams']

    params = ParameterVector(name=f'U_{2*i}', length = nparams * 4)
    
    for j in range(4):
        circuit.append(gate(*params[(j * nparams):((j + 1) * nparams)]), [j], [])

    circuit.cz(0, 1)
    circuit.cz(0, 2)
    circuit.cz(0, 3)
    circuit.cz(1, 2)
    circuit.cz(1, 3)
    circuit.cz(2, 3)
    
    return circuit

def build_circuit(l: int, odd_gates: str, even_gates: str) -> QuantumCircuit:
    """Create a quantum circuit with l total layers. A layer is the concatenation of the odd
    and even parts of a layer

         ┌───────────┐ ┌───────────┐         ┌─────────────────────┐ ┌─────────────────┐
    q_0: ┤0          ├─┤0          ├─       ─┤0                    ├─┤0                ├
         │           │ │           │         │                     │ │                 │
    q_1: ┤1          ├─┤1          ├─       ─┤1                    ├─┤1                ├
         │  U_1(θ_1) │ │  U_2(θ_2) │   ...   │  U_{2l-1}(θ_{2l-1}) │ │  U_{2l}(θ_{2l}) │
    q_2: ┤2          ├─┤2          ├─       ─┤2                    ├─┤2                ├
         │           │ │           │         │                     │ │                 │
    q_3: ┤3          ├─┤3          ├─       ─┤3                    ├─┤3                ├
         └───────────┘ └───────────┘         └─────────────────────┘ └─────────────────┘

    where the θ's are parameter vectors

    Args:
        l: the number of layers
        odd_gates: an identifier of the gate to be used in the odd layers
        even_gates: an identifier of the gate to be used in the even layers

    Returns:
        The quantum circuit
    """
    circuit = QuantumCircuit(4, name=f'{l}')
    
    for i in range(1, l+1):
        odd = subcircuit_odd(i, gate_id=odd_gates).to_instruction()
        even = subcircuit_even(i, gate_id=even_gates).to_instruction()

        circuit.append(odd, [0, 1, 2, 3])
        circuit.append(even, [0, 1, 2, 3])
    
    return circuit