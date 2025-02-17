import os
import toml
from terminal_gui.config import load_config, save_config

def test_load_config():
    config_data = load_config('test_config.toml')
    assert isinstance(config_data, dict)

def test_save_config():
    config_data = {'key': 'value'}
    save_config('test_save_config.toml', config_data)
    assert os.path.exists('test_save_config.toml')
    with open('test_save_config.toml', 'r') as file:
        loaded_data = toml.load(file)
    assert loaded_data == config_data