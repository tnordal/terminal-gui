from __future__ import annotations

import os
import subprocess
from typing import Optional


class CommandExecutor:
    @staticmethod
    def execute_command(command_type: str, command: str, working_dir: Optional[str] = None) -> None:
        """Execute a command based on its type."""
        cwd = working_dir or os.getcwd()
        
        if command_type == "shell":
            # Execute shell command
            subprocess.Popen(command, shell=True, cwd=cwd)
        elif command_type == "python":
            # Execute Python module/script
            subprocess.Popen(["python", "-m"] + command.split(), cwd=cwd)
        elif command_type == "program":
            # Start a program
            subprocess.Popen(command.split(), cwd=cwd)
        else:
            raise ValueError(f"Unsupported command type: {command_type}")