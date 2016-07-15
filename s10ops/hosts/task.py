#_*_coding:utf-8_*_
__author__ = 'alex'
from django.db import transaction
import models,os,json
import subprocess
from s10ops import settings



class Task(object):
    def __init__(self,request):
        self.request= request
        self.task_type = self.request.POST.get("task_type")

    def handle(self):
        if self.task_type:
            if hasattr(self,self.task_type):
                func = getattr(self,self.task_type)#执行某个函数
                return func()
            else:
                raise TypeError
    @transaction.atomic#装饰器，等函数都执行完了，同一的commit一次，存到mysql中
    def multi_cmd(self):
        print '---going to run cmd----'
        print self.request.POST
        selected_hosts = set(self.request.POST.getlist("selected_hosts[]"))#set 去重
        cmd = self.request.POST.get("cmd")
        print '-->',selected_hosts,cmd
         #create task info
        task_obj = models.TaskLog(  #创建任务信息
            task_type = self.task_type,
            user_id = self.request.user.id,
            #manytomany 必须在创建完记录后再添加
            cmd = cmd,
        )
        task_obj.save()#存到内存中
        task_obj.hosts.add(*selected_hosts)#add()里必须加数字，加*把列表变成数字，并添加manytomany关系

        #在任务详情表里，如果有100台主机，就创建100条记录
        for bind_host_id in selected_hosts:
            obj = models.TaskLogDetail(
                child_of_task_id = task_obj.id,
                bind_host_id = bind_host_id,
                event_log = "N/A",
            )
            obj.save()#存到内存中

        #invoke backend multitask scrip
        p = subprocess.Popen([
            'python',
            settings.MultiTaskScript,
            '-task_id',str(task_obj.id),
            '-run_type',settings.MultiTaskRunType,
        ],preexec_fn=os.setsid)
        print '----->pid',p.pid
        return {'task_id':task_obj.id}

    def multi_file_transfer(self):
        print ' ---going to handle file uploading/download '
        selected_hosts = set(self.request.POST.getlist("selected_hosts[]"))#set 去重
        transfer_type = self.request.POST.get("file_transfer_type")
        remote_path = self.request.POST.get("remote_path")
        upload_files = self.request.POST.getlist("upload_files[]")
        #create task info
        #把上传的路径和文件名转成json格式传的数据库中
        data_dic = {
            'remote_path':remote_path,
            'upload_files':upload_files,

        }

        task_obj = models.TaskLog(  #创建任务信息
            task_type = transfer_type,
            user_id = self.request.user.id,
            #manytomany 必须在创建完记录后再添加
            cmd = json.dumps(data_dic),
        )
        task_obj.save()#存到内存中
        task_obj.hosts.add(*selected_hosts)#add()里必须加数字，加*把列表变成数字，并添加manytomany关系

        #在任务详情表里，如果有100台主机，就创建100条记录
        for bind_host_id in selected_hosts:
            obj = models.TaskLogDetail(
                child_of_task_id = task_obj.id,
                bind_host_id = bind_host_id,
                event_log = "N/A",
            )
            obj.save()#存到内存中

        #invoke backend multitask scrip
        p = subprocess.Popen([
            'python',
            settings.MultiTaskScript,
            '-task_id',str(task_obj.id),
            '-run_type',settings.MultiTaskRunType,
        ],preexec_fn=os.setsid)
        print '----->pid',p.pid
        return {'task_id':task_obj.id}



    def get_task_result(self):
        task_id = self.request.GET.get('task_id')
        if task_id:#如果存在
            res_list = models.TaskLogDetail.objects.filter(child_of_task_id=task_id)
            return list(res_list.values('id',
                                        'bind_host__host__hostname',
                                        'bind_host__host__ip_addr',
                                        'bind_host__host_user__username',
                                        'date',
                                        'event_log',
                                        'result'

                                        ))