import pytest
from memory.memory_manager import MemoryManager

def test_memory_manager():
    memory = MemoryManager(":memory:")
    memory.store_interaction("Teste", "Resposta")
    context = memory.get_context()
    assert "Teste" in context
    assert "Resposta" in context
