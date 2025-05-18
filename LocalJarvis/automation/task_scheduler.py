# Exemplo de agendamento de tarefas
import schedule
import time

def job():
    print('Executando tarefa agendada!')

schedule.every(10).seconds.do(job)

# Em produção, rode isso em thread separada
# while True:
#     schedule.run_pending()
#     time.sleep(1)
