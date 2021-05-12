#!/usr/bin/python
# author lxb
from django.urls import path, re_path
from proapp import views

urlpatterns = [
    # re_path('add_book$', views.add_book),
    # re_path('show_books/', views.show_books),
    re_path('login/', views.login),
    re_path('getcourselist/', views.getcourselist),
    re_path('ewfer', views.upload),
    re_path('add_course', views.add_course),
    re_path('upload/grade$', views.upload_grade),
    re_path('grade/stu', views.grade_stu),  # 根据选择的维度返回对应的数据
    re_path('grade/getdim', views.grade_get_dim),  # 返回前端可选择的维度和度量
    re_path('upload/exam_appro', views.upload_exam_appro),  # 上传试卷审批表
    re_path('upload/exam_grade', views.upload_exam_grade),
    re_path('get/exam_grade', views.get_exam_grade)
]
