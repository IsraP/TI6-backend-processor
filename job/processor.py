import datetime
from multiprocessing import Pool
from db.mongo_connection import MongoClient


class Processor:
    def __init__(self):
        self.client = MongoClient()


    def processImage(self, entry):
        currentClient = MongoClient()

        print("[Processador] - Processando imagem " + entry["rotulo"])

        # processa imagens

        entry["processado"] = True
        entry["imagem_processada"] = "PROCESSEI"
        entry["data_processamento"] = datetime.datetime.utcnow()

        currentClient.updateImage(entry)
        print("[Processador] - Fim do processamento da imagem " + entry["rotulo"])

            
    def processImages(self):
        nonProcessedEntries = self.client.getNonProcessedImages()

        with Pool(3) as p:
            p.map(self.processImage, list(nonProcessedEntries))
        