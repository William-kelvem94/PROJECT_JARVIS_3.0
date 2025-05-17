import pytest
from command_execution.program_executor import ProgramExecutor

def test_program_executor_allowed():
    executor = ProgramExecutor(["notepad"])
    result = executor.execute("notepad")
    assert "Comando executado" in result or "notepad" in result
