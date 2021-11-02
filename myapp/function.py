import os
import re
import cv2
import uuid
import base64
import numpy as np
import shutil
import zipfile
import pydicom
import SimpleITK
from .models import *

def unzip(fName):
    zfile = zipfile.ZipFile(os.path.join('./', 'resources', 'zipTemp', fName))
    zfile.extractall(os.path.join('./', 'resources', 'dcmTemp'))
    zfile.close()

def importZip(Position):
    rootdir = './resources/dcmTemp'
    url = "http://127.0.0.1:8000/"
    list = os.listdir(rootdir)
    for item in list:
        name = str(uuid.uuid4()).replace('-','') + '.' + item.split(".")[1]   #对每个dcm文件产生唯一id
        path = os.path.join(rootdir, item)
        dcm = pydicom.dcmread(path, force=True)  #读取dicom文件
        info = {}
        # info["PatientName"] = str(dcm.PatientName).split(" ")[0]  #清洗姓名
        info["PatientAge"] = dcm.PatientAge
        info["PatientAge"] = re.sub("\D", "", info["PatientAge"])  #把字符串中的数字提取出来
        info["PatientAge"] = int(info["PatientAge"])  #把字符串的064转化成数字64
        if dcm.PatientSex == 'F':
            info['PatientSex'] = '女'
        elif dcm.PatientSex == 'M':
            info['PatientSex'] = '男'
        # info['PatientSex'] = dcm.PatientSex
        info['Position'] = Position
        info['Url'] = url + "resources/" + name
        #存入数据库
        Patient.objects.create(gender=info['PatientSex'], age=info["PatientAge"], position=info['Position'], url=info['Url'])
        #重命名后移入resources目录下长期存储
        os.rename(path, name)
        shutil.move(name, './resources')

def importSingle(info, path, fname):
    url = "http://127.0.0.1:8000/"
    name = str(uuid.uuid4()).replace('-','') + '.' + fname.split(".")[1]   #对每个dcm文件产生唯一id
    print(name)
    dcm = pydicom.dcmread(path, force=True)  #读取dicom文件
    # if(dcm.PatientName != ''): 
    #     info["name"] = str(dcm.PatientName).split(" ")[0]
    if(info['gender'] == '' and dcm.PatientSex != ''):
        if dcm.PatientSex == 'F':
            info['gender'] = '女'
        elif dcm.PatientSex == 'M':
            info['gender'] = '男'
    if(info["age"] == '' and dcm.PatientAge != ''):
        info["age"] = dcm.PatientAge
        info["age"] = re.sub("\D", "", info["age"])
        info["age"] = int(info["age"])

    info['url'] = url + "resources/" + name
    os.rename(path, name)
    Patient.objects.create(gender=info['gender'], age=info["age"], position=info['position'], url=info['url'])
    shutil.move(name, './resources')

def deleteDcm(url):
    dcm_file_path = url.split('/', 3)[3]  #  resources/xxxxx.dcm
    dcm_file_path = os.path.join('./', dcm_file_path)
    os.remove(dcm_file_path)

def get_pixels_by_simpleitk(dicom_dir):
    ds = SimpleITK.ReadImage(dicom_dir)
    img_array = SimpleITK.GetArrayFromImage(ds)
    img_array[img_array == -2000] = 0
    return img_array

def dcm2img(dcm_url):
    dcm_file_path = dcm_url.split('/', 3)[3]  #  resources/xxxxx.dcm
    dcm_file_path = os.path.join('./', dcm_file_path)
    jpgName = 'temp.jpg'
    jpg_file_path = os.path.join('./', 'resources', 'jpgTemp', jpgName)
    img = get_pixels_by_simpleitk(dcm_file_path)
    # print(np.min(img), np.max(img)-np.min(img))
    scaled_img = cv2.convertScaleAbs(img-np.min(img), alpha=(255.0 / min(np.max(img)-np.min(img), 10000)))
    cv2.imwrite(jpg_file_path, scaled_img[0])
    with open(jpg_file_path, 'rb') as f:
        image = f.read()
        image_base64 = base64.b64encode(image)
        return image_base64


