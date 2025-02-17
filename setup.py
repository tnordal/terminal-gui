from setuptools import setup, find_packages

setup(
    name='terminal-gui',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'urwid',
        'toml',
    ],
    entry_points={
        'console_scripts': [
            'terminal-gui=terminal_gui.menu:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A Python package for creating terminal-based menu systems and configuration files.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/terminal-gui',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)