#!/usr/bin/env python3

import argparse

from task3 import circuit

# Define all command line arguments
parser = argparse.ArgumentParser(description='QOSF mentorship program task 3. Read a Quil program and compile it using RXs, RZs and CZs')
parser.add_argument('infile', help='The quil file to read from')
parser.add_argument('-o', help='Optimize the circuit', default=0, action='count')

def main():
    args = parser.parse_args()
    infile = args.infile
    optimize = args.o

    dag = circuit.Circuit.from_quil(infile)
    dag.compile(optimize=optimize)
    dag.to_quil()

if __name__ == "__main__":
    main()