import base64
import requests
import os, glob
from multiprocessing import Pool


def sendImage(filename):
    with open(os.path.join(os.getcwd(), filename), 'rb') as file:
            encoded_string = base64.b64encode(file.read()).decode("utf-8")
            
            API_ENDPOINT = "http://44.198.5.220:8000/mamografias/"
            

            data = {
                'imagem':encoded_string,
                'rotulo':os.path.basename(file.name),
            }
            
            # sending post request and saving response as response object
            r = requests.post(url = API_ENDPOINT, data = data)

path = './MamaPoss/'
files = glob.glob(os.path.join(path, '*.jpg'))
   
with Pool(4) as p:
    p.map(sendImage, list(files))
