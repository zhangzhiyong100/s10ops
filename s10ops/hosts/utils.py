#_*_coding:utf-8_*_
__author__ = 'jieli'

import time
import os,random
from s10ops import settings


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):   #如果obj里包含isoformat的方法表示是一个时间
        return obj.strftime("%Y-%m-%d ")  #把时间转化成字符串返回


def handle_upload_file(request,file_obj):
    random_dir = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890',6))

    upload_dir = '/%s/%s' %(settings.FileUploadDir,request.user.id)
    upload_dir2 = '/%s/%s' %(upload_dir,random_dir)
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    if not os.path.isdir(upload_dir2):
        os.mkdir(upload_dir2)
    with open('%s/%s' %(upload_dir2,file_obj.name),'wb') as destination :
        for chunk in file_obj.chunks():
            destination.write(chunk)

    return "%s/%s"%(random_dir,file_obj.name)