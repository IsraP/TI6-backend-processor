import datetime
from db.mongo_connection import MongoClient
from tensorflow.keras.models import load_model
from datetime import datetime
import numpy as np
import cv2 as cv
import base64
import tensorflow as tf

class Classifier:
    def __init__(self):
        self.client = MongoClient()

    def readb64(self, uri):
        nparr = np.fromstring(base64.b64decode(uri), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        return img

    def classifyImage(self, entry):
        currentClient = MongoClient()
        
        print("[Classificador %s]" % datetime.now() + " - Classificando imagem " + entry["rotulo"])

        new_model = load_model('./model/imageclassifier.h5')
        img = self.readb64(entry["imagem_processada"])
        img = tf.image.resize(img, (256,256))
        result = new_model.predict(np.expand_dims(img/255, 0))

        if(result < 0.5):
            tem_tumor = True
        else:
            tem_tumor = False

        entry["classificado"] = True
        entry["tem_tumor"] = tem_tumor
        entry["data_classificacao"] = datetime.utcnow()

        currentClient.updateImage(entry)
        print("[Classificador %s]" % datetime.now() + " - Fim da classificação da imagem " + entry["rotulo"])

