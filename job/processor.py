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
import skimage

class Processor:
    def __init__(self):
        self.client = MongoClient()
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.LOAD_TRUNCATED_IMAGES = True

    
    def cortarBordas(self, img, l=0.01, r=0.01, u=0.04, d=0.04):

        nrows, ncols, x = img.shape

        l_crop = int(ncols * l)
        r_crop = int(ncols * (1 - r))
        u_crop = int(nrows * u)
        d_crop = int(nrows * (1 - d))

        cropped_img = img[u_crop:d_crop, l_crop:r_crop]

        return cropped_img

    def normalizarMinMax(self, img):

        norm_img = (img - img.min()) / (img.max() - img.min())

        return norm_img

    def Binarizar(self, img, thresh, maxval):

        img_binarized = np.zeros(img.shape, np.uint8)  
        img_binarized[img >= thresh] = maxval
        return img_binarized

    def editMask(self, mask, ksize=(23, 23), operation="open"):

        kernel = cv.getStructuringElement(shape=cv.MORPH_RECT, ksize=ksize)

        if operation == "open":
            edited_mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        elif operation == "close":
            edited_mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

        edited_mask = cv.morphologyEx(edited_mask, cv.MORPH_DILATE, kernel)

        return edited_mask

    def OrdenaContornosPorArea(self, contours, reverse=True):


        sorted_contours = sorted(contours, key=cv.contourArea, reverse=reverse)


        bounding_boxes = [cv.boundingRect(c) for c in sorted_contours]

        return sorted_contours, bounding_boxes
    def EncontraMaiorArea(self, mask, top_x=None, reverse=True):


        mask = cv.cvtColor(mask, cv.COLOR_RGB2GRAY)
        contours, hierarchy = cv.findContours(
            image=mask, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_NONE
        )

        n_contours = len(contours)

        if n_contours > 0:

            if n_contours < top_x or top_x == None:
                top_x = n_contours
                
            
            # Sort contours based on contour area.
            sorted_contours, bounding_boxes = self.OrdenaContornosPorArea(
                contours=contours, reverse=reverse
            )

            # Get the top X largest contours.
            X_largest_contours = sorted_contours[0:top_x]

            # Create black canvas to draw contours on.
            to_draw_on = np.zeros(mask.shape, np.uint8)

            # Draw contours in X_largest_contours.
            X_largest_blobs = cv.drawContours(
                image=to_draw_on,  # Draw the contours on `to_draw_on`.
                contours=X_largest_contours,  # List of contours to draw.
                contourIdx=-1,  # Draw all contours in `contours`.
                color=1,  # Draw the contours in white.
                thickness=-1,  # Thickness of the contour lines.
            )

        return n_contours, X_largest_blobs

    def applyMask(self, img, mask):

        masked_img = img.copy()
        masked_img[mask == 0] = 0

        return masked_img

    def VerificarFlip(self, mask):

        # Get number of rows and columns in the image.
        nrows, ncols = mask.shape
        x_center = ncols // 2
        y_center = nrows // 2

        # Sum down each column.
        col_sum = mask.sum(axis=0)
        # Sum across each row.
        row_sum = mask.sum(axis=1)

        left_sum = sum(col_sum[0:x_center])
        right_sum = sum(col_sum[x_center:-1])

        if left_sum < right_sum:
            LR_flip = True
        else:
            LR_flip = False

        return LR_flip


    def FlipImagem(self, img):

        flipped_img = np.fliplr(img)

        return flipped_img

    def formatarImagem(self, img):
        g = self.Binarizar(img,0.1,255)
        e = self.editMask(g)
        x,y = self.EncontraMaiorArea(e,1)
        newImg = self.applyMask(img,y)
        if self.VerificarFlip(y):
            newImg = self.FlipImagem(newImg)
        return newImg

    def clahe(self, img, clip=2.0, tile=(8, 8)):

        img = cv.normalize(
            img,
            None,
            alpha=0,
            beta=255,
            norm_type=cv.NORM_MINMAX,
            dtype=cv.CV_32F,
        )

        img_uint8 = img.astype("uint8")
        gray_image = cv.cvtColor(img_uint8, cv.COLOR_BGR2GRAY)

        clahe_create = cv.createCLAHE(clipLimit=clip, tileGridSize=tile)

        clahe_img = clahe_create.apply(gray_image)

        return clahe_img

    def pad(self, img):

        nrows, ncols = img.shape

        if nrows != ncols:

            if ncols < nrows:
                target_shape = (nrows, nrows)
            elif nrows < ncols:
                target_shape = (ncols, ncols)

        
            padded_img = np.zeros(shape=target_shape)
            padded_img[:nrows, :ncols] = img

        elif nrows == ncols:

            padded_img = img

        return padded_img


    def readb64(self, uri):
        nparr = np.fromstring(base64.b64decode(uri), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        return img
    
    def writeb64(self, data):
        with BytesIO() as output_bytes:
            PIL_image = Image.fromarray(skimage.img_as_ubyte(data))
            PIL_image.save(output_bytes, 'JPEG') # Note JPG is not a vaild type here
            bytes_data = output_bytes.getvalue()

        # encode bytes to base64 string
        base64_str = str(base64.b64encode(bytes_data), 'utf-8')
        return base64_str


    def processImage(self, entry):
        currentClient = MongoClient()

        print("[Processador] - Processando imagem " + entry["rotulo"])

        data = self.readb64(entry["imagem"])

        img_cropped = self.cortarBordas(data)
        normalize = self.normalizarMinMax(img_cropped)
        noArtefact = self.formatarImagem(normalize)
        clahe_img = self.clahe(noArtefact)
        imagemQuadrado = self.pad(clahe_img)

        imagemQuadrado = np.array(imagemQuadrado, dtype=np.uint8)

        img_str = self.writeb64(imagemQuadrado)

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
        #     break
            
        with Pool(2) as p:
            p.map(self.processImage, list(nonProcessedEntries))

        print("--- %s seconds ---" % (time.time() - start_time))  