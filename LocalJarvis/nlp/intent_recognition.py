# Exemplo de reconhecimento de intenção

def recognize_intent(text):
    # TODO: Integrar modelo real
    if 'tempo' in text:
        return 'weather_query'
    if 'tocar música' in text:
        return 'play_music'
    return 'unknown'
