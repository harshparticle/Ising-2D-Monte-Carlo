# 2D Ising Model Simulation using Monte Carlo

This repository contains Python code for simulating the 2D Ising model using the Metropolis Monte Carlo algorithm. The code investigates various properties of the model, including magnetization, spontaneous magnetization, spin-spin correlations, and column-specific correlations. It also implements Umbrella Sampling and the Weighted Histogram Analysis Method (WHAM) to estimate the minimum magnetization.

## Overview

The Ising model is a simplified representation of magnetic material, where spins on a lattice can be either up (+1) or down (-1). This code simulates the model's behavior under different temperatures and external magnetic fields to study phase transitions and critical phenomena.

## Features

- **Lattice Initialization:** Creates a square lattice with random spin configurations.
- **Energy Calculation:** Determines the energy change when a spin is flipped.
- **Metropolis Algorithm:** Implements the Metropolis Monte Carlo algorithm for spin updates.
- **Magnetization Measurement:** Calculates the average magnetization of the lattice.
- **Correlation Functions:** Computes spin-spin correlations and column-specific correlations.
- **Umbrella Sampling & WHAM:** Uses advanced techniques to estimate minimum magnetization.
- **Visualization:** Generates plots of magnetization vs. field, spontaneous magnetization vs. temperature, correlation vs. temperature, and column-specific correlation vs. separation.

## Requirements

- Python 3.x
- NumPy
- Matplotlib
- Numba
- SciPy

## Installation

To get started, clone this repository to your local machine: 
```
git clone https://github.com/harshparticle/Ising-2D-Monte-Carlo.git
```
This will create a new directory named `Ising-2D-Monte-Carlo` containing all the necessary files.

## Usage

1. Install the required packages: `pip install numpy matplotlib numba scipy`
2. Run the Python script: `python ising_model.py` (Replace `ising_model.py` with the actual script name if different.)

## Results

The simulation generates several plots showcasing the following:

- **Magnetization vs. External Field:** Shows how the magnetization changes with the applied field at different temperatures.
- **Spontaneous Magnetization vs. Temperature:** Illustrates the emergence of spontaneous magnetization below the critical temperature.
- **Correlation vs. Temperature:** Demonstrates the decay of correlations with increasing temperature.
- **Column-Specific Correlation vs. Separation:** Reveals the spatial dependence of correlations within a column.
- **Umbrella Sampling & WHAM:** Presents the estimated minimum magnetization compared to the exact solution.

## Customization

You can modify the following parameters in the code to explore different scenarios:

- **Lattice Size (L):** Controls the dimensions of the lattice.
- **Temperature (T):** Sets the system's temperature.
- **External Field (h):** Applies an external magnetic field.
- **Coupling Constant (J):** Determines the interaction strength between spins.
- **Equilibration Steps (n_eq):** Specifies the number of steps for the system to reach equilibrium.
- **Measurement Steps (n_steps):** Determines the number of steps for data collection.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or raise issues.

## License

MIT License

Copyright (c) [Year] [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

