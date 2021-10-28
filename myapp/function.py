import os
import uuid
import shutil
import zipfile
import pydicom
from .models import *

def unzip(fName):
    zfile = zipfile.ZipFile(os.path.join('./', 'resources', 'zipTemp', fName))
    zfile.extractall(os.path.join('./', 'resources', 'dcmTemp'))
    zfile.close()

def importZip(Position):
    rootdir = './resources/dcmTemp'
    url = "http://127.0.0.1:8002/"
    list = os.listdir(rootdir)
    for item in list:
        name = str(uuid.uuid4()).replace('-','') + '.' + item.split(".")[1]   #对每个dcm文件产生唯一id
        path = os.path.join(rootdir, item)
        dcm = pydicom.dcmread(path, force=True)  #读取dicom文件
        info = {}
        info["PatientName"] = str(dcm.PatientName).split(" ")[0]  #清洗姓名
        info["PatientAge"] = dcm.PatientAge
        if dcm.PatientSex == 'F':
            info['PatientSex'] = '女'
        elif dcm.PatientSex == 'M':
            info['PatientSex'] = '男'
        # info['PatientSex'] = dcm.PatientSex
        info['Position'] = Position
        info['Url'] = url + name
        #存入数据库
        Patient.objects.create(name=info["PatientName"], gender=info['PatientSex'], age=info["PatientAge"], position=info['Position'], url=info['Url'])
        #重命名后移入resources目录下长期存储
        os.rename(path, name)
        shutil.move(name, './resources')

def importSingle(info, path, fname):
    url = "http://127.0.0.1:8002/"
    name = str(uuid.uuid4()).replace('-','') + '.' + fname.split(".")[1]   #对每个dcm文件产生唯一id
    print(name)
    dcm = pydicom.dcmread(path, force=True)  #读取dicom文件
    if(dcm.PatientName != ''): 
        info["name"] = str(dcm.PatientName).split(" ")[0]
    if(dcm.PatientSex != ''):
        if dcm.PatientSex == 'F':
            info['gender'] = '女'
        elif dcm.PatientSex == 'M':
            info['gender'] = '男'
    if(dcm.PatientAge != ''):
        info["age"] = dcm.PatientAge

    info['url'] = url + name
    os.rename(path, name)
    Patient.objects.create(name=info["name"], gender=info['gender'], age=info["age"], position=info['position'], url=info['url'])
    shutil.move(name, './resources')

