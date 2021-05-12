from django.db import models
from mongoengine import *
import mongoengine
import datetime


# Create your models here.

class Course(Document):
    course_year = mongoengine.StringField(max_length=16)
    course_term = mongoengine.StringField(max_length=16)
    course_id = mongoengine.StringField(max_length=16, primary_key=True)
    course_name = mongoengine.StringField(max_length=16)
    course_teacher = mongoengine.StringField(max_length=16)
    stu_grade = mongoengine.StringField(max_length=30)


class Grade(Document):
    course_id = mongoengine.StringField(max_length=20, primary_key=True)
    dim_mea = mongoengine.ListField()
    dataframe = mongoengine.ListField()


class Examappro(Document):
    course_id = mongoengine.StringField(max_length=20, primary_key=True)  # 课程编号
    question_type = mongoengine.ListField()  # 试卷类型及分值分布
    question_distr = mongoengine.ListField()  # 不同试卷课程目标对应的题号及题型
    grade_data_A = mongoengine.ListField()  # 试卷A的分数分布
    grade_data_B = mongoengine.ListField()  # 试卷B的分数分布
    grade_data_average = mongoengine.ListField()  # 平时成绩的分布
    grade_model = mongoengine.ListField()  # 存储不同维度的度量值
   