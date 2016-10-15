#coding=utf-8
import hashlib
import urllib.parse
import urllib.request

import cx_Oracle
import mysql.connector
import mysql.connector
import datetime
import time
import os


# 提交报告
def submitreport():
    # 接口地址
    url = 'http://app.jdimage.cn/api/report/upload'

    # md5加密
    studyuid = ''
    m1 = hashlib.md5()
    m1.update(studyuid.encode('utf_8'))
    studyuid = m1.hexdigest()
    # 报告内容
    # reportdic = {'appKey': '', 'uuid': '', 'patientPhone': '', 'modality': '', 'hospitalName': '', 'pacsCode': '',
    #              'patientName': '', 'patientSex': '', 'patientAge': 50, 'typeName': '', 'clinicId': '',
    #              'applyDoctorName': '', 'officeName': '骨科', 'patientId': '', 'studyDate': '', 'reportBody': '',
    #              'reportDoctorName': '', 'imageShow': '', 'diagnosis': '', 'reportDate': '', 'auditDoctorName': '',}
    # reportdic['uuid'] = studyuid
    # reportdic['modality'] = 'CT'
    # reportdic['clinicId'] = '123456'
    # reportdic['typeName'] = '住院'
    # reportdic[
    #     'imageShow'] = '颈椎CTI检查，序列 SE T1WI, FSE T2WI ,FIR STIR ,矢状位、横断位扫描：颈椎CTI检查，序列 FSE T1WI ，FRFSE T2WI ，矢状位、横断位扫描示：颈椎生理曲度存在，各椎体序列整齐，形态及信号无殊。诸颈椎间盘未见异常改变。椎管无狭窄。硬膜囊及颈髓无殊。椎旁软组织无异。'
    # reportdic['diagnosis'] = '颈椎CTI检查未见异常。'
    # reportdic['studyDate'] = '2016-08-22 00:00:01'
    # reportdic['patientName'] = '叶**'
    # reportdic['patientSex'] = '男'
    # reportdic['patientPhone'] = '18072996469'
    # reportdic['patientId'] = 'CT14374'
    # reportdic['hospitalName'] = '影像云诊断中心'
    # reportdic['pacsCode'] = 'jdimage'
    # reportdic['reportDate'] = '2016-08-31 11:22:36'
    # reportdic['applyDoctorName'] = '张**'
    # reportdic['reportDoctorName'] = '吴会权'
    # reportdic['auditDoctorName'] = '孙泽刚'
    # reportdic['reportBody'] = '胸部正侧位'
    reportdic ={'patientSex': '女', 'officeName': '/', 'pacsCode': 'JDRMYY', 'auditDoctorName': None, 'modality': 'DR', 'patientName': '郑小囡', 'appKey': '', 'reportDoctorName': '张华', 'reportBody': '颈椎(侧位),腰椎正侧位,右肩关节正位,骨盆正位,右手正斜位,右腕正侧位,右尺桡骨正侧位,右肘正侧位,右肱骨正侧位,右足正斜位,右踝正侧位,右胫腓骨正侧位,右膝关节正侧位,胸部正位,右股骨正侧位（中下', 'diagnosis': '颈椎骨质退行性改变，必要时进一步检查。\r\n第4腰椎向前轻度滑移，腰椎退变。\r\n骨盆平片未见异常。\r\n两肺纹理增多，请结合临床。\r\n右侧肩关节脱位伴肱骨大结节撕脱性骨折。\r\n右肱骨中远段未见明显骨折。\r\n右尺桡骨中段骨折。\r\n右腕关节骨质未见明显异常；右手小指、拇指指间关节增生性改变。\r\n右股骨中上段未见明显骨折与异常；右膝关节骨质退行性改变。\r\n右腓骨中下段骨折，右胫骨远段撕脱性骨折可能，右踝关节脱位，建议进一步检查。', 'patientPhone': '/', 'uuid': 'ed09fbbf085cc02a1dfe34fd75a862a7', 'clinicId': '/', 'hospitalName': '建德市第一人民医院', 'imageShow': '   部分颈椎由于体外物重叠影显示欠清，所见颈椎生理曲度变直，部分颈椎体显示唇样骨质增生。各椎间隙未见明显狭窄，附件及小关节无殊。\r\n    第4腰椎向前轻度滑移，诸腰椎边缘唇样增生改变。其余未见明显异常。\r\n    骨盆所组成骨骨皮质连续，骨小梁排列整齐。所见关节未见异常，软组织影清晰。\r\n    两侧胸廓对称，两肺野纹理增多、增粗。两侧肺门结构正常。气管居中。纵隔无增宽。两侧横膈位置形态正常。心脏形态大小正常。两侧肋膈角锐利。所见肋骨未见明显错位骨折征象。\r\n    右肱骨大结节撕脱性骨质断裂，右侧肱骨头下关节盂下移位。右肩诸骨未见明显骨折征象。\r\n    右肱骨中远段骨皮质连续，未见明显骨折征象，所见肘关节间隙无殊。\r\n    右尺桡骨中段双骨折，断端成角错位，周围软组织肿胀。\r\n    右腕关节诸组成骨未见明显骨折征象，关节间隙未见明显异常，周围软组织显示清晰。\r\n    右手诸骨未见明显骨折线，右手小指、拇指指间关节边缘变尖。\r\n    右股骨中上段形态良好，皮质连续，未见明显骨折与异常。关节间隙如常。\r\n    右胫骨髁间隆棘隆起，髌骨上缘骨质变尖、增生，关节间隙未见狭窄，周围软组织未见异常。\r\n    右腓骨中下段骨折，断端移位，胫骨远段局部骨质不连，右踝关节变形。\r\n', 'patientId': 'X290562', 'patientAge': '64', 'applyDoctorName': '/', 'studyDate': '2015-01-06 09:04:31', 'reportDate': '2015-01-06 09:49:06', 'auditDate': '2015-01-06 09:49:07', 'typeName': '/'}

    reportdata = urllib.parse.urlencode(reportdic)
    reportdata = reportdata.encode('utf-8')
    with urllib.request.urlopen(url, reportdata) as f:
        postResult = eval(
            (f.read().decode('utf-8')).replace('true', 'True').replace('false',
                                                                       'False'))  # {"flag":true}{"msg":"有参数未传","flag":false}
        if 'flag' in postResult.keys():
            if True == postResult['flag']:
                print(postResult['flag'])
            else:  # 发送报告失败，保存到数据库
                print(postResult['flag'])
                print(postResult['msg'])
        print(f.read().decode('utf-8'))


