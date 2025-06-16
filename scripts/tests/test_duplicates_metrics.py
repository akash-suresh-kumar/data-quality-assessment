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
    from metrics.duplicates_metrics import duplicatesMetric
except ImportError as e:
    print(f"Error importing PreProcessing: {e}")
    print("Current working directory:", os.getcwd())
    print("Test file location:", os.path.abspath(__file__))
    print("Python path entries:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

class TestDuplicatesMetric:
    """Test suite for the duplicatesMetric function."""
    
    def test_no_duplicates(self):
        """Test metric calculation when there are no duplicates."""
        data = {
            'uniqueID': ['A', 'B', 'C', 'D'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:01:00', 
                '2023-01-01 10:02:00',
                '2023-01-01 10:03:00'
            ],
            'other_col': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # No duplicates should return score of 1.0
        assert result == 1.0
    
    def test_all_duplicates(self):
        """Test metric calculation when all rows are duplicates."""
        data = {
            'uniqueID': ['A', 'A', 'A', 'A'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00'
            ],
            'other_col': [1, 2, 3, 4]  # Different values in other columns
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # 3 duplicates out of 4 total = 1 - 3/4 = 0.25
        assert result == 0.25
    
    def test_partial_duplicates(self):
        """Test metric calculation with some duplicates."""
        data = {
            'uniqueID': ['A', 'A', 'B', 'C'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',  # Duplicate of first row
                '2023-01-01 10:01:00',
                '2023-01-01 10:02:00'
            ],
            'other_col': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # 1 duplicate out of 4 total = 1 - 1/4 = 0.75
        assert result == 0.75
    
    def test_single_row_dataframe(self):
        """Test metric calculation with single row DataFrame."""
        data = {
            'uniqueID': ['A'],
            'observationDateTime': ['2023-01-01 10:00:00'],
            'other_col': [1]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # Single row has no duplicates
        assert result == 1.0
    
    def test_empty_dataframe(self):
        """Test metric calculation with empty DataFrame."""
        df = pd.DataFrame(columns=['uniqueID', 'observationDateTime', 'other_col'])
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # Empty DataFrame should return 1.0 (perfect score, no duplicates possible)
        assert result == 1.0
    
    def test_two_rows_no_duplicates(self):
        """Test metric calculation with two unique rows."""
        data = {
            'uniqueID': ['A', 'B'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:01:00'
            ],
            'other_col': [1, 2]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        assert result == 1.0
    
    def test_two_rows_all_duplicates(self):
        """Test metric calculation with two identical rows."""
        data = {
            'uniqueID': ['A', 'A'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00'
            ],
            'other_col': [1, 2]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # 1 duplicate out of 2 total = 1 - 1/2 = 0.5
        assert result == 0.5
    
    def test_nan_values_in_columns(self):
        """Test metric calculation with NaN values in specified columns."""
        data = {
            'uniqueID': ['A', 'A', 'B', None],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',
                '2023-01-01 10:01:00',
                '2023-01-01 10:02:00'
            ],
            'other_col': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # Should handle NaN values in duplicate detection
        assert isinstance(result, (int, float))
        assert 0 <= result <= 1
    
    def test_different_column_names(self):
        """Test metric calculation with different column names."""
        data = {
            'deviceID': ['Device1', 'Device1', 'Device2'],
            'timestamp': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',  # Duplicate
                '2023-01-01 10:01:00'
            ],
            'value': [100, 200, 300]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'deviceID', 'timestamp')
        
        # 1 duplicate out of 3 total = 1 - 1/3 = 0.667
        expected = round(1 - 1/3, 3)
        assert result == expected
    
    def test_numeric_columns(self):
        """Test metric calculation with numeric columns."""
        data = {
            'id': [1, 1, 2, 3],
            'value': [10, 10, 20, 30],  # First two are duplicates
            'other': [100, 200, 300, 400]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'id', 'value')
        
        # 1 duplicate out of 4 total = 1 - 1/4 = 0.75
        assert result == 0.75
    
    def test_mixed_data_types(self):
        """Test metric calculation with mixed data types."""
        data = {
            'mixed_col': ['A', 1, 'A', 2],
            'other_col': [10, 20, 10, 40],
            'extra': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'mixed_col', 'other_col')
        
        # Should handle mixed data types
        assert isinstance(result, (int, float))
        assert 0 <= result <= 1
    
    def test_large_dataset_performance(self):
        """Test metric calculation with larger dataset."""
        # Create a larger dataset with known duplicate pattern
        size = 1000
        data = {
            'uniqueID': ['A'] * 500 + ['B'] * 500,  # Two groups
            'observationDateTime': (
                ['2023-01-01 10:00:00'] * 250 + ['2023-01-01 10:01:00'] * 250 +  # Group A: 2 unique combinations
                ['2023-01-01 11:00:00'] * 500  # Group B: 1 unique combination (all same)
            ),
            'other_col': list(range(size))
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # Unique combinations:
        # - ('A', '2023-01-01 10:00:00'): 250 rows
        # - ('A', '2023-01-01 10:01:00'): 250 rows  
        # - ('B', '2023-01-01 11:00:00'): 500 rows
        # Total unique combinations: 3
        # Total rows: 1000
        # Duplicates: 1000 - 3 = 997
        # Expected metric: 1 - 997/1000 = 0.003
        expected = round(1 - 997/1000, 3)
        assert result == expected
    
    def test_rounding_precision(self):
        """Test that the result is properly rounded to 3 decimal places."""
        data = {
            'uniqueID': ['A'] * 7,  # 7 rows
            'observationDateTime': ['2023-01-01 10:00:00'] * 7,  # All same
            'other_col': [1, 2, 3, 4, 5, 6, 7]
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # 6 duplicates out of 7 total = 1 - 6/7 = 0.142857...
        # Should be rounded to 3 decimal places
        expected = round(1 - 6/7, 3)
        assert result == expected
        
        # Check that it's actually rounded to 3 decimal places
        assert len(str(result).split('.')[-1]) <= 3
    
    def test_missing_columns_error(self):
        """Test error handling when specified columns don't exist."""
        data = {
            'wrongColumn1': ['A', 'B'],
            'wrongColumn2': ['X', 'Y']
        }
        df = pd.DataFrame(data)
        
        with pytest.raises(KeyError):
            duplicatesMetric(df, 'uniqueID', 'observationDateTime')
    
    def test_duplicate_detection_ignores_other_columns(self):
        """Test that duplicate detection only considers specified columns."""
        data = {
            'uniqueID': ['A', 'A', 'B'],
            'observationDateTime': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:00:00',  # Duplicate based on these two columns
                '2023-01-01 10:01:00'
            ],
            'different_values': [1, 999, 3],  # Different values in other column
            'more_different': ['X', 'Z', 'Y']
        }
        df = pd.DataFrame(data)
        
        result = duplicatesMetric(df, 'uniqueID', 'observationDateTime')
        
        # Should still detect duplicate despite different values in other columns
        # 1 duplicate out of 3 total = 1 - 1/3 = 0.667
        expected = round(1 - 1/3, 3)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])