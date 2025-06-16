import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
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
    from metrics.schema_validation_metrics import validate_data_with_schema
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
class TestSchemaValidationMetrics:
    
    @pytest.fixture
    def sample_schema(self):
        """Sample JSON schema for testing"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"],
            "additionalProperties": False
        }
    
    @pytest.fixture
    def valid_data_file(self):
        """Create a temporary file with valid JSON data"""
        valid_data = [
            {"name": "John Doe", "age": 30, "email": "john@example.com"},
            {"name": "Jane Smith", "age": 25, "email": "jane@example.com"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(valid_data, f)
            return f.name
    
    @pytest.fixture
    def invalid_data_file(self):
        """Create a temporary file with invalid JSON data"""
        invalid_data = [
            {"name": "John Doe", "age": 30},  # Valid
            {"name": "Jane Smith"},  # Missing required 'age'
            {"name": "Bob", "age": -5},  # Invalid age (negative)
            {"name": "Alice", "age": 25, "extra_field": "not allowed"}  # Additional property
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(invalid_data, f)
            return f.name
    
    @pytest.fixture
    def mixed_errors_file(self):
        """Create a temporary file with mixed validation errors"""
        mixed_data = [
            {"age": 30},  # Missing required 'name'
            {"name": "Test", "age": 25, "forbidden": "value"},  # Additional property
            {"name": "Another", "age": 30, "extra1": "val1", "extra2": "val2"}  # Additional properties
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(mixed_data, f)
            return f.name
    
    def teardown_method(self):
        """Clean up temporary files"""
        for filename in ['valid_data.json', 'invalid_data.json', 'mixed_errors.json']:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_validate_all_valid_data(self, sample_schema, valid_data_file):
        """Test validation with all valid data"""
        result = validate_data_with_schema(valid_data_file, sample_schema)
        num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
        
        assert num_samples == 2
        assert err_count == 0
        assert len(err_data_arr) == 0
        assert additional_prop_err_count == 0
        assert req_prop_err_count == 0
    
    def test_validate_with_errors(self, sample_schema, invalid_data_file):
        """Test validation with various error types"""
        result = validate_data_with_schema(invalid_data_file, sample_schema)
        num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
        
        assert num_samples == 4
        assert err_count > 0
        assert additional_prop_err_count > 0
        assert req_prop_err_count > 0
    
    def test_validate_mixed_errors(self, sample_schema, mixed_errors_file):
        """Test validation with mixed error types"""
        result = validate_data_with_schema(mixed_errors_file, sample_schema)
        num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
        
        assert num_samples == 3
        assert err_count == 3  # All records should have errors
        assert additional_prop_err_count == 2  # Two records with additional properties
        assert req_prop_err_count == 1  # One record missing required property
    
    def test_empty_file(self, sample_schema):
        """Test validation with empty JSON array"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump([], f)
            temp_file = f.name
        
        try:
            result = validate_data_with_schema(temp_file, sample_schema)
            num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
            
            assert num_samples == 0
            assert err_count == 0
            assert additional_prop_err_count == 0
            assert req_prop_err_count == 0
        finally:
            os.unlink(temp_file)
    
    def test_invalid_schema(self, valid_data_file):
        """Test with invalid schema"""
        invalid_schema = {
            "type": "invalid_type"  # Invalid schema
        }
        
        # This should handle schema errors gracefully and return zeros
        result = validate_data_with_schema(valid_data_file, invalid_schema)
        num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
        
        # When schema is invalid, function should return all zeros
        assert num_samples == 0
        assert err_count == 0
        assert additional_prop_err_count == 0
        assert req_prop_err_count == 0
        assert len(err_data_arr) == 0
    
    def test_file_not_found(self, sample_schema):
        """Test with non-existent file"""
        with pytest.raises(FileNotFoundError):
            validate_data_with_schema("non_existent_file.json", sample_schema)
    
    def test_required_property_error_detection(self, sample_schema):
        """Test specific detection of required property errors"""
        data_with_missing_required = [
            {"age": 30},  # Missing required 'name'
            {"name": "Test"}  # Missing required 'age'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data_with_missing_required, f)
            temp_file = f.name
        
        try:
            result = validate_data_with_schema(temp_file, sample_schema)
            num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
            
            assert num_samples == 2
            assert err_count == 2
            assert req_prop_err_count == 2  # Both records missing required properties
            assert additional_prop_err_count == 0
        finally:
            os.unlink(temp_file)
    
    def test_additional_property_error_detection(self, sample_schema):
        """Test specific detection of additional property errors"""
        data_with_additional_props = [
            {"name": "Test", "age": 30, "extra": "not allowed"},
            {"name": "Another", "age": 25, "forbidden": "value"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data_with_additional_props, f)
            temp_file = f.name
        
        try:
            result = validate_data_with_schema(temp_file, sample_schema)
            num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
            
            assert num_samples == 2
            assert err_count == 2
            assert additional_prop_err_count == 2  # Both records have additional properties
            assert req_prop_err_count == 0
        finally:
            os.unlink(temp_file)
    
    def test_complex_schema_validation(self):
        """Test with a more complex schema"""
        complex_schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "settings": {"type": "array"}
                            },
                            "required": ["name"]
                        }
                    },
                    "required": ["id", "profile"]
                }
            },
            "required": ["user"],
            "additionalProperties": False
        }
        
        complex_data = [
            {
                "user": {
                    "id": 1,
                    "profile": {
                        "name": "John",
                        "settings": ["opt1", "opt2"]
                    }
                }
            },
            {
                "user": {
                    "id": 2
                    # Missing required 'profile'
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(complex_data, f)
            temp_file = f.name
        
        try:
            result = validate_data_with_schema(temp_file, complex_schema)
            num_samples, err_count, err_data_arr, additional_prop_err_count, req_prop_err_count = result
            
            assert num_samples == 2
            assert err_count == 1  # One record with missing required property
        finally:
            os.unlink(temp_file)