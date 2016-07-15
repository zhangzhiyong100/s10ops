#_*_coding:utf-8_*_
__author__ = 'zhangzhiyong'

import time
import paramiko
from hosts import models
from django.utils import timezone
from s10ops import settings
import json
def paramiko_ssh(task_id,host_obj,task_content,task_type,user_id):
    bind_host = host_obj
    try:

        t = paramiko.Transport((bind_host.host.ip_addr,int(bind_host.host.port) ))
        if bind_host.host_user.auth_type == 'ssh-password':

            t.connect(username=bind_host.host_user.username,password=bind_host.host_user.password)
        sftp = paramiko.SFTPClient.from_transport(t)

        task_dic = json.loads(task_content)
        if task_type == 'file_send':
            upload_files = task_dic['upload_files']
            for file_path in upload_files:
                file_abs_path = "%s/%s/%s"%(settings.FileUploadDir,user_id,file_path)
                remote_filename = file_path.split("/")[-1]  #获取文件名
                print '----\033[32;1m sending [%s] to [%s]\033[0m'%(remote_filename,task_dic['remote_path'])
                sftp.put(file_abs_path,"%s/%s"%(task_dic['remote_path'],remote_filename))
            cmd_result = "successfully send files %s to remote path [%s]"%(upload_files,task_dic['remote_path'])
            result = 'success'
    except Exception,e:
        print e
        cmd_result = e
        result = 'failed'
    log_obj = models.TaskLogDetail.objects.get(child_of_task_id = task_id,bind_host_id = bind_host.id)
    log_obj.event_log = cmd_result
    log_obj.date = timezone.now()
    log_obj.result = result

    log_obj.save()


def paramiko_ssh(task_id,host_obj,task_content):

    print 'going to run--->',host_obj,task_content
    bind_host = host_obj
    s = paramiko.SSHClient()
    s.load_system_host_keys()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if bind_host.host_user.auth_type == 'ssh-password':
            s.connect(bind_host.host.ip_addr,#ip地址
                      int(bind_host.host.port),#端口
                      bind_host.host_user.username,#用户名
                      bind_host.host_user.password,#密码
                      timeout=5)#超时时间
        else:#rsa_key
            pass
            '''
            key = paramiko.RSAKey.from_private_key_file(settings.RSA_PRIVATE_KEY_FILE)
            s.connect(bind_host.host.ip_addr,
                      int(bind_host.host.port),
                      bind_host.host_user.username,
                      pkey=key,
                      timeout=5)
            '''
        stdin,stdout,stderr = s.exec_command(task_content)#task_content = cmd
        result = stdout.read(),stderr.read()#2个值，要么正确，要么错误
        #if any(result):
        cmd_result = filter(lambda x:len(x.strip())>0,result)[0]
        #else:
        #    cmd_result = 'execution has no output!'
        result = 'success'
        #print '----------- HOST:%s  IP:%s -------------' %(bind_host.host.hostname,bind_host.host.ip_addr)

        #for line in cmd_result:
        #    print line,

        #s.close()
    except Exception,e:
        #print '----------- HOST:%s  IP:%s -------------' %(bind_host.host.hostname,bind_host.host.ip_addr)
        print '\033[31;1m%s\033[0m' % e
        cmd_result = e
        result = 'failed'
    for line in cmd_result:
        print line,

    #保存到数据库中
    log_obj = models.TaskLogDetail.objects.get(child_of_task_id = task_id,bind_host_id = bind_host.id)
    log_obj.event_log = cmd_result
    log_obj.date = timezone.now()
    log_obj.result = result

    log_obj.save()




    #log_obj = models.TaskLogDetail.objects.get(child_of_task_id= int(task_id), bind_host_id=bind_host.id)
    #log_obj.event_log = cmd_result
    #log_obj.result= res_status
    #log_obj.save()


    #python multi_task.py -task_id 2 -run_type by_paramiko
