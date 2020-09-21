#!/usr/bin/env python3

import argparse
import sys

from exitstatus import ExitStatus

from task3 import circuit

# Define all command line arguments
parser = argparse.ArgumentParser(description='QOSF mentorship program task 3. Read a Quil program and compile it using RXs, RZs and CZs')
parser.add_argument('infile', help='The Quil file to read from')
parser.add_argument('-o', help='Optimize the circuit (up to two levels)', default=0, action='count')

def main():
    args = parser.parse_args()
    infile = args.infile
    optimize = args.o

    dag = circuit.Circuit.from_quil(infile)
    dag.compile(optimize=optimize)
    dag.to_quil()

    sys.exit(ExitStatus.success)

if __name__ == "__main__":
    main()