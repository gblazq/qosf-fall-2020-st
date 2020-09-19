#!/usr/bin/env python3

import argparse
from functools import partial
import logging
import sys

from exitstatus import ExitStatus
import numpy as np
from qiskit import Aer
from qiskit.aqua.components.optimizers import COBYLA
from qiskit.providers.aer.noise import NoiseModel
from qiskit.test.mock import FakeVigo

from task2.circuit import build_circuit
from task2.optimizer import objective_function, execute_circuit

# Define all command line arguments
parser = argparse.ArgumentParser(description='QOSF mentorship program task 2')
parser.add_argument('-s', '--shots', help="Set the number of shots to simulate in each iteration. Can be set more than once", nargs='+', type=int, default=1000)
parser.add_argument('--seed', help="Set the seed for the random number generators", type=int)
parser.add_argument('-b', '--bell', help="Measure in the Bell basis", action='store_const', const='bell', default='computational')
parser.add_argument('-l', '--logfile', help='A filename to store debugging messages to', type=str)
parser.add_argument('-v', '--verbose', help='Print debugging messages to stdout', action='store_true', default=False)

def main():
    # Parse all command line arguments
    args = parser.parse_args()
    shots = args.shots
    seed = args.seed
    basis = args.bell
    logfile = args.logfile
    verbose = args.verbose

    # Define the logger
    logger = logging.getLogger('task2')
    if logfile:
        logger.addHandler(logging.FileHandler(logfile))
    if verbose:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    np.random.seed(seed=seed)

    # Get the noise model
    device_backend = FakeVigo()
    noise_model = NoiseModel.from_backend(device_backend)
    coupling_map = device_backend.configuration().coupling_map
    basis_gates = noise_model.basis_gates

    backend = Aer.get_backend('qasm_simulator')
    statevector_backend = Aer.get_backend('statevector_simulator')

    circuit = build_circuit(measure=basis)
    unmeasured_circuit = build_circuit(measure=None)

    # qiskit's COBYLA can't take args to pass to the objective function, so we freeze them with functools.partial
    optimizer = COBYLA(maxiter=1000, tol=1e-8, disp=True)

    for nshots in shots:
        logger.debug('====================================================================================')
        logger.debug(f'\nShots per iteration: {nshots}')
        logger.debug(circuit)

        partial_objective_function = partial(objective_function, circuit=circuit, shots=nshots, backend=backend, bell_basis=(basis == 'bell'),
                                            noise_model=noise_model, coupling_map=coupling_map, basis_gates=basis_gates)
        ret = optimizer.optimize(num_vars=2, objective_function=partial_objective_function, 
                                initial_point=np.random.rand(len(circuit.parameters))*4*np.pi - 2*np.pi)


        params = ret[0]
        logger.debug(f'\nParameters:\n{params}')
        logger.debug(f'\nStatevector:\n{execute_circuit(unmeasured_circuit, params, statevector_backend).result().get_statevector()}')
        logger.debug(f'\nSimulated results:\n{execute_circuit(circuit, params, backend, nshots, noise_model, coupling_map, basis_gates).result().get_counts()}')
        logger.debug('====================================================================================\n')

    sys.exit(ExitStatus.success)

if __name__ == "__main__":
    main()
