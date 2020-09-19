## Task 2

### Description

For this task, we had to implement a circuit that generates a state with equal probability (50%) of measuring the states |01> and |10> with the following requirements:

- The circuit should consist only of CNOTs, RXs and RYs.
- All parameters should start at 0 or randomly chosen and be variationally optimized.
- Simulations should be done with sampling and noise.

### Implementation

#### The circuit

Let's first reason what is the simplest circuit that can generate the goal state. So far, the only restriction we've been imposed is that the resulting state have 0.5 probability of measuring |01> and |10>. Any state of the form |01> + e^{i \phi}|10> (up to a global phase) will do.

Of course, that's a maximally entangled state, so we'll need a controlled gate to reach it. Therefore, our circuit will need to include at least one CNOT, and in fact only one will suffice. If we can generate the state |10> + e^{i \phi}|11>, a CNOT applied to that state, controlled by the second qubit, will get us the result we want.

We can generate that intermediate state with two rotations, one on each qubit. Basically, we need a rotation of \pi on the first qubit and a rotation of \pi/2 on the first (or any multiple of those angles), and the gates we choose will determine the relative phase. To keep it simple, I'm choosing two rotations around the Y axis, mainly because this way we can keep the relative phase between both states constant at \pm \pi and the coefficients will be real, but any other combination would do.

Therefore, I'm trying to optimize the following circuit:

            ┌──────────────┐        
       q_0: ┤ RY(theta[0]) ├──■───
            ├──────────────┤┌─┴─┐
       q_1: ┤ RY(theta[1]) ├┤ X ├─
            └──────────────┘└───┘

which we know that would yield the desired state with \theta[0] = n \pi/2 and \theta[1] = \pi, with n=1,3,5...

One could think how to make sure we're generating |01> + |10> and not some other state with the same probabilities. The main difficulty here is that we'll be simulating actual measurements, so we won't be able to peek at the coefficients. I can imagine two ways of solving this problem:

1. We can take advantage of our knowledge of the gates and the phases they produce and restrict the first parameter to be in a range that can never introduce a relative phase, say [-pi, pi].
2. We can measure in a basis that includes the state we want to generate as a basis vector. In this case, we can measure in the Bell basis by applying another CNOT and a Hadamard in the q_0 qubit. This would take |01> + |10> to |10>

I've implemented the second option (in this case, I haven't converted the Hadamard to RXs and RYs, and there is no parameter to optimize). Notice that even though I'm using a gate outside the set of gates we've been allowed, this is only to measure in the right basis and it does not take part on the circuit that generates the desired state. Anyway, the first option would work as well.

#### Noise generation

For this task, I'm using qiskit, so I've used one of the noise models that come with it. To be precise, I've simulated all iterations using the noise model from the Vigo chip.

#### The algorithm

There are two key points to consider when implementing the algorithm. First of all, we're going to run all iterations with sampling. Therefore, we'll only have access to the final measurements. Second, in order to variationally find the best parameters, we need to choose a cost function. Taking into account that we'll only know the measured probabilities after each iteration, I've chosen to maximize the loglikelihood of the probability function induced by the state we want to generate, a fair binomial distribution with two possible outcomes.

For measurements in the Bell basis, the cost function is the sum of the absolute value of the expected and measured probabilities.

The variational parameters are found by gradient descent, using qiskit's COBYLA optimizer.

The sketch of the algorithm, without entering on details about the gradient descent method, is as follows:

1. Generate the circuit and the initial random parameters.
2. Run the circuit with the current parameters and the specified number of shots.
3. Measure the results and compute the cost function.
4. Update the parameters using gradient descent (i.e. in the direction in which the cost function is minimized the greatest)
5. Repeat from 2 until convergence.

### Using the program

The code is given as a CLI program. After installing the requirements using `pip install -r requirements.txt` run it with

```bash
main.py -h
usage: main.py [-h] [-s SHOTS [SHOTS ...]] [--seed SEED] [-b] [-l LOGFILE]
               [-v]

QOSF mentorship program task 2

optional arguments:
  -h, --help            show this help message and exit
  -s SHOTS [SHOTS ...], --shots SHOTS [SHOTS ...]
                        Set the number of shots to simulate in each iteration.
                        Can be set more than once
  --seed SEED           Set the seed for the random number generators
  -b, --bell            Measure in the Bell basis
  -l LOGFILE, --logfile LOGFILE
                        A filename to store debugging messages to
  -v, --verbose         Print debugging messages to stdout
```

### Results

I present here the results of the simulations, including the final parameters, the resulting statevector and the results of a simulation with those parameters.

#### Computational basis

In this basis, the circuit, together with the measurements, is:
    
            ┌──────────────┐      ░ ┌─┐   
       q_0: ┤ RY(theta[0]) ├──■───░─┤M├───
            ├──────────────┤┌─┴─┐ ░ └╥┘┌─┐
       q_1: ┤ RY(theta[1]) ├┤ X ├─░──╫─┤M├
            └──────────────┘└───┘ ░  ║ └╥┘
    meas: 2/═════════════════════════╩══╩═
                                     0  1 

The results can be reproduced with

```bash
main.py --shots 1 10 100 1000 --seed 0 -v
```

The resulting parameters are:

| Shots  | \theta[0]   | \theta[1]   |
| ------ | ----------- | ----------- |
| 1      | 0.61340858  | 2.70414933  |
| 10     | 4.07030871  | 2.02967976  |
| 100    | 4.54103787  | -3.73896361 |
| 1000   | -1.55972989 | 3.17478776  |

