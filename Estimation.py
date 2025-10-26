import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Optional

THEORETICAL_PC_2D_SQUARE = 0.59274621

def sigmoid(p: np.ndarray, pc: float, width: float) -> np.ndarray:
    '''
    Sigmoid function for percolation transition.
    At the critical point p_c, the percolation probability is 0.5.
    The width parameter controls how sharp the transition is.

    Args:
        p: Occupation probability values
        pc: Critical probability (inflection point)
        width: Transition width (smaller = sharper transition)
        
    Returns:
        Percolation probabilities from sigmoid curve
    '''
    return 1 / (1 + np.exp(-(p - pc) / width))


def estimate_pc(
    p_values: np.ndarray, 
    percolation_probs: np.ndarray,
    initial_guess: Tuple[float, float]=(0.59, 0.05),
    bounds: Tuple[Tuple[float, float], Tuple[float, float]] = ((0.4, 0.001), (0.8, 0.2))
) -> Tuple[Optional[float], Optional[float], Optional[dict]]:
    '''
    Estimate critical probability p_c by fitting sigmoid to data.

    Uses scipy.optimize.curve_fit to find the best-fit sigmoid parameters.
    Returns the critical point (inflection point of sigmoid) and uncertainty.  # ← This should be indented

    Args:
        p_values: Array of occupation probabilities tested
        percolation_probs: Array of measured percolation probabilities
        initial_guess: Initial guess for (pc, width)
        bounds: Bounds for (pc, width) as ((pc_min, width_min), (pc_max, width_max))
        
    Returns:
        Tuple of (pc, stderr, fit_info) where:
            - pc: Estimated critical probability (None if fit fails)
            - stderr: Standard error of pc estimate (None if fit fails)
            - fit_info: Dict with fit details (None if fit fails)
    '''
    try:
        # Perform curve fit
        popt, pcov = curve_fit(
            sigmoid,
            p_values,
            percolation_probs,
            p0=initial_guess,
            bounds=bounds,
            maxfev=10000  # Maximum function evaluations
        )
        
        pc_fit = popt[0]
        width_fit = popt[1]
        
        # Calculate standard errors from covariance matrix
        perr = np.sqrt(np.diag(pcov))
        pc_stderr = perr[0]
        width_stderr = perr[1]
        
        # Calculate R² (goodness of fit)
        residuals = percolation_probs - sigmoid(p_values, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((percolation_probs - np.mean(percolation_probs))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        fit_info = {
            'pc': pc_fit,
            'pc_stderr': pc_stderr,
            'width': width_fit,
            'width_stderr': width_stderr,
            'r_squared': r_squared,
            'residuals': residuals,
            'fitted_curve': sigmoid(p_values, *popt)
        }
        
        return pc_fit, pc_stderr, fit_info
        
    except RuntimeError as e:
        print(f"Warning: Curve fitting failed: {e}")
        return None, None, None
    except Exception as e:
        print(f"Warning: Unexpected error in curve fitting: {e}")
        return None, None, None


def print_pc_analysis(
            pc: Optional[float],
            stderr:Optional[float],
            fit_info: Optional[dict],
            theoretical_pc: float=THEORETICAL_PC_2D_SQUARE
            ):
    '''
    Print formatted analysis of p_c estimation.
    Args:
    pc: Estimated critical probability
    stderr: Standard error of estimate
    fit_info: Additional fit information
    theoretical_pc: Known theoretical value for comparison
    '''
    print("\n" + "="*60)
    print("PERCOLATION CRITICAL POINT ANALYSIS")
    print("="*60)

    if pc is not None:
        print(f"\nEstimated p_c:    {pc:.4f} ± {stderr:.4f}")
        print(f"Theoretical p_c:  {theoretical_pc:.4f}")
        
        error = abs(pc - theoretical_pc)
        error_pct = (error / theoretical_pc) * 100
        print(f"Absolute error:   {error:.4f}")
        print(f"Relative error:   {error_pct:.2f}%")
        
        if fit_info is not None:
            print(f"\nTransition width: {fit_info['width']:.4f} ± {fit_info['width_stderr']:.4f}")
            print(f"R² (goodness):    {fit_info['r_squared']:.4f}")
            
            if fit_info['r_squared'] < 0.95:
                print("\n⚠ Warning: R² < 0.95 suggests poor fit.")
                print("  Consider: more trials, finer p resolution, or larger N")
    else:
        print("\n✗ Could not estimate p_c")
        print("  Possible issues:")
        print("  - Insufficient data points")
        print("  - Data doesn't span the transition (P(p) = 0 to 1)")
        print("  - Too much noise (increase num_trials)")
        print("  - Grid too small (increase N)")

    print("="*60 + "\n")


def suggest_improvements(
            p_values: np.ndarray,
            percolation_probs: np.ndarray,
            N: int,
            num_trials: int
            ):
    '''
    Suggest improvements for better p_c estimation.
    Args:
    p_values: Array of occupation probabilities tested
    percolation_probs: Array of measured percolation probabilities
    N: Grid size
    num_trials: Number of trials per p value
    '''
    suggestions = []

    # Check if we span the transition
    if max(percolation_probs) < 0.9:
        suggestions.append("Increase max(p) to see full transition (P(p) → 1)")
    if min(percolation_probs) > 0.1:
        suggestions.append("Decrease min(p) to see full transition (P(p) → 0)")

    # Check resolution near p_c
    p_near_pc = p_values[(p_values > 0.55) & (p_values < 0.65)]
    if len(p_near_pc) < 10:
        suggestions.append("Add more p values near p_c ≈ 0.593 for better accuracy")

    # Check grid size
    if N < 100:
        suggestions.append(f"Increase grid size (N={N} → N≥100) for sharper transition")

    # Check number of trials
    if num_trials < 100:
        suggestions.append(f"Increase trials (n={num_trials} → n≥100) to reduce noise")

    if suggestions:
        print("Suggestions for improvement:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()


def analyze_simulation_results(
            p_values: np.ndarray,
            percolation_probs: np.ndarray,
            N: int,
            num_trials: int,
            verbose: bool = True
            ) -> dict:
    '''
    Complete analysis of simulation results including p_c estimation.
    Args:
        p_values: Array of occupation probabilities tested
        percolation_probs: Array of measured percolation probabilities
        N: Grid size used in simulation
        num_trials: Number of trials per p value
        verbose: Whether to print detailed analysis
        
    Returns:
        Dictionary with analysis results
    '''
    # Estimate p_c
    pc, stderr, fit_info = estimate_pc(p_values, percolation_probs)

    # Print analysis if verbose
    if verbose:
        print_pc_analysis(pc, stderr, fit_info)
        suggest_improvements(p_values, percolation_probs, N, num_trials)

    # Return results
    results = {
        'pc_estimate': pc,
        'pc_stderr': stderr,
        'theoretical_pc': THEORETICAL_PC_2D_SQUARE,
        'fit_info': fit_info,
        'error': abs(pc - THEORETICAL_PC_2D_SQUARE) if pc is not None else None,
        'error_percent': abs(pc - THEORETICAL_PC_2D_SQUARE) / THEORETICAL_PC_2D_SQUARE * 100 if pc is not None else None
    }

    return results
        