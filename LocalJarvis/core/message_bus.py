from queue import Queue
from threading import Thread

class MessageBus:
    def __init__(self):
        self.queue = Queue()
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data):
        self.queue.put((event_type, data))

    def start(self):
        def run():
            while True:
                event_type, data = self.queue.get()
                for callback in self.subscribers.get(event_type, []):
                    callback(data)
        Thread(target=run, daemon=True).start()

# Exemplo de uso:
# bus = MessageBus()
# bus.subscribe('greet', lambda data: print('Olá', data))
# bus.publish('greet', 'usuário')
# bus.start()
