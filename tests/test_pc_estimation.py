import pytest
import numpy as np
from pc_estimation import sigmoid, estimate_pc, analyze_simulation_results



class TestSigmoid:
    '''Test sigmoid function.'''
    def test_sigmoid_at_pc(self):
        '''Sigmoid should be 0.5 at p_c.'''
        pc = 0.6
        width = 0.05
        result = sigmoid(np.ndarray([pc]), pc, width)
        
        assert np.isclose(result[0], 0.5), "Sigmoid should be 0.5 at p_c"

    def test_sigmoid_bounds(self):
        '''Sigmoid should approach 0 and 1 at extremes.'''
        pc = 0.6
        width = 0.05
        
        # Far below p_c
        low = sigmoid(np.array([0.3]), pc, width)
        assert low[0] < 0.01, "Sigmoid should approach 0 below p_c"
        
        # Far above p_c
        high = sigmoid(np.array([0.9]), pc, width)
        assert high[0] > 0.99, "Sigmoid should approach 1 above p_c"



class TestPcEstimation:
    '''Test p_c estimation.'''
    def test_perfect_sigmoid_data(self):
        """Should recover p_c exactly from perfect sigmoid data."""
        true_pc = 0.593
        true_width = 0.03
        
        p_values = np.linspace(0.5, 0.7, 50)
        percolation_probs = sigmoid(p_values, true_pc, true_width)
        
        pc, stderr, fit_info = estimate_pc(p_values, percolation_probs)
        
        assert pc is not None, "Should successfully fit perfect data"
        assert abs(pc - true_pc) < 0.001, f"Should recover true p_c (got {pc:.4f}, expected {true_pc:.4f})"
        assert fit_info['r_squared'] > 0.999, "Perfect data should have R² ≈ 1"

    def test_noisy_data(self):
        """Should handle noisy data gracefully."""
        np.random.seed(42)
        
        true_pc = 0.593
        true_width = 0.03
        
        p_values = np.linspace(0.5, 0.7, 30)
        percolation_probs = sigmoid(p_values, true_pc, true_width)
        # Add noise
        percolation_probs += np.random.normal(0, 0.05, len(p_values))
        percolation_probs = np.clip(percolation_probs, 0, 1)
        
        pc, stderr, fit_info = estimate_pc(p_values, percolation_probs)
        
        assert pc is not None, "Should handle noisy data"
        assert abs(pc - true_pc) < 0.01, "Should be close to true p_c despite noise"
        assert stderr < 0.01, "Standard error should be reasonable"

    def test_insufficient_data(self):
        """Should fail gracefully with insufficient data."""
        p_values = np.array([0.5, 0.6])
        percolation_probs = np.array([0.2, 0.8])
        
        pc, stderr, fit_info = estimate_pc(p_values, percolation_probs)
        
        # May succeed with just 2 points, but won't be reliable
        # Main thing is it shouldn't crash
        assert True, "Should not crash on minimal data"

    def test_no_transition(self):
        """Should handle data with no clear transition."""
        p_values = np.linspace(0.7, 0.9, 20)
        percolation_probs = np.ones(20) * 0.95  # All high
        
        pc, stderr, fit_info = estimate_pc(p_values, percolation_probs)
        
        # May or may not succeed - main thing is no crash
        assert True, "Should not crash on flat data"


class TestAnalyzeResults:
    '''Test complete analysis function.'''
    def test_analyze_realistic_data(self):
        """Test with realistic simulation-like data."""
        np.random.seed(42)
        
        # Simulate realistic percolation data
        p_values = np.linspace(0.4, 0.7, 31)
        true_pc = 0.593
        
        # Realistic transition with noise
        percolation_probs = sigmoid(p_values, true_pc, 0.04)
        percolation_probs += np.random.normal(0, 0.03, len(p_values))
        percolation_probs = np.clip(percolation_probs, 0, 1)
        
        results = analyze_simulation_results(
            p_values=p_values,
            percolation_probs=percolation_probs,
            N=50,
            num_trials=100,
            verbose=False
        )
        
        assert results['pc_estimate'] is not None, "Should estimate p_c"
        assert results['error'] is not None, "Should calculate error"
        assert 0.55 < results['pc_estimate'] < 0.65, "p_c should be reasonable"
        assert results['error_percent'] < 5, "Error should be < 5% for good data"

    def test_returns_dict(self):
        """Test that analysis returns proper dict structure."""
        p_values = np.linspace(0.5, 0.7, 20)
        percolation_probs = sigmoid(p_values, 0.593, 0.03)
        
        results = analyze_simulation_results(
            p_values=p_values,
            percolation_probs=percolation_probs,
            N=50,
            num_trials=100,
            verbose=False
        )
        
        expected_keys = ['pc_estimate', 'pc_stderr', 'theoretical_pc', 
                        'fit_info', 'error', 'error_percent']
        
        for key in expected_keys:
            assert key in results, f"Results should contain '{key}'"