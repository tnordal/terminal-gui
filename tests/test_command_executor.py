import os
import pytest
from terminal_gui.command_executor import CommandExecutor

def test_execute_shell_command(mocker):
    """Test shell command execution"""
    mock_popen = mocker.patch('subprocess.Popen')
    CommandExecutor.execute_command("shell", "echo test")
    mock_popen.assert_called_once_with("echo test", shell=True, cwd=os.getcwd())

def test_execute_python_command(mocker):
    """Test Python command execution"""
    mock_popen = mocker.patch('subprocess.Popen')
    CommandExecutor.execute_command("python", "test.py")
    mock_popen.assert_called_once_with(["python", "-m", "test.py"], cwd=os.getcwd())

def test_execute_program_command(mocker):
    """Test program command execution"""
    mock_popen = mocker.patch('subprocess.Popen')
    CommandExecutor.execute_command("program", "notepad test.txt")
    mock_popen.assert_called_once_with(["notepad", "test.txt"], cwd=os.getcwd())

def test_execute_command_with_working_dir(mocker):
    """Test command execution with custom working directory"""
    mock_popen = mocker.patch('subprocess.Popen')
    working_dir = "/tmp"
    CommandExecutor.execute_command("shell", "ls", working_dir)
    mock_popen.assert_called_once_with("ls", shell=True, cwd=working_dir)

def test_execute_invalid_command_type():
    """Test execution with invalid command type"""
    with pytest.raises(ValueError) as exc:
        CommandExecutor.execute_command("invalid", "test")
    assert "Unsupported command type: invalid" in str(exc.value)