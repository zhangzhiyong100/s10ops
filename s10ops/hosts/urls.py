
from django.conf.urls import include, url
import views

urlpatterns = [
    url("^$", views.hosts_index, name="hosts"),
    url("^host_mgr/$", views.host_mgr, name="host_mgr"),
    url("^multi_file_transfer/$", views.multi_file_transfer, name="multi_file_transfer"),
    url("^multi_cmd/$", views.multi_cmd, name="multi_cmd"),
    url("^submit_task/$", views.submit_task, name="submit_task"),
    url("^get_task_result/$", views.get_task_result, name="get_task_result"),
    url("^file_upload/$", views.file_upload, name="file_upload"),

]
