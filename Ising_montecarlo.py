import numpy as np  #
import matplotlib.pyplot as plt  
from numba import njit  # Import Numba for JIT compilation (speeds up code)
from scipy.integrate import trapezoid  


@njit  # Using Numba to compile this function for faster execution
def init_lattice_nb(L):
    """
    Initializes a square lattice of size LxL with random spins (-1 or +1).

    Args:
        L (int): The size of the lattice.

    Returns:
        numpy.ndarray: The initialized lattice.
    """
    lattice = np.empty((L, L), dtype=np.int8)  # Creating an empty lattice
    for i in range(L):  # Loop over rows
        for j in range(L):  # Loop over columns
            # Assign random spins (-1 or +1) to each lattice site
            lattice[i, j] = -1 if np.random.randint(0, 2) == 0 else 1 #randint generates 0 and 1. If 0 assign -1 spin else +1 spin.
    return lattice  # Returns the initialized lattice


@njit  
def delta_energy_nb(lattice, i, j, J, h):
    """
    Calculates the change in energy if the spin at (i, j) is flipped.

    Args:
        lattice (numpy.ndarray): The Ising lattice.
        i (int): Row index of the spin.
        j (int): Column index of the spin.
        J (float): Coupling constant (interaction strength).
        h (float): External magnetic field.

    Returns:
        float: The change in energy.
    """
    L = lattice.shape[0]  # Get the size of the lattice
    s = lattice[i, j]  # Get the spin at (i, j)
    # Calculate the sum of neighboring spins (periodic boundary conditions assured by mod L) 
    nb = (
        lattice[(i + 1) % L, j] +
        lattice[(i - 1) % L, j] +
        lattice[i, (j + 1) % L] +
        lattice[i, (j - 1) % L]
    )  
    # Calculates and return the change in energy
    return 2 * s * (J * nb + h)  


@njit  
def metropolis_step_nb(lattice, beta, J, h):
    """
    Performs a single Metropolis Monte Carlo step.

    Args:
        lattice (numpy.ndarray): The Ising lattice.
        beta (float): Inverse temperature (1/T).
        J (float): Coupling constant.
        h (float): External magnetic field.
    """
    L = lattice.shape[0]  # Lattice size
    for _ in range(L * L):  # Loop over all lattice sites
        i = np.random.randint(0, L)  # Choose a random row
        j = np.random.randint(0, L)  # Choose a random column
        dE = delta_energy_nb(lattice, i, j, J, h)  # Calculate energy change
        # Metropolis acceptance criterion:
        if dE <= 0 or np.random.random() < np.exp(-beta * dE):  
            lattice[i, j] = -lattice[i, j]  # Flip the spin


@njit  
def measure_magnetization_nb(L, T, h, n_eq, n_steps, J):
    """
    Measures the average magnetization of the lattice.

    Args:
        L (int): Lattice size.
        T (float): Temperature.
        h (float): External magnetic field.
        n_eq (int): Number of equilibration steps.
        n_steps (int): Number of measurement steps.
        J (float): Coupling constant.

    Returns:
        float: The average magnetization.
    """
    lattice = init_lattice_nb(L)  # Initialize the lattice
    beta = 1.0 / T  # Calculate inverse temperature
    for _ in range(n_eq):  # Equilibration steps
        metropolis_step_nb(lattice, beta, J, h)  
    m_accum = 0.0  # Accumulator for magnetization
    for _ in range(n_steps):  # Measurement steps
        metropolis_step_nb(lattice, beta, J, h)  
        m_accum += lattice.sum()  # Add total spin to accumulator
    # Calculates and return the average magnetization
    return m_accum / (n_steps * L * L)  


@njit 
def compute_m_vs_h_nb(L, T, h_values, n_eq, n_steps, J):
    """
    Computes magnetization as a function of external field according to problem (c).

    Args:
        L (int): Lattice size.
        T (float): Temperature.
        h_values (numpy.ndarray): Array of external field values.
        n_eq (int): Number of equilibration steps.
        n_steps (int): Number of measurement steps.
        J (float): Coupling constant.

    Returns:
        numpy.ndarray: Magnetization values corresponding to h_values.
    """
    m_vs_h = np.empty(h_values.shape[0], dtype=np.float64)  # Array to store results
    for idx in range(h_values.shape[0]):  # Loop over  different field values
        # Calculates and store magnetization for each field
        m_vs_h[idx] = measure_magnetization_nb(L, T, h_values[idx], n_eq, n_steps, J) 
    return m_vs_h  # Return the magnetization array


