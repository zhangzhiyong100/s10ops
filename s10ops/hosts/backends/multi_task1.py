#_*_coding:utf-8_*_
__author__ = 'zhangzhiyong'
import os,sys
import MySQLdb
BaseDir ="\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-2])
print BaseDir
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s10ops.settings")
from hosts import models


print models.Host.objects.all()