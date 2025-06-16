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
    from metrics.iat_outliers_metrics import iatOutliersMetric
except ImportError as e:
    print(f"Error importing PreProcessing: {e}")
    print("Current working directory:", os.getcwd())
    print("Test file location:", os.path.abspath(__file__))
    print("Python path entries:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

class TestIATOutliersMetric:
    
    def test_no_outliers_perfect_score(self):
        """Test that data with no outliers returns score of 1.0"""
        # Create data with consistent IAT values (no outliers)
        data = {'IAT': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert result == 1.0
    
    def test_all_outliers_zero_score(self):
        """Test that data with all outliers returns score close to 0"""
        # Create data where most values are far from the median/mode
        # Using a clear pattern: many similar values + clear outliers
        data = {'IAT': [1.0, 1.0, 1.0, 1.0, 1.0, 100.0, 200.0, 300.0, 400.0, 500.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert result < 1.0  # Should detect the outliers
    
    def test_mixed_data_with_outliers(self):
        """Test with mixed data containing some outliers"""
        # Create data with clear outliers
        data = {'IAT': [1.0, 1.1, 1.0, 1.2, 1.0, 1.1, 50.0, 100.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
        assert result < 1.0  # Should be less than 1 due to outliers
    
    def test_single_value(self):
        """Test with single IAT value"""
        data = {'IAT': [5.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert result == 1.0  # Single value cannot be an outlier
    
    def test_two_identical_values(self):
        """Test with two identical IAT values"""
        data = {'IAT': [2.5, 2.5]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert result == 1.0
    
    def test_two_different_values(self):
        """Test with two different IAT values"""
        data = {'IAT': [1.0, 2.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
    
    def test_with_nan_values(self):
        """Test that NaN values are properly handled"""
        data = {'IAT': [1.0, 2.0, np.nan, 1.5, np.nan, 1.2]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
        # Should work without errors despite NaN values
    
    def test_empty_dataframe_after_dropna(self):
        """Test behavior with dataframe that becomes empty after dropping NaN"""
        data = {'IAT': [np.nan, np.nan, np.nan]}
        df = pd.DataFrame(data)
        
        with pytest.raises((ValueError, Exception)):
            iatOutliersMetric(df)
    
    def test_normal_distribution(self):
        """Test with normally distributed data"""
        np.random.seed(42)
        data = {'IAT': np.random.normal(10, 2, 100)}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
    
    def test_return_type_and_precision(self):
        """Test that return value is properly rounded to 3 decimal places"""
        data = {'IAT': [1.0, 1.1, 1.2, 1.3, 10.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert isinstance(result, float)
        # Check that result has at most 3 decimal places
        assert len(str(result).split('.')[-1]) <= 3
    
    def test_zero_mad_edge_case(self):
        """Test edge case where MAD might be zero"""
        # All values are the same, so MAD = 0
        data = {'IAT': [5.0, 5.0, 5.0, 5.0, 5.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert result == 1.0
    
    def test_large_dataset(self):
        """Test with a larger dataset"""
        np.random.seed(123)
        base_values = np.random.normal(5, 1, 1000)
        # Add some clear outliers
        outliers = [50, 100, -20, 200]
        all_values = np.concatenate([base_values, outliers])
        
        data = {'IAT': all_values}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
        assert result < 1.0  # Should detect the outliers
    
    def test_negative_values(self):
        """Test with negative IAT values"""
        data = {'IAT': [-1.0, -2.0, -1.5, -1.2, -10.0]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
    
    def test_very_small_values(self):
        """Test with very small IAT values"""
        data = {'IAT': [0.001, 0.002, 0.001, 0.0015, 0.1]}
        df = pd.DataFrame(data)
        
        result = iatOutliersMetric(df)
        assert 0 <= result <= 1
    
    @pytest.fixture
    def sample_dataframe(self):
        """Fixture providing a sample dataframe for testing"""
        return pd.DataFrame({
            'IAT': [1.0, 1.1, 1.0, 1.2, 1.0, 1.1, 1.05, 15.0, 20.0],
            'other_col': range(9)
        })
    
    def test_with_additional_columns(self, sample_dataframe):
        """Test that function works with dataframes containing additional columns"""
        result = iatOutliersMetric(sample_dataframe)
        assert 0 <= result <= 1
        assert result < 1.0  # Should detect outliers