#!/usr/bin/env python3

import argparse
import logging
import sys

from exitstatus import ExitStatus
import numpy as np
from scipy import optimize
from qiskit import Aer
from qiskit.quantum_info import random_statevector

from task1.circuit import build_circuit
from task1.optimizer import objective_function

# Define all command line arguments
parser = argparse.ArgumentParser(description='QOSF mentorship program task 1')
parser.add_argument('maxL', help='The maximum number of layers to simulate', type=int)
parser.add_argument('outfile', help='A filename to write the results to. Results are stored as a (iteration, number of layers, minimum of metric) CSV file')
parser.add_argument('-m', '--minL', help="The number of layers to start with (default: 1)", type=int, default=1)
parser.add_argument('-i', '--iterations', help="The number of iterations to simulate (i.e. the number of random statevectors, default: 1)", type=int, default=1)
parser.add_argument('-o', '--odd', help="The parameterized gate to use in the odd layers. One of rx, ry, rz, u1, u2, u3, phase (default: rx)", type=str, default='rx', choices=['rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'phase'])
parser.add_argument('-e', '--even', help="The parameterized gate to use in the even layers. One of rx, ry, rz, u1, u2, u3, phase (default: rz)", type=str, default='rz', choices=['rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'phase'])
parser.add_argument('-s', '--seed', help="Set the random number generators seed", type=int)
parser.add_argument('-l', '--logfile', help='A filename to store debugging messages to', type=str)
parser.add_argument('-v', '--verbose', help='Print debugging messages to stdout', action='store_true', default=False)

def main():
    # Parse all command line arguments
    args = parser.parse_args()
    maxL = args.maxL
    minL = args.minL
    outfile = args.outfile
    odd_gates = args.odd
    even_gates = args.even
    seed = args.seed
    logfile = args.logfile
    verbose = args.verbose
    iterations = args.iterations

    # Define the logger
    logger = logging.getLogger('task1')
    if logfile:
        logger.addHandler(logging.FileHandler(logfile))
    if verbose:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    np.random.seed(seed=seed)

    backend = Aer.get_backend('statevector_simulator')

    for i in range(iterations):
        random_vector = random_statevector(dims=(2,2,2,2), seed=seed)

        for j in range(minL, maxL + 1):
            circuit = build_circuit(j, odd_gates=odd_gates, even_gates=even_gates)

            res =  optimize.minimize(fun=objective_function, 
                                     x0=np.random.rand(len(circuit.parameters))*2*np.pi, 
                                     args=(circuit, random_vector, backend),
                                     jac='2-point',
                                     bounds=[(0, 2*np.pi)]*len(circuit.parameters),
                                     callback=lambda v: v % (2*np.pi))

            logger.debug(f'Iteration: {i + 1}')
            logger.debug(f'Goal statevector: {random_vector.data}')    
            logger.debug(f'Number of layers: {j}')
            logger.debug(f'Odd gates: {odd_gates}')
            logger.debug(f'Even gates: {even_gates}')
            logger.debug(circuit.decompose())
            logger.debug('\nResult')
            logger.debug('====================================================================================')
            logger.debug(f'{res}')
            logger.debug('====================================================================================\n')

            with open(outfile, 'a') as f:
                f.write(f'{i},{j},{res.fun}')
                f.write('\n')
    
    sys.exit(ExitStatus.success)

if __name__ == "__main__":
    main()
