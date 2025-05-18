# Testes para plugins do LocalJarvis
import pytest
from plugins.media_control import Plugin as MediaControlPlugin
from plugins.weather_plugin import Plugin as WeatherPlugin

def test_media_control_can_handle():
    plugin = MediaControlPlugin({})
    assert plugin.can_handle("play música")
    assert plugin.can_handle("pause música")
    assert not plugin.can_handle("abrir bloco de notas")

def test_weather_plugin_can_handle():
    plugin = WeatherPlugin({'api_key': ''})
    assert plugin.can_handle("qual o clima?")
    assert not plugin.can_handle("abrir notepad")

def test_weather_plugin_handle():
    plugin = WeatherPlugin({'api_key': ''})
    resposta = plugin.handle("qual o clima?")
    assert "Plugin de clima" in resposta

def test_plugin_interface_process():
    plugin = MediaControlPlugin({})
    # Usa handle se process não existir
    if hasattr(plugin, 'process'):
        result = plugin.process("play música")
        assert result is not None
    elif hasattr(plugin, 'handle'):
        result = plugin.handle("play música")
        assert result is not None
    plugin2 = WeatherPlugin({'api_key': ''})
    if hasattr(plugin2, 'process'):
        result2 = plugin2.process("qual o clima?")
        assert result2 is not None
    elif hasattr(plugin2, 'handle'):
        result2 = plugin2.handle("qual o clima?")
        assert result2 is not None
