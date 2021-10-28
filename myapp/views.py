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
    position = request.POST.get("position")  #前端传递的当前影像位置
    print('uplaod_file_name => ', fp.name)
    print(position)
    # fp 获取到的上传文件对象
    if fp:
        fpName = str(time.time())+fp.name
        path = os.path.join('./', 'static', 'zipTemp', fpName)
        if fp.multiple_chunks():
            file_yield = fp.chunks()  # 迭代写入文件
            with open(path,'wb') as f:
                for buf in file_yield:   # for情况执行无误才执行 else
                    f.write(buf)
                else:
                    print("大文件上传完毕")
        else:
            with open(path,'wb') as f:
                f.write(fp.read())
                print("小文件上传完毕")

        unzip(fpName)
        importZip(position)  #传递位置参数，让rename可以向数据库添加记录
        os.remove(path) #删除上传的zip文件
    else:
        error = "文件上传为空"
    resp = {"isSuccess":True}
    return HttpResponse(json.dumps(resp), content_type="application/json")

def uploadSingle(request):
    fp = request.FILES.get("file")
    info = {}
    info["name"] = request.POST.get("name")
    info["gender"] = request.POST.get("gender")
    info["age"] = request.POST.get("age")
    info["position"] = request.POST.get("position")
    print('uplaod_file_name => ', fp.name)
    print(info)

    if fp:
        fpName = fp.name
        path = os.path.join('./', 'static', 'dcmTemp', fpName)
        if fp.multiple_chunks():
            file_yield = fp.chunks()  # 迭代写入文件
            with open(path,'wb') as f:
                for buf in file_yield:   # for情况执行无误才执行 else
                    f.write(buf)
                else:
                    print("大文件上传完毕")
        else:
            with open(path,'wb') as f:
                f.write(fp.read())
                print("小文件上传完毕")

        importSingle(info, path, fpName) #传入表单信息，文件路径和文件名
    else:
        error = "文件上传为空"
    resp = {"isSuccess":True}
    return HttpResponse(json.dumps(resp), content_type="application/json")




