## Task 3

### Description

In this task, we had to write a compiler that takes a quantum circuit as an input and produces an equivalent quantum circuit consisting only on RX, RZ and CZ gates.

The input circuit can have gates from the following set: I, H, X, Y, Z, RX, RY, RZ, CNOT, CZ.

### Implementation

I have implemented a CLI program that takes a Quil[1] program as an input and compiles the circuit to the restricted set of gates. The compiler actually implements a small subset of the Quil instructions, namely the previously mentioned gates (I, H, X, Y, Z, RX, RY, RZ, CNOT, CZ). 

Doing the basic version of the task is quite easy, as we only have to store the equivalences of each gate in terms of RX, RZ and CZ. However, if we aim to be able to do any kind of optimization, we need to use a data structure that allows us to traverse the circuit and find suitable translations or optimizations. For this reason, my compiler uses a direct acyclic graph (DAG) to represent the quantum circuit. DAGs are common data structures for compilers, as they allow to store the action flow in an efficient way. The [circuit.py](task3/circuit.py) file contains the `Circuit` class, which can parse a Quil program into a DAG, compile the circuit by applying suitable translations and optimizations and print the output as another Quil program.

To store a circuit as a DAG, I use two types of nodes, which can be found at [nodes.py](task3/nodes.py). The `Node` class implements the basic structure of a node. Any node with input and output edges must represent a gate. Gate nodes are instances of the `Gate` class, which stores attributes such as the gate type, any parameters, and the qubits the gate is applied to. To easily traverse the DAG, it also includes in and out qubits, which are instances of the `Qubit` class.

The basic translators (which may introduce global phases) can be found at [translators.py](task3/translators.py). They are functions that take nodes as input and return a translation to the restricted set of gates if the gate is of a certain type.

The structure of a compilation is as follows (assuming we already have a DAG representing the circuit):

1. Traverse all the gates, one by one.
2. For each gate, find any suitable translation and apply it. Applying a translation means replacing the node with the gate with a subgraph that represents the same gate with the restricted set of gates.
3. Repeat until we reach a fixed point.

Subgraph replacement is done by the `replace_subgraph` method of the `Circuit` instances.

#### Using the program

The entry point of the program is [main.py](main.py).

```python
main.py --help

usage: main.py [-h] infile

QOSF mentorship program task 3. Read a Quil program and compile it using RXs,
RZs and CZs

positional arguments:
  infile      The quil file to read from

optional arguments:
  -h, --help  show this help message and exit
```

### Example results

As an example, the following [example circuit](test.quil)

```
H 0
H 1
H 2
H 3
CNOT 0 1
CNOT 0 2
CNOT 0 3
RX(1.00) 1
RY(pi) 3
RZ(pi/2) 2
X 0
Y 0
Z 1
CNOT 2 1
H 2
```

is compiled, with the command `main.py test.quil` to

```
RZ(pi/2) 0
RX(pi/2) 0
RZ(pi/2) 0
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
CZ 0 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RX(1.00) 1
RZ(pi) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
CZ 0 2
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
CZ 2 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
CZ 0 3
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
RX(pi) 0
RX(pi/2) 0
RZ(pi) 0
RX(-pi/2) 0
RX(pi/2) 3
RZ(pi) 3
RX(-pi/2) 3
```

### Analyzing the overhead

There are different metrics one could use to quantify the overhead of a circuit. The most obvious one is, probably, the number of gates or gate depth. Clearly, by restricting the set of gates in the output circuit, the compilation will introduce more gates than in the input circuit. There's no room for optimizing the translators, as they are already use the minimum number of gates (in some cases there are alternative ways to write a given unitary with RXs, RZs and CZs, but I have chosen the translations with the minimum gate depth). Counting each translation gate depth, our basic compiler will produce a circuit with

g(NH, NX, NY, NZ, NRX, NRY, NRZ, NCZ, NCNOT, NI) = 3(NH + NY + NRY) + 7NCNOT + NX + NZ + NRX + NRZ + NCZ + NI

gates, where NH is the number of H gates in the input circuit, etc. The gate depth overhead with respect to the input circuit would be

g(NH, NX, NY, NZ, NRX, NRY, NRZ, NCZ, NCNOT, NI) = 2(NH + NY + NRY) + 6NCNOT

For example, the test Quil program consisted on 15 gates and its compilation results in 53 gates, adding 38 gates with respect to the original circuit.

