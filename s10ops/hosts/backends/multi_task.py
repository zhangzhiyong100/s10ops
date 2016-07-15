#_*_coding:utf-8_*_
__author__ = 'zhangzhiyong'

#print __file__  #当前文件的路径，相对路径
import os,sys
BaseDir ="/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])

sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s10ops.settings")
from hosts import models
import django
import multiprocessing  #多进程

from django.core.exceptions import ObjectDoesNotExist
import paramiko_handle

django.setup() #allow outsider scripts invoke django db models

def by_paramiko(task_id):
    try:
        task_obj = models.TaskLog.objects.get(id=task_id)
        pool = multiprocessing.Pool(processes=5)

        res = []
        if task_obj.task_type == 'multi_cmd':
            for h in task_obj.hosts.select_related():
                p = pool.apply_async(paramiko_handle.paramiko_ssh,args=(task_id,h,task_obj.cmd))
                res.append(p)
        elif task_obj.task_type in ('file_send','file_get'):
            for h in task_obj.hosts.select_related():
                p = pool.apply_async(paramiko_handle.paramiko_sftp,args=(task_id,h,task_obj.cmd,task_obj.task_type,task_obj.user.id))
                res.append(p)
        #for r in res:
        #    print r.get()
        pool.close()
        pool.join()

    except  ObjectDoesNotExist,e:
        sys.exit(e)


def by_ansible(task_id):
    pass

if __name__ == '__main__':
    required_args = ['-task_id','-run_type']
    for arg in required_args:
        if not arg in sys.argv:#如果没在
            sys.exit("arg [%s] is required!"% arg)

    if len(sys.argv) < 5:#至少有4个参数，小于5表示有问题
        sys.exit("5 arguments expected but %s given" % len(sys.argv))

    task_id = sys.argv[sys.argv.index("-task_id")+1]
    run_type = sys.argv[sys.argv.index("-run_type")+1]#根据ren_type调用相应的接口

    if hasattr(__import__(__name__),run_type):    #判断是否有这种方法
        func = getattr(__import__(__name__),run_type)#调用这种方法
        func(task_id)
    else:
        sys.exit("Invalid run_type, only support [by_paramiko,by_ansible,by_daltstack]" )

