#_*_coding:utf-8_*_

from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import models,task,json,utils
# Create your views here.

@login_required
def index(request):
    return render(request,'index.html')

@login_required
def hosts_index(request):
    return render(request,'hosts/dashboard.html')

@login_required
def assets_index(request):
    return render(request,'assets/dashboard.html')

@login_required
def monitor_index(request):
    return render(request,'monitor/dashboard.html')
@login_required
def acc_logout(request):
    logout(request)

    return  HttpResponseRedirect("/")


def acc_login(requeset):
    login_err = ''
    if requeset.method == 'POST':
        username = requeset.POST.get('email')
        password = requeset.POST.get('password')

        user = authenticate(username=username,password=password)
        if user is not None:
            login(requeset,user)

            return HttpResponseRedirect('/')

        else:
            login_err = "Wrong username or password!"
    return  render(requeset,'login.html', {'login_err':login_err})


@login_required
def host_mgr(request):
    selected_gid = request.GET.get('selected_gid')#从host_mgr.html中获取selected_gid，
    if selected_gid:    #根据selected_gid到BindHostToUser里过滤用户组
        host_list = models.BindHostToUser.objects.filter(host_groups__id =selected_gid)
    else:   #如果selected_gid不存在，到bind_hosts里选取没绑定用户组的用户
        host_list = request.user.bind_hosts.select_related()
    return render(request,"hosts/host_mgr.html",{'host_list':host_list})

@login_required
def multi_cmd(request):
    return render(request,"hosts/multi_cmd.html")

@login_required
def multi_file_transfer(request):
    return render(request,"hosts/multi_file_transfer.html")


@login_required
def submit_task(request):
    print request.POST

    tas_obj = task.Task(request)#调用task.py的方法
    res = tas_obj.handle()
    return HttpResponse(json.dumps(res)) #字典需要用json下解读，res传过来是字典

@login_required
def get_task_result(request):
    task_obj = task.Task(request)
    res = task_obj.get_task_result()
    print '--res--task--',res
    return HttpResponse(json.dumps(res,default=utils.json_date_handler))
    #json.dump(res,default)表示把res的内容按后面函数的方式处理后返回，因为json处理不了时间格式，所以单独写函数

@csrf_exempt #csrf豁免
@login_required
def file_upload(request):
    filename = request.FILES['filename']
    print '-->',request.POST
    file_path = utils.handle_upload_file(request,filename)

    return HttpResponse(json.dumps({'uploaded_file_path':file_path}))