from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection, transaction
import os
import json
import time

from .models import *
from .function import *

# Create your views here.


def uploadZip(request):
    fp = request.FILES.get("file")
    position = request.POST.get("position")  # 前端传递的当前影像位置
    print('uplaod_file_name => ', fp.name)
    print(position)
    # fp 获取到的上传文件对象
    if fp:
        fpName = str(time.time())+fp.name
        path = os.path.join('./', 'resources', 'zipTemp', fpName)
        if fp.multiple_chunks():
            file_yield = fp.chunks()  # 迭代写入文件
            with open(path, 'wb') as f:
                for buf in file_yield:   # for情况执行无误才执行 else
                    f.write(buf)
                else:
                    print("大文件上传完毕")
        else:
            with open(path, 'wb') as f:
                f.write(fp.read())
                print("小文件上传完毕")

        unzip(fpName)
        importZip(position)  # 传递位置参数，让rename可以向数据库添加记录
        os.remove(path)  # 删除上传的zip文件
    else:
        error = "文件上传为空"
    resp = {"isSuccess": True}
    return HttpResponse(json.dumps(resp), content_type="application/json")


def uploadSingle(request):
    fp = request.FILES.get("file")
    info = {}
    # info["name"] = request.POST.get("name")
    info["gender"] = request.POST.get("gender")
    info["age"] = request.POST.get("age")
    info["position"] = request.POST.get("position")
    print('uplaod_file_name => ', fp.name)
    print(info)

    if fp:
        fpName = fp.name
        path = os.path.join('./', 'resources', 'dcmTemp', fpName)
        if fp.multiple_chunks():
            file_yield = fp.chunks()  # 迭代写入文件
            with open(path, 'wb') as f:
                for buf in file_yield:   # for情况执行无误才执行 else
                    f.write(buf)
                else:
                    print("大文件上传完毕")
        else:
            with open(path, 'wb') as f:
                f.write(fp.read())
                print("小文件上传完毕")

        importSingle(info, path, fpName)  # 传入表单信息，文件路径和文件名
    else:
        error = "文件上传为空"
    resp = {"isSuccess": True}
    return HttpResponse(json.dumps(resp), content_type="application/json")


def queryAll(request):
    resp = {"isSuccess": True, "msg": "success"}
    cursor = connection.cursor()
    cursor.execute('''select * from myapp_patient''')
    row = cursor.fetchall()
    resp['ret'] = row
    return HttpResponse(json.dumps(resp), content_type="application/json")


def deleteItem(request):
    msg = "delete success!"
    try:
        del_id = request.GET.get('id')
        del_url = Patient.objects.filter(id=del_id)[0].url
        deleteDcm(del_url)
        Patient.objects.filter(id=del_id).delete()
    except Exception as e:
        msg = "delete failed! " + str(e)
    resp = {"isSuccess": True, "msg": msg}
    return HttpResponse(json.dumps(resp), content_type="application/json")


def viewDcm(request):
    dcm_url = request.GET.get('url')
    img_base64 = dcm2img(dcm_url)
    os.remove('./resources/jpgTemp/temp.jpg')  # 删除临时jpg文件
    return HttpResponse(img_base64, content_type='image/jpeg')


def viewPng(request):
    img_url = request.GET.get('url')
    img_base64 = img2base64(img_url)
    return HttpResponse(img_base64, content_type='image/png')


def viewJpg(request):
    img_url = request.GET.get('url')
    img_base64 = img2base64(img_url)
    return HttpResponse(img_base64, content_type='image/jpeg')
