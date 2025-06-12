import pytest
import pandas as pd
import numpy as np

# Dynamic path resolution for portable imports
import sys
import os

def setup_imports():
    """Setup imports for the test file to work from any location"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    metrics_path = os.path.join(scripts_dir, 'metrics')
    if not os.path.exists(metrics_path):
        possible_paths = [
            os.path.join(current_dir, '..', 'metrics'),
            os.path.join(current_dir, '..', '..', 'scripts', 'metrics'),
            scripts_dir
        ]
        
        for path in possible_paths:
            normalized_path = os.path.normpath(os.path.abspath(path))
            parent_dir = os.path.dirname(normalized_path)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)

setup_imports()

try:
    from metrics.iat_regularity_metrics import computeModeDeviation, iatRegularityMetric
except ImportError as e:
    print(f"Error importing from metrics: {e}")
    print("Current working directory:", os.getcwd())
    print("Test file location:", os.path.abspath(__file__))
    raise

class TestComputeModeDeviation:
    
    def test_identical_values(self):
        """Test mode deviation with identical values"""
        data = pd.Series([5, 5, 5, 5, 5])
        result = computeModeDeviation(data)
        assert result == 0.0
    
    def test_simple_deviation(self):
        """Test mode deviation with simple known values"""
        data = pd.Series([1, 2, 3, 2, 2])  # mode is 2
        result = computeModeDeviation(data)
        expected = (abs(1-2) + abs(2-2) + abs(3-2) + abs(2-2) + abs(2-2)) / 5
        assert result == expected
    
    def test_single_value(self):
        """Test mode deviation with single value"""
        data = pd.Series([10])
        result = computeModeDeviation(data)
        assert result == 0.0
    
    def test_float_values(self):
        """Test mode deviation with float values"""
        data = pd.Series([1.5, 2.5, 1.5, 3.5, 1.5])  # mode is 1.5
        result = computeModeDeviation(data)
        expected = (0 + 1.0 + 0 + 2.0 + 0) / 5
        assert result == expected


class TestIATRegularityMetric:
    
    def test_perfect_regularity(self):
        """Test with perfectly regular IAT values (all same)"""
        data = {'IAT': [2.0, 2.0, 2.0, 2.0, 2.0]}
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert result == 1.0
    
    def test_high_regularity(self):
        """Test with high regularity (small deviations from mode)"""
        data = {'IAT': [2.0, 2.1, 2.0, 1.9, 2.0]}  # mode is 2.0
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert 0 < result <= 1
        assert result > 0.5  # Should be relatively high
    
    def test_low_regularity(self):
        """Test with low regularity (large deviations from mode)"""
        data = {'IAT': [1.0, 5.0, 1.0, 10.0, 1.0]}  # mode is 1.0
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert 0 <= result <= 1
    
    def test_single_value(self):
        """Test with single IAT value"""
        data = {'IAT': [5.0]}
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert result == 1.0  # Perfect regularity with single value
    
    def test_two_identical_values(self):
        """Test with two identical values"""
        data = {'IAT': [3.0, 3.0]}
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert result == 1.0
    
    def test_mixed_regularity(self):
        """Test with mixed regularity"""
        data = {'IAT': [2.0, 3.0, 2.0, 4.0, 2.0]}  # mode is 2.0
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert 0 <= result <= 1
    
    def test_return_type_and_precision(self):
        """Test that return value is properly rounded to 3 decimal places"""
        data = {'IAT': [1.0, 1.1, 1.0, 1.2, 1.0]}
        df = pd.DataFrame(data)
        
        result = iatRegularityMetric(df)
        assert isinstance(result, float)
        # Check that result has at most 3 decimal places
        assert len(str(result).split('.')[-1]) <= 3
    
    def test_with_additional_columns(self):
        """Test that function works with dataframes containing additional columns"""
        df = pd.DataFrame({
            'IAT': [2.0, 2.1, 2.0, 3.0, 2.0],
            'other_col': range(5)
        })
        result = iatRegularityMetric(df)
        assert 0 <= result <= 1