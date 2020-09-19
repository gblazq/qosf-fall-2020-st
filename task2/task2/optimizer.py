from typing import List, Optional

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit import Aer, execute
from qiskit.providers.aer import AerProvider
from qiskit.providers.aer.noise import NoiseModel
from scipy.stats import binom

def metric_computational(counts: np.ndarray, shots: int) -> np.float_:
    """The negative loglikelihood of the 01 and 10 counts assuming a 
    binomial probability distribution with equal probability

    Args:
        counts: a dict of counts with measurements as strings
    
    Returns:
        the metric value
    """
    return -binom.logpmf([(counts.get('01') or 0), (counts.get('10') or 0)], n=shots, p=0.5).sum()

def metric_bell(counts: np.ndarray, shots: int) -> np.float_:
    """The sum of the absolute value of the differences between the goal probabilities
    and the probabilities we measured
    
    Args:
        counts: a dict of counts with measurements as strings
    
    Returns: 
        the metric value
    """
    return ((counts.get('00') or 0) + (shots - (counts.get('10') or 0)) + (counts.get('01') or 0) + (counts.get('11') or 0)) / shots

def execute_circuit(circuit: QuantumCircuit, params: np.ndarray, backend: AerProvider, shots: Optional[int] = 1, 
                    noise_model: Optional[NoiseModel] = None, coupling_map: Optional[List] = None, basis_gates: Optional[List[str]] = None):
    """Execute a circuit in a backend with the given parameters
    
    Args:
        circuit: the quantum circuit to execute
        params: the gate parameters
        backend: a backend to execute the circuit in
        shots: the number of shots to simulate

    Returns:
        the execute job
    """
    # QuantumCircuit.parameters is a set, so the order is not guaranteed
    # We sort them using their names to keep an order
    parameters = list(circuit.parameters) 
    parameters.sort(key=lambda x: x.name)
    bound_parameters = dict(zip(parameters, params))

    job = execute(circuit, backend, shots=shots, parameter_binds=[bound_parameters], seed_simulator=np.random.randint(1000), seed_transpiler=np.random.randint(1000),
                  noise_model=noise_model, coupling_map=coupling_map, basis_gates=basis_gates)
    return job

def objective_function(params: np.ndarray, circuit: QuantumCircuit, shots: int, backend: AerProvider, bell_basis: bool,
                      noise_model: NoiseModel, coupling_map: List, basis_gates: List[str]) -> np.float_:
    """The function to minimize

    It executes the circuit and returns the metric in the selected basis

    Args:
        params: the current set of gate parameters
        circuit: the quantum circuit to use
        shots: the number of shots to simulate
        backed: a backend to execute the circuit in
        bell_basis: whether to measure in the Bell basis
    
    Returns:
        the metric value of the measurements of the current circuit with respect to the goal measurements
    """
    counts = execute_circuit(circuit, params, backend, shots, noise_model, coupling_map, basis_gates).result().get_counts()

    if bell_basis:
        metric = metric_bell(counts, shots)
    else:
        metric = metric_computational(counts, shots)

    return metric