import importlib.util
import os

# Import dinâmico do MemoryManager
memory_manager_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory/memory_manager.py'))
spec = importlib.util.spec_from_file_location('memory_manager', memory_manager_path)
memory_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_manager)
MemoryManager = memory_manager.MemoryManager

def test_memory_manager():
    memory = MemoryManager(":memory:")
    memory._init_db()  # Garante que a tabela existe
    memory.store_interaction("Teste", "Resposta")
    context = memory.get_context()
    assert "Teste" in context
    assert "Resposta" in context
