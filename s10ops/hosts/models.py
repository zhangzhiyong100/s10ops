#_*_coding:utf-8_*_

from django.db import models

# Create your models here.
from myauth import UserProfile

class Host(models.Model):
    hostname = models.CharField(max_length=64)
    ip_addr = models.GenericIPAddressField(unique=True)
    port = models.IntegerField(default=22)
    idc = models.ForeignKey('IDC')
    system_type_choices= (
        ('linux','Linux'),
        ('windows','Windows'),
    )
    system_type = models.CharField(choices=system_type_choices,max_length=32,default='linux')
    enabled = models.BooleanField(default=True)
    memo = models.TextField(blank=True,null=True)   #备注
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return  "%s(%s)" %(self.hostname,self.ip_addr)
    class Meta:#规定在前端页面的显示
        verbose_name = u'主机列表'
        verbose_name_plural = u"主机列表"
class IDC(models.Model):
    name = models.CharField(unique=True,max_length=64)
    memo = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return  self.name

class HostUser(models.Model):
    auth_type_choices = (
        ('ssh-password', 'SSH/PASSWORD'),
        ('ssh-key', 'SSH/KEY'),
    )
    auth_type = models.CharField(choices=auth_type_choices,max_length=32,default='ssh-password')
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=128,blank=True,null=True)

    def __unicode__(self):
        return "(%s)%s" %(self.auth_type,self.username)

    class Meta:
        unique_together = ('auth_type','username','password')
        verbose_name = u'远程主机用户'
        verbose_name_plural = u"远程主机用户"
class HostGroup(models.Model):
    name = models.CharField(unique=True,max_length=64)
    memo = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return  self.name
    class Meta:
        verbose_name = u'主机组'
        verbose_name_plural = u"主机组"
class BindHostToUser(models.Model):
    host = models.ForeignKey("Host")
    host_user= models.ForeignKey("HostUser")
    #host_user= models.ManyToManyField("HostUser")
    host_groups = models.ManyToManyField("HostGroup")

    class Meta:#规定在前端页面的显示
        unique_together = ('host','host_user')
        verbose_name = u'主机与用户绑定关系'
        verbose_name_plural = u"主机与用户绑定关系"
    def __unicode__(self):
        return  '%s:%s' %(self.host.hostname, self.host_user.username)


    def get_groups(self):#在manytomany时，自定义展现，在admin.py里引用

        return ','.join([g.name for g in self.host_groups.select_related()])


class TaskLog(models.Model):#存任务信息
    start_time = models.DateTimeField(auto_now_add=True)#任务开始时间
    end_time = models.DateTimeField(null=True,blank=True)#任务结束时间
    task_type_choices = (('multi_cmd',"CMD"),('file_send',"批量发送文件"),('file_get',"批量下载文件"))
    task_type = models.CharField(choices=task_type_choices,max_length=50)
    user = models.ForeignKey('UserProfile')
    hosts = models.ManyToManyField('BindHostToUser')
    cmd = models.TextField()#要执行的命令
    expire_time = models.IntegerField(default=30)#超时时间
    task_pid = models.IntegerField(default=0)#
    note = models.CharField(max_length=100,blank=True,null=True)#备注
    def __unicode__(self):
        return "taskid:%s cmd:%s" %(self.id,self.cmd)
    class Meta:
        verbose_name = u'批量任务'
        verbose_name_plural = u'批量任务'

class TaskLogDetail(models.Model):#存每个子任（单个主机）务返回的结果
    child_of_task = models.ForeignKey('TaskLog')#确定是哪个任务id的子任务
    bind_host  = models.ForeignKey('BindHostToUser')#确定是哪台主机
    date = models.DateTimeField(auto_now_add=True) #finished date
    event_log = models.TextField()#执行的输出
    result_choices= (('success','Success'),('failed','Failed'),('unknown','Unknown'))#执行的状态
    result = models.CharField(choices=result_choices,max_length=30,default='unknown')
    note = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return "child of:%s result:%s" %(self.child_of_task.id, self.result)
    class Meta:
        verbose_name = u'批量任务日志'
        verbose_name_plural = u'批量任务日志'