@njit  
def measure_abs_magnetization_nb(L, T, n_eq, n_steps, J=1.0):
    """
    Measures the average absolute magnetization.

    Args:
        L (int): Lattice size.
        T (float): Temperature.
        n_eq (int): Number of equilibration steps.
        n_steps (int): Number of measurement steps.
        J (float, optional): Coupling constant. Defaults to 1.0.

    Returns:
        float: The average absolute magnetization.
    """
    lattice = init_lattice_nb(L)  # Initialize the lattice
    beta = 1.0 / T  # Calculate inverse temperature
    N = L * L  # Total number of spins
    for _ in range(n_eq):  # Equilibration
        metropolis_step_nb(lattice, beta, J, 0.0)  
    abs_m_sum = 0.0  # Accumulator for absolute magnetization
    for _ in range(n_steps):  # Measurement
        metropolis_step_nb(lattice, beta, J, 0.0)  
        abs_m_sum += abs(lattice.sum()) / N  # Accumulate absolute magnetization
    # Calculates and return the average absolute magnetization
    return abs_m_sum / n_steps  


@njit  
def measure_spin_stats_explicit_nb(L, T, h, n_eq, n_steps, J=1.0):
    """
    Measures spin-spin correlations according to Chandler problem 6.10 .

    Args:
        L (int): Lattice size.
        T (float): Temperature.
        h (float): External magnetic field.
        n_eq (int): Number of equilibration steps.
        n_steps (int): Number of measurement steps.
        J (float, optional): Coupling constant. 

    Returns:
        tuple: (Average magnetization, correlation function).
    """
    lattice = init_lattice_nb(L)  # Initialize the lattice
    beta = 1.0 / T  # Calculate inverse temperature
    N = L * L  # Total number of spins
    max_r = L // 2  # Maximum separation for correlation calculation

    for _ in range(n_eq):  # Equilibration
        metropolis_step_nb(lattice, beta, J, h)  

    sum_m = 0.0  # Accumulator for magnetization
    # Accumulators for spin-spin pairs and shifted spins
    sum_pair = np.zeros(max_r + 1, dtype=np.float64)  
    sum_shift = np.zeros(max_r + 1, dtype=np.float64)  

    for _ in range(n_steps):  # Measurement
        metropolis_step_nb(lattice, beta, J, h)  
        total_spin = 0  # Accumulator for total spin in the current step
        for i in range(L):  # Loop over rows
            for j in range(L):  # Loop over columns
                total_spin += lattice[i, j]  # Add spin to total
        m_inst = total_spin / N  # Instantaneous magnetization
        sum_m += m_inst  # Accumulate magnetization

        for r in range(max_r + 1):  # Loop over separations
            pair_sum = 0.0  # Accumulator for spin pairs
            shift_sum = 0.0  # Accumulator for shifted spins
            for i in range(L):  # Loop over rows
                for j in range(L):  # Loop over columns
                    si = lattice[i, j]  # Spin at (i, j)
                    sj = lattice[(i + r) % L, j]  # Spin at (i+r, j) 
                    pair_sum += si * sj  # Accumulate spin pair product
                    shift_sum += sj  # Accumulate shifted spin
            sum_pair[r] += pair_sum / N  # Accumulate pair sum
            sum_shift[r] += shift_sum / N  # Accumulate shifted sum

    m_avg = sum_m / n_steps  # Average magnetization
    corr = np.empty(max_r + 1, dtype=np.float64)  # Array to store correlations
    for r in range(max_r + 1):  # Loop over separations
        avg_ss = sum_pair[r] / n_steps  # Average of spin pair products
        avg_sj = sum_shift[r] / n_steps  # Average of shifted spins
        # Calculate connected correlation function
        corr[r] = avg_ss - (m_avg * avg_sj)  
    return m_avg, corr  # Return average magnetization and correlation


