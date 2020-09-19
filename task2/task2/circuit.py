from typing import Optional

from qiskit.circuit import QuantumCircuit, ParameterVector

def build_circuit(measure: Optional[str] = None) -> QuantumCircuit:
    """Create the following parameterized quantum circuit

            ┌──────────────┐      ░ ┌─┐   
       q_0: ┤ RY(theta[0]) ├──■───░─┤M├───
            ├──────────────┤┌─┴─┐ ░ └╥┘┌─┐
       q_1: ┤ RY(theta[1]) ├┤ X ├─░──╫─┤M├
            └──────────────┘└───┘ ░  ║ └╥┘
    meas: 2/═════════════════════════╬══╬═
                                     0  1 

    Measurements are either in the computational basis or
    in the Bell basis

    Args:
        measure: the basis in which to measure. If 'bell', measurements
                 will be in the Bell basis, any other value will measure
                 in the computational basis. None means no measurement (default)

    Returns:
        The quantum circuit
    """
    circuit = QuantumCircuit(2, name='task2')
    params = ParameterVector(name='theta', length=2)

    circuit.ry(params[0], 0)
    circuit.ry(params[1], 1)
    circuit.cx(0, 1)

    if measure:
        if measure == 'bell':
            circuit.cx(0, 1)
            circuit.h(0)          
        circuit.measure_all()

    return circuit
