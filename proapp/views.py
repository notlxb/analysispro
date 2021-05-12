from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import *
from mongoengine import DoesNotExist

from proapp.models import Course
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import json
from django.conf import settings
from .models import Course, Grade, Examappro
import xlrd
import docx
from win32com import client
import pythoncom
import pandas as pd
import time, re
import os


@csrf_exempt
def login(request):
    response = {}
    if request.method == 'POST':
        respose_data = json.loads(request.body.decode('utf-8'))
        try:
            username = respose_data.get('username')
            password = respose_data.get('userpwd')
            if username == 'admin' and password == '123':
                response['msg'] = 'success'
                response['error_num'] = 0
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
    return JsonResponse(response)
    # Book.objects.filter(name='lil').first().delete()
    # return HttpResponse('Hello,word')


@csrf_exempt
def getcourselist(request):
    response = {}
    if request.method == 'GET':
        qs = Course.objects.all()
        response['list'] = [
            {"course_year": cou.course_year, "course_term": cou.course_term, "course_name": cou.course_name,
             "course_id": cou.course_id,
             "course_teacher": cou.course_teacher} for cou in qs]
        return JsonResponse(response)


@csrf_exempt
def add_course(request):
    response = {}
    if request.method == 'POST':
        respose_data = json.loads(request.body.decode('utf-8'))
        year_term = respose_data.get("course_year").split('-')
        year = year_term[0] + "-" + year_term[1]
        course_add = Course(course_year=year, course_term=year_term[2], course_id=respose_data.get("course_id"),
                            course_name=respose_data.get("course_name"),
                            course_teacher=respose_data.get("course_teacher"),
                            stu_grade="").save()
        response['error_num'] = 0
    return JsonResponse(response)


