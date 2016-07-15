#_*_coding:utf-8_*_
from django.contrib import admin

import auth_admin
# Register your models here.
import models
#在models.py写的表注册到admin里，使网页后台可以管理数据库
class HostAdmin(admin.ModelAdmin):#使注册的表在页面可以显示详细的信息
    list_editable = ('hostname','ip_addr')#可以编辑
    list_display = ('hostname','ip_addr','port','idc','system_type','enabled')#显示的内容
    search_fields = ('hostname','ip_addr')#可以搜索的内容
    list_filter = ('idc','system_type')#可以过滤的内容
class HostUserAdmin(admin.ModelAdmin):
    list_display = ('auth_type','username','password')

class BindHostToUserAdmin(admin.ModelAdmin):
    list_display = ('host','host_user','get_groups')#'get_groups'是自己定义的，在models中
    filter_horizontal = ('host_groups',)#在选择内容时，水平方向有一个信息框
admin.site.register(models.UserProfile,auth_admin.UserProfileAdmin)
admin.site.register(models.Host,HostAdmin)
admin.site.register(models.HostGroup)
admin.site.register(models.HostUser,HostUserAdmin)
admin.site.register(models.BindHostToUser,BindHostToUserAdmin)
admin.site.register(models.IDC)
admin.site.register(models.TaskLog)
admin.site.register(models.TaskLogDetail)