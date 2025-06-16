import pytest
import pandas as pd
import numpy as np
import json
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import matplotlib.pyplot as plt


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
    from metrics import PreProcessing as pp
except ImportError as e:
    print(f"Error importing PreProcessing: {e}")
    print("Current working directory:", os.getcwd())
    print("Test file location:", os.path.abspath(__file__))
    print("Python path entries:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
    
    # Try direct import as fallback
    try:
        import PreProcessing as pp
        print("Successfully imported PreProcessing directly")
    except ImportError:
        print("Direct import also failed")
        raise


class TestPreProcessing:
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration dictionary for testing"""
        return {
            'folderName': 'test_folder',
            'dataFileNameJSON': 'test_data.json',
            'datasetName': 'Test Dataset',
            'schemaFileName': 'test_schema.json',
            'URL': 'http://test.url',
            'interArrivalTime': {
                'alpha': [0.1, 0.2, 0.3],
                'inputFields': ['deviceId', 'observationDateTime']
            }
        }
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data for testing"""
        return [
            {
                'deviceId': 'device_001',
                'observationDateTime': '2023-01-01T10:00:00Z',
                'value': 25.5
            },
            {
                'deviceId': 'device_002', 
                'observationDateTime': '2023-01-01T11:00:00Z',
                'value': 30.2
            },
            {
                'deviceId': 'device_001',
                'observationDateTime': '2023-01-01T12:00:00Z', 
                'value': 28.1
            }
        ]
    
    @pytest.fixture
    def sample_dataframe(self):
        """Sample DataFrame for testing"""
        data = {
            'deviceId': ['device_001', 'device_002', 'device_001', 'device_002'],
            'observationDateTime': [
                '2023-01-01T10:00:00Z',
                '2023-01-01T11:00:00Z', 
                '2023-01-01T12:00:00Z',
                '2023-01-01T13:00:00Z'
            ],
            'IAT': [10, 20, 15, 25],
            'value': [25.5, 30.2, 28.1, 32.4]
        }
        return pd.DataFrame(data)

    def test_readFile_success(self, sample_config, sample_json_data):
        """Test successful file reading"""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.load') as mock_json_load:
                # First call returns config, second call returns data
                mock_json_load.side_effect = [sample_config, sample_json_data]
                
                result = pp.readFile('test_config.json')
                
                # Verify return values
                assert len(result) == 9
                configDict, df, input1, input2, datasetName, fileName, URL, alpha, schema = result
                
                assert configDict == sample_config
                assert input1 == 'deviceId'
                assert input2 == 'observationDateTime'
                assert datasetName == 'Test Dataset'
                assert alpha == [0.1, 0.2, 0.3]
                assert isinstance(df, pd.DataFrame)

    def test_timeRange(self, sample_dataframe):
        """Test time range calculation"""
        result = pp.timeRange(sample_dataframe)
        startTime, endTime, startMonth, endMonth, startYear, endYear = result
        
        assert isinstance(startTime, pd.Timestamp)
        assert isinstance(endTime, pd.Timestamp)
        assert startMonth == 'Jan'
        assert endMonth == 'Jan'
        assert startYear == 23  # 2023 - 2000
        assert endYear == 23

    def test_dropDupes(self, sample_dataframe, capsys):
        """Test duplicate removal"""
        # Add duplicate row
        duplicate_row = sample_dataframe.iloc[0:1].copy()
        df_with_dupes = pd.concat([sample_dataframe, duplicate_row], ignore_index=True)
        
        result_df, dupe_count = pp.dropDupes(df_with_dupes, 'deviceId', 'observationDateTime')
        
        assert dupe_count == 1
        assert len(result_df) == len(sample_dataframe)
        
        # Check printed output
        captured = capsys.readouterr()
        assert '1 duplicate rows have been removed.' in captured.out

    def test_outRemove(self, sample_dataframe):
        """Test outlier removal using IQR method"""
        # Add some extreme outliers
        sample_dataframe.loc[len(sample_dataframe)] = ['device_003', '2023-01-01T14:00:00Z', 1000, 35.0]
        sample_dataframe.loc[len(sample_dataframe)] = ['device_004', '2023-01-01T15:00:00Z', -100, 40.0]
        
        result_df, lower, upper = pp.outRemove(sample_dataframe, 'test_data.json', 'deviceId')
        
        assert isinstance(result_df, pd.DataFrame)
        assert isinstance(lower, float)
        assert isinstance(upper, float)
        assert 'idTrunc' in result_df.columns
        assert len(result_df) <= len(sample_dataframe)

    def test_dataStats(self, sample_dataframe):
        """Test statistical calculations"""
        result = pp.dataStats(sample_dataframe)
        mean, median, mode, std, variance, skew, kurtosis = result
        
        assert isinstance(mean, int)
        assert isinstance(median, int)
        assert isinstance(mode, int)
        assert isinstance(std, int)
        assert isinstance(variance, int)
        assert isinstance(skew, int)
        assert isinstance(kurtosis, int)

    @patch('pygal.Radar')
    def test_radarChart(self, mock_radar):
        """Test radar chart creation"""
        mock_chart = MagicMock()
        mock_radar.return_value = mock_chart
        
        pp.radarChart(0.8, 0.9, 0.7, 0.85, 0.95, 0.6)
        
        mock_radar.assert_called_once()
        assert mock_chart.add.call_count == 2
        mock_chart.render_to_png.assert_called_once_with('../plots/radarPlot.png')

    def test_dropDupes_no_duplicates(self, sample_dataframe):
        """Test dropDupes with no duplicates"""
        result_df, dupe_count = pp.dropDupes(sample_dataframe, 'deviceId', 'observationDateTime')
        
        assert dupe_count == 0
        assert len(result_df) == len(sample_dataframe)


if __name__ == "__main__":
    pytest.main([__file__])