# ****************************上传试卷审批表获得课程目标的题型分布以及对应分值****************************
@csrf_exempt
def upload_exam_appro(request):
    response = {}
    if request.method == 'POST':
        file = request.FILES.get('file')
        cou_id = request.POST.get('course_id')
        file_name = cou_id + "" + file.name
        url = settings.MEDIA_ROOT + '/exam_approval/' + file_name
        with open(url, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        document = docx.Document(url)
        numTables = document.tables
        table_temp = []
        null_text = str(time.time())
        for row in numTables[0].rows:
            row_temp = []
            for cell in row.cells:
                if cell.text != null_text:
                    row_temp.append(cell.text)
                    cell.text = null_text
            table_temp.append(row_temp)
        question_type = []
        for i in range(1, len(table_temp[4])):
            question_type.append(table_temp[4][i].replace(" ", ""))
        tt = table_temp[5]
        type_all = []
        for i in range(len(tt)):
            array = []
            temp = tt[i].split("\n")
            for j in range(len(temp)):
                match = re.compile(r'[（](.*?)[）]', re.S)
                percent = "".join(re.findall(match, temp[j])).replace(" ", "")
                choice = re.sub("[A-Za-z0-9\%\(\)\（\）\、\[\]\,\。]", "", temp[j]).replace(" ", "")
                if percent != "" and choice != "":
                    result = choice + "," + percent
                array.append(result)
            type_all.append({question_type[i]: array})
        table_temp = []
        for row in numTables[1].rows:
            row_temp = []
            for cell in row.cells:
                if cell.text != null_text:
                    row_temp.append(cell.text)
                    cell.text = null_text
            table_temp.append(row_temp)
        start_end = []
        course_pop = []
        for i in range(len(table_temp)):
            if table_temp[i][0] == "课程目标":
                continue
            elif "课程目标" in table_temp[i][0]:
                start_end.append(i)
                course_pop_item = table_temp[i][0].replace(".", "+")
                course_pop.append({course_pop_item: table_temp[i][1]})
            elif table_temp[i][0] == "命题教师对试卷的自查情况":
                start_end.append(i)
                break
        for i in range(len(start_end) - 1):
            temp_A = []
            temp_B = []
            for j in range(start_end[i] + 1, start_end[i + 1] - 1):
                print(table_temp[j])
                temp_A.append(
                    {"title_num_1": table_temp[j][0], "title_num_2": table_temp[j][1],
                     "score_sin": table_temp[j][2]})
                temp_B.append(
                    {"title_num_1": table_temp[j][3], "title_num_2": table_temp[j][4],
                     "score_sin": table_temp[j][5]})
            temp = course_pop[i]
            temp["试卷类型A"] = temp_A
            temp["试卷类型B"] = temp_B
            course_pop[i] = temp
        Examappro(course_id=cou_id, question_type=type_all, question_distr=course_pop).save()
        response['code'] = 200
        response['msg'] = 'success'
        return JsonResponse(response)


# *****************************************************************************************

# ************************************上传试卷A，B和平时成绩************************************
@csrf_exempt
def upload_exam_grade(request):
    response = {}
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course_id')
            examappro = Examappro.objects.get(course_id=course_id)  # 判断试卷审批表是否上
        except DoesNotExist:
            response['code'] = 202
            response['msg'] = 'fail'
            return JsonResponse(response)
        else:
            # ########################################################################
            file_type = request.POST.get('file_type')  # file_type = 试卷A/试卷B/平时分
            file = request.FILES.get('file')
            file_name = course_id + file_type + "." + file.name.split(".")[1]
            url_dir = settings.MEDIA_ROOT + '/exam_grade/' + course_id + '/'
            if not os.path.exists(url_dir):
                os.mkdir(url_dir)
            url_dir_file = url_dir + file_name
            with open(url_dir_file, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            # ##########################################################################
            data = xlrd.open_workbook(url_dir_file, formatting_info=True)
            table = data.sheets()[0]
            nrows = table.nrows
            ncol = table.ncols
            if 'A' in file_type or 'B' in file_type:
                grade_data = []
                for i in range(1, nrows):
                    if i % 2 == 1:
                        temp = {}
                        question_index = table.row_values(i)[0]
                        temp1 = [str(x).split(".")[0] for x in table.row_values(i) if x != ""]
                        temp2 = [str(x) for x in table.row_values(i + 1) if x != ""]
                        del temp1[0]
                        for j in range(len(temp1)):
                            temp[temp1[j]] = temp2[j]
                        grade_data.append({question_index: temp})
                if 'A' in file_type:
                    examappro.grade_data_A = grade_data
                    examappro.save()
                else:
                    examappro.grade_data_B = grade_data
                    examappro.save()
                # ##########################################################################
                examappro = Examappro.objects.get(course_id=course_id)
                question_distr = examappro.question_distr
                if 'A' in file_type:
                    grade_data_kind = examappro.grade_data_A
                else:
                    grade_data_kind = examappro.grade_data_B
                all_score = []
                dis_score = []
                for i in range(len(question_distr)):
                    sum_score_1 = 0
                    dis_score_1 = 0
                    exam_type = question_distr[i][file_type]
                    for j in range(len(exam_type)):
                        title_num_2 = exam_type[j]["title_num_2"]
                        title = "题型" + exam_type[j]["title_num_1"][0]

                        if "," in title_num_2:
                            title_num_2 = title_num_2.split(",")
                        elif "，" in title_num_2:
                            title_num_2 = title_num_2.split("，")
                        else:
                            title_num_2 = title_num_2.split()
                        new_title_num_2 = []
                        if len(title_num_2) != 0:
                            for k in range(len(title_num_2)):
                                if "-" in title_num_2[k]:
                                    temp = title_num_2[k].split("-")
                                    for m in range(int(temp[0]), int(temp[1]) + 1):
                                        new_title_num_2.append(str(m))
                                elif title_num_2[k] != "":
                                    new_title_num_2.append(title_num_2[k])
                            new_title_num_2 = [x for x in new_title_num_2 if "-" not in x]
                            for x in new_title_num_2:
                                dis_score_1 += float(grade_data_kind[j][title][x])
                            sum_score_1 += int(float(exam_type[j]["score_sin"]))
                        else:
                            sum_score_1 += int(float(exam_type[j]["score_sin"]))
                    dis_score.append("%.2f" % dis_score_1)
                    all_score.append(sum_score_1)
                datasets = []
                for i in range(len(all_score)):
                    temp = float(dis_score[i]) / float(all_score[i])
                    datasets.append("%.2f" % temp)
                g_model = examappro.grade_model
                cheak_exist = 0
                for i in range(len(g_model)):
                    if g_model[i]["name"] == file_type:
                        g_model[i]["data"] = [x for x in datasets]
                        cheak_exist = 1
                if cheak_exist == 0:
                    g_model.append({"name": file_type, "type": 'bar', "data": [x for x in datasets]})
                examappro.grade_model = g_model
                examappro.save()
            # ##########################################################################
            else:
                full_grade = [0 for i in range(0, ncol - 3)]
                real_grade = [0 for j in range(0, ncol - 3)]
                course_pop = [x.replace(".", "+") for x in table.row_values(2) if x != ""]
                for i in range(3, nrows):
                    for j in range(3, ncol):
                        full_grade[j - 3] += table.row_values(i)[j] * table.row_values(i)[1]
                        real_grade[j - 3] += table.row_values(i)[j] * table.row_values(i)[2]
                average_data = []
                percent_data = []
                for j in range(len(course_pop)):
                    arr = ["%.2f" % (real_grade[j] / full_grade[j]), full_grade[j], real_grade[j]]
                    average_data.append({course_pop[j]: arr})
                    percent_data.append("%.2f" % (real_grade[j] / full_grade[j]))
                examappro.grade_data_average = average_data
                grade_model = examappro.grade_model
                cheak_exist = 0
                for i in range(len(grade_model)):
                    if grade_model[i]["name"] == "平时成绩":
                        grade_model[i]["data"] = [x for x in percent_data]
                        cheak_exist = 1
                if cheak_exist == 0:
                    grade_model.append({"name": '平时成绩', "type": 'bar', "data": [x for x in percent_data]})
                examappro.grade_model = grade_model
                examappro.save()
            # ##########################################################################
            response['code'] = 200
            response['msg'] = 'success'
            return JsonResponse(response)
    # cou_id = request.POST.get('course_id')
    # file_name = cou_id + "" + file.name
    # course = Course.objects.get(course_id=cou_id)
    # course.stu_grade = file_name
    # course.save()
    # data = xlrd.open_workbook(url, formatting_info=True)
    # table = data.sheets()[0]
    # nrows = table.nrows
    # all_data = []
    # for i in range(1, nrows):
    #     if i % 2 == 1:
    #         tt = {}
    #         temp1 = [str(x) for x in table.row_values(i) if x != ""]
    #         temp2 = [str(x) for x in table.row_values(i + 1) if x != ""]
    #         title = temp1[0]
    #         del temp1[0]
    #         for i in range(len(temp1)):
    #             tt[temp1[i]] = temp2[i]
    #         all_data.append({title: tt})
    # examappro = Examappro.objects.get(course_id=cou_id)
    # examappro.grade_data_A = all_data
    # examappro.save()


@csrf_exempt
def get_exam_grade(request):
    response = {}
    if request.method == 'GET':
        course_id = request.GET.get('course_id')
        examappro = Examappro.objects.get(course_id=course_id)
        question_distr = examappro.question_distr
        grade_data_A = examappro.grade_data_A
        all_score = []
        dis_score = []
        course_pop = []
        for i in range(len(question_distr)):
            sum_score_1 = 0
            dis_score_1 = 0
            exam_type_A = question_distr[i]["试卷类型A"]
            for j in range(len(exam_type_A)):
                title_num_2 = exam_type_A[j]["title_num_2"]
                title = "题型" + exam_type_A[j]["title_num_1"][0]
                title_num_2 = title_num_2.split("，")
                new_title_num_2 = []
                for k in range(len(title_num_2)):
                    if "-" in title_num_2[k]:
                        temp = title_num_2[k].split("-")
                        for i in range(int(temp[0]), int(temp[1]) + 1):
                            new_title_num_2.append(str(i))
                    elif title_num_2[k] != "":
                        new_title_num_2.append(title_num_2[k])
                new_title_num_2 = [x + ".0" for x in new_title_num_2 if "-" not in x]
                for x in new_title_num_2:
                    dis_score_1 += float(grade_data_A[j][title][x])
                sum_score_1 += int(float(exam_type_A[j]["score_sin"]))
            dis_score.append("%.2f" % dis_score_1)
            all_score.append(sum_score_1)

        for i in range(len(question_distr)):
            els = list(question_distr[i].items())
            course_pop.append(els[0][0].replace("+", "."))
        datasets = []
        for i in range(len(all_score)):
            temp = float(dis_score[i]) / float(all_score[i])
            datasets.append("%.2f" % temp)

        response['labels'] = course_pop
        response['datasets'] = datasets
        response["course_name"] = Course.objects.get(course_id=course_id).course_name
        return JsonResponse(response)


@csrf_exempt
def upload_grade(request):
    response = {}
    if request.method == 'POST':
        file = request.FILES.get('file')
        cou_id = request.POST.get('course_id')
        file_name = cou_id + "" + file.name
        course = Course.objects.get(course_id=cou_id)
        course.stu_grade = file_name
        course.save()
        url = settings.MEDIA_ROOT + '/stu_grade/' + file_name
        with open(url, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # 处理excel表格
        data = xlrd.open_workbook(url, formatting_info=True)
        table = data.sheets()[0]
        cell_data = []
        cell_data_index = table.merged_cells
        for merged in table.merged_cells:
            for i in range(merged[0], merged[1]):
                for j in range(merged[2], merged[3]):
                    cell_data.append(table.cell_value(i, j))
                    cell_data = [x for x in cell_data if x != '']

        df = pd.read_excel(url)
        df2 = df.copy()
        inx = 0
        for temp in cell_data_index:
            index = [i for i in range(temp[2], temp[3])]
            name = cell_data[inx] + "" + "平均分"
            df[name] = (df.iloc[:, [x for x in index]].sum(axis=1)) / len(index)
            df.iloc[:, [x for x in index]] = df.iloc[:, [x for x in index]].astype('str')
            df[cell_data[inx]] = [','.join(i) for i in df.iloc[:, [x for x in index]].values]
            inx += 1
        df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        df2.drop(df2.columns[df2.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        # 获取处理之后的列名(维度和度量值)
        columns_name = [column for column in df2 if column != "学生姓名" and column != "学生学号"]
        df_1 = json.loads(df.T.to_json()).values()
        Grade(course_id=cou_id, dim_mea=columns_name, dataframe=df_1).save()
        response['code'] = 200
        response['msg'] = 'success'
        return JsonResponse(response)
    response['code'] = 202
    response['msg'] = 'fail'
    return JsonResponse(response)


@csrf_exempt
def grade_stu(request):
    response = {}
    if request.method == 'GET':
        course_id = request.GET.get('course_id')
        course_name = Course.objects.get(course_id=course_id).course_name
        dim = [x for x in request.GET.get('dim').split(' ') if x != '']
        mea = [x for x in request.GET.get('mea').split(' ') if x != '']
        df = pd.DataFrame(Grade.objects.get(course_id=course_id).dataframe)
        df.transpose()
        mea2 = []
        for x in mea:
            if x != '期末成绩':
                temp = x + '' + "平均分"
                mea2.append(temp)
            else:
                mea2.append(x)
        agg_function = {}
        for x in mea2:
            agg_function[x] = 'mean'
        grouped1 = df.groupby(dim[0]).agg(agg_function)
        grouped1 = grouped1.applymap(lambda x: '%.2f' % x)
        labels = [x + "班级" for x in grouped1.index.tolist()]
        datasets = []
        for x in mea2:
            datasets.append({"label": x, "data": grouped1[x].tolist()})
        response['labels'] = labels
        response['datasets'] = datasets
        response["course_name"] = course_name
        return JsonResponse(response)


@csrf_exempt
def grade_get_dim(request):
    response = {}
    if request.method == 'GET':
        course_id = request.GET.get('course_id')
        dim_mea = Grade.objects.get(course_id=course_id).dim_mea

        response['list'] = dim_mea
        return JsonResponse(response)


@csrf_exempt
def upload(request):
    response = {}
    if request.method == 'POST':
        file = request.FILES.get('file', '')
        file_addr = '%s/%s' % (settings.MEDIA_ROOT, file.name)
        with open(file_addr, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        response['code'] = 200
        response['msg'] = '上传成功'
        return JsonResponse(response)
    response['code'] = 202
    response['msg'] = 'fail'
    return JsonResponse(response)
