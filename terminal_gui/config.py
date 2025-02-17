import toml

def load_config(file_path):
    with open(file_path, 'r') as file:
        return toml.load(file)

def save_config(file_path, config_data):
    with open(file_path, 'w') as file:
        toml.dump(config_data, file)

def get_menu_colors(config):
    return config.get('menu_colors', {
        'background': '#ffffff',
        'text': '#000000',
        'highlight': '#ff0000'
    })