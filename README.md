# Terminal GUI

Terminal GUI is a Python package for creating sophisticated terminal-based menu systems with support for different menu styles, nested submenus, and customizable colors.

## Features

- Three menu styles:
  - Simple: Basic vertical menu
  - Horizontal: Expanding horizontal menu system
  - Cascading: Overlapping box style menu
- Nested submenus support
- Customizable colors using terminal colors or RGB hex values
- Keyboard navigation (arrow keys, ESC)
- TOML-based configuration

## Installation

```bash
uv add terminal-gui
```

## Usage

### Basic Menu Creation

```python
from terminal_gui.menu import Menu

# Create and run a menu from a config file
menu = Menu('menu_config.toml')
menu.main()
```

### Configuration File Format (menu_config.toml)

```toml
# Select menu type: "simple", "horizontal" (default), or "cascading"
menu_type = "horizontal"

[menu_structure]
heading = "Main Menu"
menu = [
    { name = "Menu 1", submenu = [
        { name = "Sub menu 1" },
        { name = "Sub menu 2" },
    ] },
    { name = "Menu 2", submenu = [
        { name = "Sub menu 1", submenu = [
            { name = "SubSub menu 1" },
            { name = "SubSub menu 2" },
        ] },
    ] },
]

# Color Configuration
[menu_colors]
# Default colors
default_fg = "black"     # Default text color
default_bg = "dark gray" # Default background color

# Heading colors
heading_fg = "light blue"      # Heading text color
heading_bg = "light gray"      # Heading background color
focus_heading_fg = "dark red"  # Focused heading text color
focus_heading_bg = "dark blue" # Focused heading background color

# Additional color configurations available for:
# - line_fg/bg: Separator line colors
# - focus_line_fg/bg: Focused line colors
# - options_fg/bg: Menu option colors
# - focus_options_fg/bg: Focused option colors
# - selected_fg/bg: Selected item colors

# Available colors:
# - Basic terminal colors: black, dark red, dark green, brown, dark blue,
#   dark magenta, dark cyan, light gray, dark gray, light red, light green,
#   yellow, light blue, light magenta, light cyan, white
# - RGB hex colors: e.g., "#ff0000" for red
```

## Navigation

- Arrow keys: Navigate through menu items
- Enter: Select menu item
- ESC: Go back/exit submenu
- Mouse: Click to select (if terminal supports it)

## Running Tests

To run the tests:

```bash
pytest
```

## License

MIT License