# 查询数据库
def selSql(selStr):
    sqlresult = []
    # print(selStr)
    connection = cx_Oracle.Connection("radinfo/pacs.jd@192.9.216.21/radinfo")
    cursor = connection.cursor()
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
        sqlresult.append(row)
        print(row)
        # print(sum)
    connection.close()
    return sqlresult


def inserttomysql(startdate, enddate):
    selstr = 'select PATIENTSALIAS,PATIENTSID,PATIENTSSEX,PATIENTSDOB,STUDIESINSTUID,STUDIESDONEDATE,STUDIESDONETIME,ADMISSIONID,STUDIESMODALITIES,RESULTSBODIESALIAS,RESULTSEXAMINEALIAS,ACCESSIONNUMBER,REPORTSSTATUS,REPORTSDOCTORALIAS,REPORTSDATE,REPORTSTIME,RECORDSDOCTOR,RECORDSDOCTORALIAS,RECORDSDATE,RECORDSTIME,APPROVEDOCTOR,APPROVEDOCTORALIAS,APPROVEDATE,APPROVETIME,REPORTSCONCLUSION,REPORTSEVIDENCES,REPORTSTECHNOLOGIES,REPORTSCOMMENTS  from VHIS_JDYX WHERE   STUDIESDONEDATE>=\'%s\' and STUDIESDONEDATE< \'%s\' order by StudiesDoneTime' % (startdate, enddate)
    reportlistsql = selSql(selstr)
    print(reportlistsql[0])
    # cnx = mysql.connector.connect(user='root', password='',
    #                               host='127.0.0.1',
    #                               database='ypacs')
    # cursor = cnx.cursor()
    # add_employee = ("INSERT INTO VHIS_JDYX "
    #                 "(PATIENTSALIAS,PATIENTSID,PATIENTSSEX,PATIENTSDOB,STUDIESINSTUID,STUDIESDONEDATE,STUDIESDONETIME,ADMISSIONID,STUDIESMODALITIES,RESULTSBODIESALIAS,RESULTSEXAMINEALIAS,ACCESSIONNUMBER,REPORTSSTATUS,REPORTSDOCTORALIAS,REPORTSDATE,REPORTSTIME,RECORDSDOCTOR,RECORDSDOCTORALIAS,RECORDSDATE,RECORDSTIME,APPROVEDOCTOR,APPROVEDOCTORALIAS,APPROVEDATE,APPROVETIME,REPORTSCONCLUSION,REPORTSEVIDENCES,REPORTSTECHNOLOGIES,REPORTSCOMMENTS) "
    #                 "VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s) ")
    #
    # # insert_new_salary = ("INSERT INTO VHIS_JDYX (PATIENTSALIAS) " "VALUES (%s)")
    # # print(insert_new_salary)
    # temp = ('we',)
    # # Insert new employee
    # # cursor.execute(insert_new_salary, temp)
    # for report in reportlistsql:
    #     cursor.execute(add_employee, report)
    # # Make sure data is committed to the database
    #     cnx.commit()
    # cursor.close()
    # cnx.close()