@njit  
def measure_column_correlation_nb(L, T, col_idx, n_eq, n_steps, J):
    """
    Measures spin-spin correlations in a specific column according to Chandler Problem 6.11(b) and (c).

    Args:
        L (int): Lattice size.
        T (float): Temperature.
        col_idx (int): Index of the column to analyze.
        n_eq (int): Number of equilibration steps.
        n_steps (int): Number of measurement steps.
        J (float): Coupling constant.

    Returns:
        tuple: (Average magnetization, correlation function).
    """
    lattice = init_lattice_nb(L)  # Initialize the lattice
    beta = 1.0 / T  # Calculate inverse temperature
    N = L * L  # Total number of spins
    max_r = L // 2  # Maximum separation for correlation

    for _ in range(n_eq):  # Equilibration
        metropolis_step_nb(lattice, beta, J, 0.0) 

    sum_m = 0.0  # Accumulator for magnetization
    corr_sum = np.zeros(max_r + 1, dtype=np.float64)  # Accumulator for correlations

    for _ in range(n_steps):  # Measurement
        metropolis_step_nb(lattice, beta, J, 0.0)  
        m_inst = lattice.sum() / N  # Instantaneous magnetization
        sum_m += m_inst  # Accumulate magnetization

        for r in range(max_r + 1):  # Loop over separations
            c = 0.0  # Accumulator for spin pairs in the column
            for i in range(L):  # Loop over rows in the column
                # Calculate spin pair product in the column 10 and 4
                c += lattice[i, col_idx] * lattice[(i + r) % L, col_idx]  
            corr_sum[r] += c / L  # Accumulate correlation sum

    m_avg = sum_m / n_steps  # Average magnetization
    # Calculate correlation function for the column 10 and 4
    corr = corr_sum / n_steps - m_avg**2  
    return m_avg, corr  # Return average magnetization and correlation


# ——————————————————————————————————————————————————————
# 2) Main Execution and Plotting
# ——————————————————————————————————————————————————————

