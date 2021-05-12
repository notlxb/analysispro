# #!/usr/bin/python
# # author lxb
import pandas  as pd
# import numpy as np
import xlrd
# import json
#
# #
# file_path = "./stu_grade/BSDAD9087123学生成绩.xls"
# data = xlrd.open_workbook(file_path, formatting_info=True)
# table = data.sheets()[0]
# cell_data = []
# cell_data_index = table.merged_cells
# for merged in table.merged_cells:
#     for i in range(merged[0], merged[1]):
#         for j in range(merged[2], merged[3]):
#             cell_data.append(table.cell_value(i, j))
#             cell_data = [x for x in cell_data if x != '']
#
# df = pd.read_excel(file_path)
# inx = 0
# for temp in cell_data_index:
#     index = [i for i in range(temp[2], temp[3])]
#     df.iloc[:, [x for x in index]] = df.iloc[:, [x for x in index]].astype('str')
#     df[cell_data[inx]] = [','.join(i) for i in df.iloc[:, [x for x in index]].values]
#     inx += 1
# df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
#
# print(json.loads(df.T.to_json()).values())
import cubes

# file_path = './平时分.xls'
# data = xlrd.open_workbook(file_path, formatting_info=True)
# table = data.sheets()[0]
# nrow = table.nrows
# ncol = table.ncols
# full_grade = [0 for i in range(0, ncol - 3)]
# real_grade = [0 for j in range(0, ncol - 3)]
# course_pop = [x.replace(".", "+") for x in table.row_values(2) if x != ""]
# print(course_pop)
# for i in range(3, nrow):
#     for j in range(3, ncol):
#         full_grade[j - 3] += table.row_values(i)[j] * table.row_values(i)[1]
#         real_grade[j - 3] += table.row_values(i)[j] * table.row_values(i)[2]
# average_data = []
# for j in range(len(course_pop)):
#     arr = [full_grade[j], real_grade[j], "%.2f" % (real_grade[j] / full_grade[j])]
#     average_data.append({course_pop[j]: arr})
#
# print(average_data)
# data = [{"name": '平时成绩', "type": 'bar'}, {"name": '试卷A', "type": 'bar'}]
# for i in range(len(data)):
#     if data[i]["name"] == "sadsa":
#         data[i]["type"] = "dasdsa"
# print(data)
ss = ['1-3']
for i in range(len(ss)):
    print("sss")
