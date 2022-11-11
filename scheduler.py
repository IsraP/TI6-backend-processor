from apscheduler.schedulers.blocking import BlockingScheduler
from job.job import Job
from datetime import datetime


job = Job()

sched = BlockingScheduler()


def process():
    print("[Serviço - %s] - Iniciando execução do serviço" % datetime.now())

    job.executeJob()

    print("[Serviço - %s] - Execução finalizada" % datetime.now())


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(process, 'interval', seconds=5)
    
    print("\nIniciando agendador")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass