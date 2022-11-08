import base64
import datetime
from io import BytesIO
from multiprocessing import Pool
from db.mongo_connection import MongoClient
import numpy as np
import cv2
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


    def processImage(self, entry):
        currentClient = MongoClient()

        print("[Processador] - Processando imagem " + entry["rotulo"])

        img:Image = Image.open(BytesIO(base64.b64decode(entry["imagem"])))

        img = img.filter(ImageFilter.GaussianBlur(radius=0))

        enhancer_sharpness = ImageEnhance.Sharpness(img)
        img = enhancer_sharpness.enhance(1.2)

        enhancer_contrast = ImageEnhance.Contrast(img)
        img = enhancer_contrast.enhance(2.8)

        enhancer_brightness = ImageEnhance.Brightness(img)
        img = enhancer_brightness.enhance(1.3)

        img = img.quantize(32)

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        img_str = img_str.decode("utf-8")

        entry["processado"] = True
        entry["imagem_processada"] = img_str
        entry["data_processamento"] = datetime.datetime.utcnow()

        currentClient.updateImage(entry)
        print("[Processador] - Fim do processamento da imagem " + entry["rotulo"])

            
    def processImages(self):
        start_time = time.time()

        nonProcessedEntries = self.client.getNonProcessedImages()

        for entry in list(nonProcessedEntries):
            self.processImage(entry)

        print("--- %s seconds ---" % (time.time() - start_time))

        # with Pool(3) as p:
        #     p.map(self.processImage, list(nonProcessedEntries))
        