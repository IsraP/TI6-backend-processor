from pymongo import MongoClient as mc


class MongoClient:

    def createConnection(self):
        return mc("mongodb://44.198.5.220:27017", connect=False).TI6.mamografias # oof security

    def getNonProcessedImages(self):
        return self.createConnection().find({
            "processado": False
        })

    def getNonClassifiedImages(self):
        return self.createConnection().find({
            "processado": True,
            "classificado": False
        })

    def updateImage(self, newDocument):
        self.createConnection().update_one({'_id':newDocument["_id"]}, {"$set": newDocument}, upsert=False)