def updatemysql(sqlstr, values):
    # update_old_salary = (
    #     "UPDATE salaries SET to_date = %s "
    #     "WHERE emp_no = %s AND from_date = %s")
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='ypacs')
    cursor = cnx.cursor()
    cursor.execute(sqlstr, values)
    # Make sure data is committed to the database
    cnx.commit()
    cursor.close()
    cnx.close()



#
# def selsqlfrommysql():
#     # 查询数据库
#     try:
#         cnx = mysql.connector.connect(user='root', password='',
#                                       host='127.0.0.1',
#                                       database='ypacs')
#         cursor = cnx.cursor()
#         query = ("SELECT * FROM VHIS_JDYX ")
#         cursor.execute(query)
#         for enddate in cursor:
#             print(enddate)
#
#         cursor.close()
#         cnx.close()
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#     else:
#         cnx.close()


if __name__ == "__main__":
    os.environ['nls_lang'] = 'AMERICAN_AMERICA.AL32UTF8' #解决CX_ORACLE查询出错的编码问题,
    submitreport()

    # selsqlfrommysql()
    # a = none
    # print(type(a))
    # currentdate = datetime.datetime.strptime('20160401', '%Y%m%d')    #发送开始时间
    # enddate = datetime.datetime.strptime('20160901', '%Y%m%d')  #结束时间
    # nextdate = currentdate + datetime.timedelta(days=1)
    #
    # while 1:
    #     # time.sleep(1)
    #     if currentdate < enddate:
    #         inserttomysql(currentdate.strftime('%Y%m%d'), nextdate.strftime('%Y%m%d'))
    #         currentdate = nextdate
    #         nextdate = currentdate + datetime.timedelta(days=1)
    #         print(currentdate)
    # sqlstr = (
    #     "UPDATE vhis_jdyx SET SENDIMAGES = %s "
    #     "WHERE AccessionNumber = %s ")
    # values = (1, 'CT163734')
    # updatemysql(sqlstr, values)

    selstr =' SELECT * FROM VHIS_JDYX  where ACCESSIONNUMBER =\'CT160295\' '
    selSql(selstr)

