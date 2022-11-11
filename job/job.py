from multiprocessing import Pool
from db.mongo_connection import MongoClient
from job.processor import Processor
from job.classifier import Classifier

class Job:
    def __init__(self):
        self.client = MongoClient()

    def processImages(self, proc, size, nonProcessedEntries):
        with Pool(min(size, 4)) as p:
            results = p.map(proc.processImage, nonProcessedEntries)
        return results

    def classifyImages(self, clas, size, nonProcessedEntries):
        with Pool(min(size, 4)) as p:
            results = p.map(clas.classifyImage, nonProcessedEntries)
        return results


    def executeJob(self):
        proc = Processor()
        clas = Classifier()

        c = self.client.getNonProcessedImages()
        nonProcessedEntries = list(c)
        c.close()

        size = len(nonProcessedEntries)

        while(size > 0):
            processedEntries = self.processImages(proc, size, nonProcessedEntries)
            self.classifyImages(clas, size, processedEntries)

            j = self.client.getNonProcessedImages()
            nonProcessedEntries = list(j)
            j.close()

            size = len(nonProcessedEntries)