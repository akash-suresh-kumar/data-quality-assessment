import pytest
import json
import tempfile
import os
import sys

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
    from metrics.required_fields_validation import validate_requiredFields
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
class TestRequiredFieldsValidation:
    
    @pytest.fixture
    def required_fields_set(self):
        """Sample set of required fields"""
        return {"name", "age", "email", "id"}
    
    @pytest.fixture
    def complete_data_file(self):
        """Create a temporary file with complete data (all required fields present)"""
        complete_data = [
            {"name": "John", "age": 30, "email": "john@example.com", "id": 1},
            {"name": "Jane", "age": 25, "email": "jane@example.com", "id": 2},
            {"name": "Bob", "age": 35, "email": "bob@example.com", "id": 3}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(complete_data, f)
            return f.name
    
    @pytest.fixture
    def missing_fields_data_file(self):
        """Create a temporary file with missing required fields"""
        missing_data = [
            {"name": "John", "age": 30, "email": "john@example.com"},  # Missing 'id'
            {"name": "Jane", "age": 25, "id": 2},  # Missing 'email'
            {"age": 35, "email": "bob@example.com", "id": 3},  # Missing 'name'
            {"name": "Alice", "id": 4}  # Missing 'age' and 'email'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(missing_data, f)
            return f.name
    
    @pytest.fixture
    def null_values_data_file(self):
        """Create a temporary file with null values (treated as missing)"""
        null_data = [
            {"name": "John", "age": 30, "email": None, "id": 1},  # email is null
            {"name": None, "age": 25, "email": "jane@example.com", "id": 2},  # name is null
            {"name": "Bob", "age": None, "email": None, "id": 3},  # age and email are null
            {"name": "Alice", "age": 28, "email": "alice@example.com", "id": None}  # id is null
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(null_data, f)
            return f.name
    
    @pytest.fixture
    def mixed_data_file(self):
        """Create a temporary file with mixed scenarios"""
        mixed_data = [
            {"name": "Complete", "age": 30, "email": "complete@example.com", "id": 1},
            {"name": "Missing", "age": 25},  # Missing email and id
            {"name": None, "age": 35, "email": "null@example.com", "id": 3},  # name is null
            {"age": 40, "email": "partial@example.com"},  # Missing name and id
            {"name": "Another", "age": None, "email": None, "id": 5}  # age and email are null
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(mixed_data, f)
            return f.name
    
    def teardown_method(self):
        """Clean up temporary files"""
        for filename in os.listdir('.'):
            if filename.endswith('.json') and filename.startswith('tmp'):
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
    
    def test_all_fields_present(self, required_fields_set, complete_data_file):
        """Test when all required fields are present in all records"""
        num_samples, num_missing_prop = validate_requiredFields(complete_data_file, required_fields_set)
        
        assert num_samples == 3
        assert num_missing_prop == 0
    
    def test_missing_fields(self, required_fields_set, missing_fields_data_file):
        """Test when some required fields are missing"""
        num_samples, num_missing_prop = validate_requiredFields(missing_fields_data_file, required_fields_set)
        
        assert num_samples == 4
        # Record 1: missing 'id' (1 missing)
        # Record 2: missing 'email' (1 missing)
        # Record 3: missing 'name' (1 missing)
        # Record 4: missing 'age' and 'email' (2 missing)
        assert num_missing_prop == 5
    
    def test_null_values_treated_as_missing(self, required_fields_set, null_values_data_file):
        """Test that null values are treated as missing attributes"""
        num_samples, num_missing_prop = validate_requiredFields(null_values_data_file, required_fields_set)
        
        assert num_samples == 4
        # Record 1: email is null (1 missing)
        # Record 2: name is null (1 missing)
        # Record 3: age and email are null (2 missing)
        # Record 4: id is null (1 missing)
        assert num_missing_prop == 5
    
    def test_mixed_scenarios(self, required_fields_set, mixed_data_file):
        """Test mixed scenarios with complete, missing, and null values"""
        num_samples, num_missing_prop = validate_requiredFields(mixed_data_file, required_fields_set)
        
        assert num_samples == 5
        # Record 1: complete (0 missing)
        # Record 2: missing email and id (2 missing)
        # Record 3: name is null (1 missing)
        # Record 4: missing name and id (2 missing)
        # Record 5: age and email are null (2 missing)
        assert num_missing_prop == 7
    
    def test_empty_required_fields_set(self, complete_data_file):
        """Test with empty set of required fields"""
        empty_set = set()
        num_samples, num_missing_prop = validate_requiredFields(complete_data_file, empty_set)
        
        assert num_samples == 3
        assert num_missing_prop == 0
    
    def test_empty_data_file(self, required_fields_set):
        """Test with empty JSON array"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump([], f)
            temp_file = f.name
        
        try:
            num_samples, num_missing_prop = validate_requiredFields(temp_file, required_fields_set)
            
            assert num_samples == 0
            assert num_missing_prop == 0
        finally:
            os.unlink(temp_file)
    
    def test_single_record_all_missing(self, required_fields_set):
        """Test with single record missing all required fields"""
        single_record = [{"extra_field": "value"}]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(single_record, f)
            temp_file = f.name
        
        try:
            num_samples, num_missing_prop = validate_requiredFields(temp_file, required_fields_set)
            
            assert num_samples == 1
            assert num_missing_prop == 4  # All 4 required fields missing
        finally:
            os.unlink(temp_file)
    
    def test_single_record_all_null(self, required_fields_set):
        """Test with single record where all required fields are null"""
        single_record = [{"name": None, "age": None, "email": None, "id": None}]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(single_record, f)
            temp_file = f.name
        
        try:
            num_samples, num_missing_prop = validate_requiredFields(temp_file, required_fields_set)
            
            assert num_samples == 1
            assert num_missing_prop == 4  # All 4 required fields are null (treated as missing)
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found(self, required_fields_set):
        """Test with non-existent file"""
        with pytest.raises(FileNotFoundError):
            validate_requiredFields("non_existent_file.json", required_fields_set)
    
    def test_large_required_fields_set(self, complete_data_file):
        """Test with large set of required fields"""
        large_set = {f"field_{i}" for i in range(100)}
        num_samples, num_missing_prop = validate_requiredFields(complete_data_file, large_set)
        
        assert num_samples == 3
        # Each record should be missing most of the 100 required fields
        assert num_missing_prop > 250  # Approximately 100 missing per record * 3 records
    
    def test_extra_fields_ignored(self, required_fields_set):
        """Test that extra fields (not in required set) are ignored"""
        data_with_extra = [
            {
                "name": "John", "age": 30, "email": "john@example.com", "id": 1,
                "extra1": "value1", "extra2": "value2", "extra3": "value3"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data_with_extra, f)
            temp_file = f.name
        
        try:
            num_samples, num_missing_prop = validate_requiredFields(temp_file, required_fields_set)
            
            assert num_samples == 1
            assert num_missing_prop == 0  # All required fields are present
        finally:
            os.unlink(temp_file)
    
    def test_partial_overlap_required_fields(self):
        """Test with required fields that partially overlap with data fields"""
        partial_required = {"name", "age", "non_existent_field"}
        data = [
            {"name": "John", "age": 30, "email": "john@example.com"},
            {"name": "Jane", "id": 2}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            num_samples, num_missing_prop = validate_requiredFields(temp_file, partial_required)
            
            assert num_samples == 2
            # Record 1: missing 'non_existent_field' (1 missing)
            # Record 2: missing 'age' and 'non_existent_field' (2 missing)
            assert num_missing_prop == 3
        finally:
            os.unlink(temp_file)
