import base64
import datetime
from io import BytesIO
from multiprocessing import Pool
from db.mongo_connection import MongoClient
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageFile
import time

class Processor:
    def __init__(self):
        self.client = MongoClient()
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.LOAD_TRUNCATED_IMAGES = True

    
    def crop(self, img):
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        blur = cv.GaussianBlur(img, (5, 5), 0)
        _, breast_mask = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        cnts, _ = cv.findContours(breast_mask.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnt = max(cnts, key=cv.contourArea)
        x, y, w, h = cv.boundingRect(cnt)
        return cv.cvtColor(img[y:y + h, x:x + w], cv.IMREAD_COLOR)

    def clahe(self, img):
        #contrast enhancement
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl_img = clahe.apply(img)

        return cl_img
        # cv.imwrite('clahe_2.jpg',cl_img)
        # data = cv.imread('clahe_2.jpg', cv.IMREAD_COLOR)
        # ret, thresh3 = cv.threshold(cl_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    def readb64(self, uri):
        nparr = np.fromstring(base64.b64decode(uri), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        return img
    
    def writeb64(self, data):
        b64_bytes = base64.b64encode(data)
        b64_string = b64_bytes.decode("utf-8")

        return b64_string


    def processImage(self, entry):
        currentClient = MongoClient()

        print("[Processador] - Processando imagem " + entry["rotulo"])

        data = self.readb64(entry["imagem"])
        img_cropped = self.crop(data)
        #normalization(img_cropped)
        data = self.clahe(img_cropped)

        img_str = self.writeb64(data)

        entry["processado"] = True
        entry["imagem_processada"] = img_str
        entry["data_processamento"] = datetime.datetime.utcnow()

        currentClient.updateImage(entry)
        print("[Processador] - Fim do processamento da imagem " + entry["rotulo"])

            
    def processImages(self):
        start_time = time.time()

        nonProcessedEntries = self.client.getNonProcessedImages()

        # for entry in list(nonProcessedEntries):
        #     self.processImage(entry)
            
        with Pool(8) as p:
            p.map(self.processImage, list(nonProcessedEntries))

        print("--- %s seconds ---" % (time.time() - start_time))  