if __name__ == "__main__":
    # (a) Magnetization vs. External Field (⟨m⟩ vs h) according to problem (c)
    L_list = [20, 50]  # Lattice sizes to simulate
    T_list_h = [1.5, 2.269, 3.0]  # Temperatures to simulate
    h_values = np.linspace(-1.0, 1.0, 21)  # Range of external field values
    n_eq_h = 100  # Number of equilibration steps
    n_steps_h = 500  # Number of measurement steps
    J = 1.0  # Coupling constant

    plt.figure(figsize=(8, 4))  # Create a figure for the plot
    for L in L_list:  # Loop over lattice sizes
        for T in T_list_h:  # Loop over temperatures
            # Calculate magnetization vs. field
            m_vs_h = compute_m_vs_h_nb(L, T, h_values, n_eq_h, n_steps_h, J)  
            # Plot the results
            plt.plot(h_values, m_vs_h, 'o-', label=f"L={L}, T={T}")  
    plt.xlabel("External field $h$")  # X-axis label
    plt.ylabel("⟨m⟩")  # Y-axis label
    plt.title("Magnetization vs Field")  # Plot title
    plt.legend()  # Show legend
    plt.grid(True)  # Add gridlines
    plt.tight_layout()  # Adjust layout for better spacing


    # (b) Spontaneous Magnetization vs. Reduced Temperature (⟨|m|⟩ vs T/Tc) according to Chandler Problem 6.10
    L = 20  # Lattice size
    T_c = 2.269  # Critical temperature looked up from Google
    T_list = np.linspace(1.0, 4.0, 20)  # Range of temperatures
    red_T = T_list / T_c  # Reduced temperature
    n_eq = 100  # Number of equilibration steps
    n_steps = 30000  # Number of measurement steps
    R = 5  # Number of independent runs for averaging

    _ = measure_abs_magnetization_nb(L, T_list[0], 10, 10, J)  # Warm-up for better performance from numba package 

    abs_m_accum = np.zeros_like(red_T)  # Accumulator for absolute magnetization
    for seed in range(R):  # Loop over independent runs
        np.random.seed(seed)  # Set random seed for reproducibility
        for i, T in enumerate(T_list):  # Loop over temperatures
            # Accumulate absolute magnetization from each run
            abs_m_accum[i] += measure_abs_magnetization_nb(L, T, n_eq, n_steps, J)  
    abs_m_avg = abs_m_accum / R  # Average absolute magnetization

    plt.figure(figsize=(6, 4))  # Create a figure for the plot
    plt.plot(T_list, abs_m_avg, 'o-', label=f"L={L}")  # Plot the results
    plt.axvline(1.0, color='k', ls='--')  # Add vertical line at T/Tc = 1
    plt.xlabel(r"$T$")  # X-axis label
    plt.ylabel(r"⟨|m|⟩")  # Y-axis label
    plt.title(" Magnetization versus Temperature")  # Plot title
    plt.legend()  # Show legend
    plt.grid(True)  # Add gridlines
    plt.tight_layout()  # Adjust layout


    # (c) Correlation vs. Reduced Temperature (C(r) vs T/Tc) according to Chandler Problem 6.10
    r_values = [1, 2, 3, 5, 10]  # Separations to analyze
    corr_accum = {r: np.zeros_like(red_T) for r in r_values}  # Correlation accumulators

    _ = measure_spin_stats_explicit_nb(L, T_list[0], 0.0, 10, 10, J)  # Warm-up

    for seed in range(R):  # Loop over independent runs
        np.random.seed(seed)  # Set random seed
        for i, T in enumerate(T_list):  # Loop over temperatures
            # Calculate correlations
            _, conn_corr = measure_spin_stats_explicit_nb(L, T, 0.0, n_eq, n_steps, J)  
            for r in r_values:  # Loop over separations
                corr_accum[r][i] += conn_corr[r]  # Accumulate correlations
    corr_avg = {r: corr_accum[r] / R for r in r_values}  # Average correlations

    plt.figure(figsize=(6, 4))  # Create a figure for the plot
    for r in r_values:  # Loop over separations
        plt.plot(red_T, corr_avg[r], '-o', label=f"r={r}")  # Plot correlations
    plt.axvline(1.0, color='k', ls='--')  # Add vertical line at T/Tc = 1
    plt.xlabel(r"$T/T_c$")  # X-axis label
    plt.ylabel(r"$C(r)$")  # Y-axis label
    plt.title("Correlation vs Reduced Temperature")  # Plot title
    plt.legend()  # Show legend
    plt.grid(True)  # Add gridlines
    plt.tight_layout()  # Adjust layout


    # (d) Column-Specific Correlation (C(r) vs r) according to Chandler problem 6.11(b) and (c)
    T = 0.5 * T_c  # Temperature for this analysis
    n_eq_c = 1000  # Number of equilibration steps
    n_steps_c = 40000  # Number of measurement steps
    col5 = 4  # Index of the 5th column
    col10 = L // 2 - 1  # Index of the 10th column

    _ = measure_column_correlation_nb(L, T, col5, n_eq_c, 10, J)  # Warm-up for better performance
    _ = measure_column_correlation_nb(L, T, col10, n_eq_c, 10, J)  # Warm-up for better performance

    # Calculate correlations for the 5th and 10th columns
    m5, corr5 = measure_column_correlation_nb(L, T, col5, n_eq_c, n_steps_c, J)  
    m10, corr10 = measure_column_correlation_nb(L, T, col10, n_eq_c, n_steps_c, J)  

    r_vals = np.arange(1, 6)  # Separations to analyze
    corr5_s = corr5[1:6]  # Correlations for the 5th column
    corr10_s = corr10[1:6]  # Correlations for the 10th column

    plt.figure(figsize=(6, 4))  # Create a figure for the plot
    # Plot correlations for the 5th and 10th columns
    plt.plot(r_vals, corr5_s, 'o-', label=f"5th col (m={m5:.3f})")  
    plt.plot(r_vals, corr10_s, 's-', label=f"10th col (m={m10:.3f})")  
    plt.xlabel("Separation $r$")  # X-axis label
    plt.ylabel(r"$C(r)$")  # Y-axis label
    plt.title(f" Correlation vs r at T/T_c={T / T_c:.2f}")  # Plot title
    plt.legend()  # Show legend
    plt.grid(True)  # Add gridlines
    plt.tight_layout()  # Adjust layout

    plt.show()  # Display all plots


    # ——————————————————————————————————————————————————————
    # 3) Umbrella Sampling + WHAM 
    # ——————————————————————————————————————————————————————

    def delta_E_and_dM(lattice, i, j, J, k_bias, M0, M):
        """
        Calculates the change in energy and magnetization with bias.

        Args:
            lattice (numpy.ndarray): The Ising lattice.
            i (int): Row index of the spin.
            j (int): Column index of the spin.
            J (float): Coupling constant.
            k_bias (float): Bias strength.
            M0 (float): Target magnetization for the window.
            M (float): Current magnetization.

        Returns:
            tuple: (Change in energy, change in magnetization).
        """
        L = lattice.shape[0]  # Lattice size
        s = lattice[i, j]  # Spin at (i, j)
        # Calculate the sum of neighboring spins (periodic boundary conditions)
        nb = (lattice[(i + 1) % L, j] + lattice[(i - 1) % L, j] +
              lattice[i, (j + 1) % L] + lattice[i, (j - 1) % L])  
        dE_int = 2 * s * J * nb  # Energy change due to interactions
        dM = -2 * s  # Change in magnetization due to spin flip
        # Change in bias potential energy
        dV = 0.5 * k_bias * ((M + dM - M0)**2 - (M - M0)**2)  
        return dE_int + dV, dM  # Return total energy change and magnetization change


    def run_window_us(L, T, J, k_bias, M0, n_eq, n_steps, bins):
        """
        Runs a simulation for a single umbrella window.

        Args:
            L (int): Lattice size.
            T (float): Temperature.
            J (float): Coupling constant.
            k_bias (float): Bias strength.
            M0 (float): Target magnetization for the window.
            n_eq (int): Number of equilibration steps.
            n_steps (int): Number of measurement steps.
            bins (int): Number of bins for the magnetization histogram.

        Returns:
            tuple: (Magnetization histogram, magnetization grid).
        """
        beta = 1.0 / T  # Inverse temperature
        lattice = init_lattice_nb(L)  # Initialize lattice
        M = lattice.sum()  # Initial magnetization
        hist = np.zeros(bins)  # Magnetization histogram
        Mgrid = np.linspace(-L * L,L * L, bins)  # Magnetization grid

        for _ in range(n_eq):  # Equilibration
            i, j = np.random.randint(0, L, 2)  # Choose random spin
            # Calculate energy and magnetization change with bias
            dE, dM = delta_E_and_dM(lattice, i, j, J, k_bias, M0, M)  
            # Metropolis acceptance criterion
            if dE <= 0 or np.random.rand() < np.exp(-beta * dE):  
                lattice[i, j] *= -1  # Flip spin
                M += dM  # Update magnetization

        for _ in range(n_steps):  # Measurement
            i, j = np.random.randint(0, L, 2)  # Choose random spin
            # Calculate energy and magnetization change with bias
            dE, dM = delta_E_and_dM(lattice, i, j, J, k_bias, M0, M)  
            # Metropolis acceptance criterion
            if dE <= 0 or np.random.rand() < np.exp(-beta * dE):  
                lattice[i, j] *= -1  # Flip spin
                M += dM  # Update magnetization
            # Update magnetization histogram
            idx = int((M - Mgrid[0]) / (Mgrid[-1] - Mgrid[0]) * (bins - 1))  
            hist[idx] += 1  # Increment histogram bin

        return hist, Mgrid  # Return histogram and grid


    def wham_us(hist_list, Mgrid, k_bias, M0_list, beta):
        """
        Performs Weighted Histogram Analysis Method (WHAM).

        Args:
            hist_list (list): List of magnetization histograms from windows.
            Mgrid (numpy.ndarray): Magnetization grid.
            k_bias (float): Bias strength.
            M0_list (list): List of target magnetizations for windows.
            beta (float): Inverse temperature.

        Returns:
            tuple: (Unbiased probability distribution, free energy).
        """
        H = np.vstack(hist_list)  # Stack histograms vertically
        n_k = H.sum(axis=1)  # Number of samples in each window
        # Bias potential for each window
        V = np.array([0.5 * k_bias * (Mgrid - M0)**2 for M0 in M0_list])  
        f = np.zeros_like(n_k)  # Initial free energy estimates
        eps = 1e-30  # Small value to avoid division by zero

        # WHAM iterative procedure
        for _ in range(5000):  # Iterate until convergence
            # Calculate denominator for probability calculation
            denom = np.sum(n_k[:, None] * np.exp(beta * (f[:, None] - V)),
                           axis=0)  
            totalH = H.sum(axis=0)  # Total histogram
            P = np.zeros_like(totalH)  # Unbiased probability distribution
            mask = denom > eps  # Mask for valid denominator values
            P[mask] = totalH[mask] / denom[mask]  # Calculate probability
            P /= trapezoid(P, Mgrid)  # Normalize probability
            # Calculate integral for free energy update
            integ = trapezoid(P[None, :] * np.exp(-beta * V), Mgrid, axis=1)  
            f_new = -np.log(integ + eps) / beta  # Update free energy
            # Check for convergence
            if np.max(np.abs(f_new - f)) < 1e-6:  
                f = f_new  # Update free energy and break loop
                break
            f = f_new  # Update free energy

        F = -np.log(P + eps) / beta  # Calculate free energy
        return P, F  # Return probability and free energy


    def m_exact_full(T, J=1.0):
        """
        Calculates the exact spontaneous magnetization for the 2D Ising model.

        Args:
            T (float or numpy.ndarray): Temperature(s).
            J (float, optional): Coupling constant. Defaults to 1.0.

        Returns:
            float or numpy.ndarray: The exact spontaneous magnetization.
        """
        Tc = 2 * J / np.log(1 + np.sqrt(2))  # Critical temperature
        z = np.exp(-2 * J / T)  # Boltzmann factor
        m = np.zeros_like(T, dtype=float)  # Array to store magnetization
        mask = T < Tc  # Mask for temperatures below Tc
        zt = z[mask]  # Boltzmann factor for temperatures below Tc
        # Calculate  exact magnetization for temperatures below Tc
        m[mask] = (1 + zt**2)**0.25 * (1 - 6 * zt**2 + zt**4)**0.125 * (
            1 - zt**2)**(-0.5)  
        return m  # Return magnetization


    # Umbrella Sampling parameters
    plt.figure(figsize=(7, 5))  # Create a figure for the plot
    temps_us = np.linspace(2.00, 2.60, 13)  # Temperatures to simulate
    for L in [10, 20]:  # Loop over lattice sizes
        N = L * L  # Total number of spins
        k_bias = 2.0  # Bias strength
        windows = np.linspace(-N, N, 31)  # Target magnetizations for windows
        m_vals = []  # List to store minimum magnetization values

        for T in temps_us:  # Loop over temperatures
            hists = []  # List to store histograms from windows
            for M0 in windows:  # Loop over target magnetizations
                # Run simulation for a single window
                h, Mgrid = run_window_us(L, T, J, k_bias, M0, 500, 5000,
                                        351)  
                hists.append(h)  # Add histogram to list

            # Perform WHAM to get unbiased probability and free energy
            _, F = wham_us(hists, Mgrid, k_bias, windows, 1.0 / T)  
            M_star = Mgrid[np.nanargmin(F)]  # Magnetization minimizing free energy
            m_vals.append(abs(M_star) / N)  # Store minimum magnetization

        # Plot the results for the current lattice size
        plt.plot(temps_us, m_vals, '--o', label=f"L={L}")  

    # Plot the exact solution for infinite lattice size
    m_inf = m_exact_full(temps_us)  
    plt.plot(temps_us, m_inf, 'k-', lw=2, label="L=∞(exact)")  

    # Add labels, title, legend, etc. to the plot
    plt.xlabel(r"$T$", fontsize=14)  
    plt.ylabel(r"$M_{\min}/L^2$", fontsize=14)  
    plt.title("Umbrella-MC estimate of $M_{\min}/L^2$", fontsize=16)  
    plt.legend()  
    plt.ylim(0.6, 1.02)  
    plt.xlim(2.0, 2.6)  
    plt.grid(True)  
    plt.tight_layout()  
    plt.show()  