How could we simplify the output with respect to gate depth? There are several simple operations we can perform:

- Collect consecutive rotations around the same axis and acting on the same qubit and replace them by a single rotation.
- Detect commuting operations and commute them to see if that enables other possible optimizations.
- Find groups of rotations on a qubit, decompose them into their Euler angles, and translate that general rotation to RXs and RZs. I think this could work if there are a great number of consecutive rotations in a qubit.
- Find consecutive, cancelling operations and delete them (for example, two consecutive Hadamards or CNOTs on the same qubits).

As an example, I have implemented the first optimization (the angle sums are explicit to show the changes). This example can be run with `main.py test.quil -o`. The algorithm for the optimization is equivalent to the translation algorithm, and it works by traversing the DAG and finding consecutive pairs of gates that may be optimized. The result is

```
RZ(pi/2) 0
RX(pi/2) 0
RZ(pi/2) 0
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2 + pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
CZ 0 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RX(1.00) 1
RZ(pi + pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2 + pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
CZ 0 2
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2 + pi/2) 2
CZ 2 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2 + pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
CZ 0 3
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
RX(pi + pi/2) 0
RZ(pi) 0
RX(-pi/2) 0
RX(pi/2) 3
RZ(pi) 3
RX(-pi/2) 3
```

This optimization reduces the gate depth to 47. Notice that the algorithm was able to detect optimizations even though in the previous, unoptimized version, the gates were not consecutively printed. This is due to the fact that we are using a DAG and we are able to traverse it to find adjacent gates instead of 'reading' a circuit sequentially.

Another example is the implementation of an optimizer that detects two consecutive H gates and returns the identity (here, I have made the identity gate explicit to see the result, it can be seen in the fourth line). This optimizer together with the previous one can be run with `main.py test.quil -oo`, and they reduce the gate depth to 42.

```
RZ(pi/2) 0
RX(pi/2) 0
RZ(pi/2) 0
I 1
CZ 0 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RX(1.00) 1
RZ(pi + pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2 + pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
CZ 0 2
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2 + pi/2) 2
CZ 2 1
RZ(pi/2) 1
RX(pi/2) 1
RZ(pi/2) 1
RZ(pi/2) 2
RX(pi/2) 2
RZ(pi/2) 2
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2 + pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
CZ 0 3
RZ(pi/2) 3
RX(pi/2) 3
RZ(pi/2) 3
RX(pi + pi/2) 0
RZ(pi) 0
RX(-pi/2) 0
RX(pi/2) 3
RZ(pi) 3
RX(-pi/2) 3
```

Gate depth is, however, not the only overhead metric we can consider. There are other important limitations in quantum circuits, most of them depending on the specific chip the circuit will run in. For example, we could be interested in reducing the distance between qubits in controlled gates, because the target chip does not allow to control arbitrary qubits. One way to measure that metric without resorting to specific chip architectures would be to weight every controlled operation by the distance between qubits. In any case, to optimize any suitable metric we would need to either change the layout of the circuit (e.g. by swapping two circuit qubits at the very beginning) or apply swaps during the circuit. Having a map of the chip architecture to know which qubits can be control/controlled would help to make a compilation for a specific chip.

Also, we could consider some metric that relates the gate fidelity to the qubit we are manipulating, in order to reduce noise effects; or a metric related to the gate depth by 'wire' if the device has different coherent times for different qubits. In that case, it could be useful to have logical qubits with less gates in physical qubits with smaller coherence times. My guess is that this two metrics should specially important in NISQ devices.

### Conclusions

I have implemented a very basic compiler using a DAG to represent quantum circuits. The compiler gets a Quil program as input and prints an equivalent Quil program, using only the specified subset of gates.

As we have seen, the basic translations produce an overhead in different metrics that we can address with optimization techniques. The most simple of this metrics is gate depth. I have proposed several simple techniques to reduce the gate depth, and I have implemented the simplest ones to show their effect. To this end, the choice of a DAG as the data structure has been quite useful.

To continue with the task, it would be interesting to implement some of the other optimization techniques, like the approximation of single qubit rotations using Euler angles, which may supersede the optimizations I have implemented. Also, I would consider adding other overhead metrics like the ones proposed.

### References

[1] : Smith, Robert S.; Curtis, Michael J.; Zeng, William J. A Practical Quantum Instruction Set Architecture. [https://arxiv.org/abs/1608.03355](https://arxiv.org/abs/1608.03355)