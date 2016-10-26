import datetime
import pyodbc
import sys
import socket
import socketserver
import _thread
import time
import re
import hashlib
import urllib.request
import urllib.parse
import os
import json

# 可配置项目

# 查询开始时间
STUDYDONEDATE = datetime.datetime.now()

# 修改内容：
# 保存log
# 参数保存

# 用json文件保存配置项
def writeJson(studydonedate):
    data = {
        'STUDYDONEDATE': studydonedate,
    }
    json_str = json.dumps(data)
    # Writing JSON data
    with open('getreport_lszxyy_conf.json', 'w') as f:
        json.dump(json_str, f)


# 读json文件的配置项
def readJson():
    # Reading data back
    with open('getreport_lszxyy_conf.json', 'r') as f:
        data = json.load(f)
    datadic = eval(data)
    if 'studydonedate' in datadic.keys:
        return  datadic['studydonedate']
    else:
        return -1


# 查询数据库
def selSql(selStr):
    sqlresult = []
    connectStr = 'DRIVER={SQL Server};SERVER=192.168.1.155;PORT=1433;DATABASE=eRadWorks;UID=epacs;PWD=epacs'
    cnxn = pyodbc.connect(connectStr)
    cursor = cnxn.cursor()
    try:
        cursor.execute(selStr)
    except Exception as e:
        print(e)
    sum = 0
    while 1:
        row = cursor.fetchone()
        sum = sum + 1
        if not row:
            break
        sqlresult.append(list(row))
        print(row)
    # print(sum)
    cnxn.close
    return sqlresult

# 计算年龄
def calculate_age(born,today):
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        # raised when birth date is February 29
        # and the current year is not a leap year
        birthday = born.replace(year=today.year, day=born.day - 1)
    age = ''
    if birthday > today:
        age = str(today.year - born.year - 1)
    else:
        age = str(today.year - born.year)
    # if age == '0':   #小于1岁,按月
    #     age = str(today.month -born.month)+'M'
    # if age == '0M':
    #     age = str(today.day-born.day)+'D'
    return age

'''
获取报告
'''
def getreport():
    global STUDYDONEDATE
    preDate = STUDYDONEDATE.strftime('%Y%m%d')
    preTime = STUDYDONEDATE.strftime('%H%M%S')
    nowTime = datetime.datetime.now().strftime('%H%M%S')
    # 更新时间
    STUDYDONEDATE = datetime.datetime.now()
    # 保存更新时间
    writeJson(STUDYDONEDATE)

    # 没有处理24小时时间转换时的情况
    selstr  = 'select STUDIESINSTUID,STUDIESMODALITIES,PATIENTSALIAS,ACCESSIONNUMBER,STUDIESDONEDATE,STUDIESDONETIME,RESULTSEXAMINEALIAS,REPORTSDOCTORALIAS,REPORTSEVIDENCES,REPORTSCONCLUSION,APPROVEDATE,APPROVETIME,ApproveDoctorAlias,PATIENTSSEX,PATIENTSDOB,PATIENTSID,REPORTSDATE,REPORTSTIME  from VHIS_JDYX WHERE  REPORTSSTATUS = 100 and APPROVEDATE = \'%s\' and APPROVETIME >=  \'%s\' and APPROVETIME< \'%s\' order by StudiesDoneTime' % (preDate, preTime, nowTime)
    reportlistsql = selSql(selstr)
    reports = []
    for temp in reportlistsql:
        report = {}
        m1 = hashlib.md5()
        m1.update(temp[0].encode('utf_8'))
        report = {'appKey': '', 'uuid': '', 'patientPhone': '', 'modality': '', 'hospitalName': '', 'pacsCode': '',
                     'patientName': '', 'patientSex': '', 'patientAge': 0, 'typeName': '', 'clinicId': '',
                     'applyDoctorName': '', 'officeName': '', 'patientId': '', 'studyDate': '', 'reportBody': '',
                     'reportDoctorName': '', 'imageShow': '', 'diagnosis': '', 'reportDate': '', 'auditDoctorName': '',}
        report['uuid'] = m1.hexdigest() # md5 加密
        if temp[1]:
            if len(temp[1]) > 2:
                report['modality'] = temp[1][1:-1]
            else:
                report['modality'] = temp[1]
        report['patientName'] = temp[2]
        # report['ACCESSIONNUMBER'] = temp[3]
        report['studyDate'] = datetime.datetime.strptime(temp[4] + temp[5], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        report['reportBody'] = temp[6]
        report['reportDoctorName'] = temp[7]
        report['imageShow'] = temp[8]
        report['diagnosis'] = temp[9]
        if len(temp[16]) >0 and len(temp[17]):
            report['reportDate'] = datetime.datetime.strptime(temp[16] + temp[17], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        else:
            report['reportDate'] = ' '

        report['auditDoctorName'] = temp[12]
        if temp[13]:
            report['patientSex'] = temp[13].replace('F', '女').replace('M', '男')
        else:
            report['patientSex'] = '/'
        if len(temp[14]) > 0 and len(report['reportDate']) > 4:
            report['patientAge'] = calculate_age(datetime.datetime.strptime(temp[14], '%Y%m%d'),datetime.datetime.strptime(report['reportDate'], '%Y-%m-%d %H:%M:%S'))
        else:
            report['patientAge'] = '/'
        report['patientId'] = temp[3]
        report['clinicId'] = '/'
        report['typeName'] = '/'
        report['officeName'] = '/'
        report['patientPhone'] = '/'
        report['hospitalName'] = '丽水市中心医院'
        report['pacsCode'] = 'LSZXYY'
        report['applyDoctorName'] = '/'
        if len(temp[10]) > 0 and len(temp[11]) > 0:
            report['auditDate']  = datetime.datetime.strptime(temp[10] + temp[11], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        reports.append(report)
    return reports

# 提交报告
def submitreport(reports):
    # 接口地址
    url = 'http://10.10.10.2:91/api/report/upload'
    for report in reports:
        reportdata = urllib.parse.urlencode(report)
        print(report)
        reportdata = reportdata.encode('utf-8')
        with urllib.request.urlopen(url, reportdata) as f:
            tmp = (f.read().decode('utf-8')).replace('true', 'True').replace('false', 'False')
            postResult = eval(tmp)  # {"flag":true}{"msg":"有参数未传","flag":false}
            print(postResult)
            # 更新本地数据库
            # if 'flag' in postResult.keys():
            #     if True == postResult['flag']:
            #         print(postResult['flag'])
            #         # 记录状态到数据库
            #         sqlstr = (
            #             "UPDATE vhis_jdyx SET SENDREPORT = %s  "
            #             "WHERE AccessionNumber = %s  ")
            #         values = ( 1, reportdic['patientId'])
            #         updatemysql(sqlstr, values)
            #     else:  # 发送报告失败，保存到数据库
            #         pass
            # print(f.read().decode('utf-8'))

if __name__ == '__main__':
    # 如果配置项为空时，使用当前时间
    resultstr = readJson()
    if resultstr != -1:
        STUDYDONEDATE = resultstr
    while True:
        submitreport(getreport())
        time.sleep(60*2)  # 2分钟更新一次