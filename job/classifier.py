import datetime
from multiprocessing import Pool
from db.mongo_connection import MongoClient


class Classifier:
    def __init__(self):
        self.client = MongoClient()


    def classifyImage(self, entry):
        currentClient = MongoClient()
        
        print("[Classificador] - Classificando imagem " + entry["rotulo"])
        
        # classifica imagens

        tem_tumor = False

        entry["classificado"] = True
        entry["tem_tumor"] = tem_tumor
        entry["data_classificacao"] = datetime.datetime.utcnow()

        currentClient.updateImage(entry)
        print("[Classificador] - Fim da Classificação da imagem " + entry["rotulo"])


    def classifyImages(self):
        nonClassifiedEntries = self.client.getNonClassifiedImages()

        with Pool(3) as p:
            p.map(self.classifyImage, list(nonClassifiedEntries))

        