The coefficients of the resulting state and the fidelity between the goal state and the outcome are (I am only reporting the real part because by choosing two RY gates the coefficients are real):

| Shots  | 00          | 01          | 10          | 11          | F      |
| ------ | ----------- | ----------- | ----------  | ----------  | ------ |
| 1      | 0.20685619  | 0.29472535  | 0.9306212   | 0.06551083  | 0.7507 |
| 10     | -0.23635492 | 0.75945288  | -0.38040109 | 0.47187148  | 0.6496 |
| 100    | 0.18950773  | -0.73114889 | 0.6154916   | -0.22511821 | 0.9067 |
| 1000   | -0.01180046 | -0.70308655 | 0.71091058  | 0.01167059  | 0.9997 |

Here, fidelities are computed with respect to the |01>, |10> linear combination that matches the signs in the outcome state. We can see that the first two simulations, with up to 10 shots, couldn't converge the state to the desired outcome. The simulation with 100 shots takes a huge step towards the desired result compared to the previous ones, and finally with 1000 shots the coefficients are right up to 1e-2. There are two reasons for this behaviour. First, we're only accessing the measurements, and that introduces a stochastic behaviour in the results. Second, all the simulations are being done with noise, which introduces gate and measurement errors. Both factors compromise the convergence towards the true minimum in a random way, and that's the reason why 10 or less shots per iteration aren't enough to properly find the parameters.

Finally, an example of simulated counts are:

| Shots  | 00 | 01  | 10  | 11 |
| ------ | -- | --- | ----| -- |
| 1      | 0  | 0   | 1   | 0  |
| 10     | 1  | 7   | 1   | 1  |
| 100    | 5  | 55  | 37  | 3  |
| 1000   | 27 | 465 | 496 | 12 |


#### Bell basis

In this basis, the circuit with measurements is:
    
            ┌──────────────┐          ┌───┐ ░ ┌─┐   
       q_0: ┤ RY(theta[0]) ├──■────■──┤ H ├─░─┤M├───
            ├──────────────┤┌─┴─┐┌─┴─┐└───┘ ░ └╥┘┌─┐
       q_1: ┤ RY(theta[1]) ├┤ X ├┤ X ├──────░──╫─┤M├
            └──────────────┘└───┘└───┘      ░  ║ └╥┘
    meas: 2/═══════════════════════════════════╩══╩═
                                               0  1 

The results can be reproduced with

```bash
main.py --shots 1 10 100 1000 -b --seed 0 -v
```

The resulting parameters are:

| Shots  | \theta[0]   | \theta[1]   |
| ------ | ----------- | ----------- |
| 1      | 0.61340858  | 2.70414933  |
| 10     | 0.37105329  | 2.42079824  |
| 100    | -4.61373569 | 2.9408969   |
| 1000   | 1.57642555  | 9.41734784  |

The coefficients of the final state and the fidelity are:

| Shots  | 00          | 01          | 10          | 11          | F       |
| ------ | ----------- | ----------- | ----------  | ----------  | ------- |
| 1      | 0.20685619  | 0.29472535  | 0.9306212   | 0.06551083  | 0.75074 |
| 10     | 0.34659428  | 0.1726136   | 0.91969852  | 0.0650505   | 0.59657 |
| 100    | -0.06725871 | -0.73738353 | -0.66800419 | -0.07424424 | 0.98756 |
| 1000   | -0.00261953 | -0.70908932 | -0.70510889 | -0.00263432 | 0.99998 |

Notice how, after measuring in the Bell basis, the state has always the same relative phase between |01> and |10>, so we're actually generating an approximation for |01> + |10>. Regarding the convergence towards the state with respect to the number of shots, we see the same behaviour than before. This time, though, we're obtaining coefficients that are closer to the objective for 100 and 1000 iterations. The reason is that by measuring in the Bell basis we are effectively limiting the effect of one of the stochastic behaviours mentioned earlier, namely the fact that we're approximating a random variable with a set of measurements. In the computational basis, the right state (disregarding noise) will produce counts of the |01> and |10> states that are drawn from a binomial distribution, whereas in the Bell basis, all possible combinations of |01> and |10> counts are measured as a |\psi^+> state.

Finally, the simulated counts are:

| Shots  | 00 | 01 | 10  | 11 |
| ------ | -- | -- | ----| -- |
| 1      | 0  | 0  | 1   | 0  |
| 10     | 2  | 0  | 5   | 3  |
| 100    | 2  | 0  | 98  | 0  |
| 1000   | 26 | 0  | 968 | 6  |

### Conclusions

We have built the circuit and generated the states with equal probability of measuring |01> and |10>. To do so, we have shown what is the simplest circuit that can generate such a state and have chosen an appropriate cost function. The optimization has shown that a small number of shots is not enough to reach a right set of parameters, which we have interpreted as an effect of the two sources of stochastic behaviour in the algorithm: the measurements and the noise. For 1000 iterations, the fidelity between the resulting state and the goal state is 0.9997.

We've also shown how to make sure we are generating the state with a specific relative phase, which has also demonstrated the effect of the difference in the random effect introduced by measuring in different bases. In this case, the fidelity of the final state with 1000 shots per iteration is 0.99998. However, to show this we have needed to introduce a Hadamard gate, although not in the circuit that generates the state, but in the later part, to be able to measure in the basis we wanted to. We have also given another way of ensuring convergence towards the |01> + |10> state by reasoning about the circuit we are using and constraining the parameter ranges.

To keep working on the task, it would be interesting to understand the effect of noise by comparing these results to simulations without noise and simulations with noise mitigation techniques.
