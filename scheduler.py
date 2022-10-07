from apscheduler.schedulers.blocking import BlockingScheduler
from job.processor import Processor
from job.classifier import Classifier

proc = Processor()
clas = Classifier()

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=4)
def process():
    print("[Processador] - Iniciando processamento de imagens")

    proc.processImages()

    print("[Processador] - Processamento finalizado")

# @sched.scheduled_job('interval', seconds=8)
# def classify():
#     print("[Classificador] - Iniciando classificacão de imagens")

#     clas.classifyImages();

#     print("[Classificador] - Classificação finalizada")

print("Iniciando agendador")
sched.start()