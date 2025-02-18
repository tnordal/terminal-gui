import os
import pytest
import toml
from terminal_gui.config import load_config, save_config

def test_load_config_success(temp_config_file, sample_config_data):
    """Test successful config loading"""
    config_data = load_config(temp_config_file)
    assert isinstance(config_data, dict)
    assert config_data == sample_config_data
    assert 'menu' in config_data
    assert 'items' in config_data['menu']

def test_load_config_file_not_found():
    """Test loading non-existent config file"""
    with pytest.raises(FileNotFoundError):
        load_config('nonexistent_config.toml')

def test_save_config_success(tmp_path, sample_config_data):
    """Test successful config saving"""
    config_file = tmp_path / 'test_save_config.toml'
    save_config(str(config_file), sample_config_data)
    
    assert config_file.exists()
    with open(config_file, 'r') as file:
        loaded_data = toml.load(file)
    assert loaded_data == sample_config_data

def test_save_config_invalid_path(sample_config_data):
    """Test saving config to invalid path"""
    with pytest.raises(OSError):
        save_config('/invalid/path/config.toml', sample_config_data)