from pymongo import MongoClient as mc


class MongoClient:

    def createConnection(self):
        return mc("mongodb://44.198.5.220:27017", connect=False) # oof security

    def getNonProcessedImages(self):
        return self.createConnection().TI6.mamografias.find({
            "processado": False
        }).limit(8)

    def getNonClassifiedImages(self):
        return self.createConnection().TI6.mamografias.find({
            "processado": True,
            "classificado": False
        }).limit(8)

    def updateImage(self, newDocument):
       con = self.createConnection()
       con.TI6.mamografias.update_one({'_id':newDocument["_id"]}, {"$set": newDocument}, upsert=False)
       con.close()