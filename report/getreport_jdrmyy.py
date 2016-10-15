import datetime
import cx_Oracle
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
import mysql.connector

#1.未上传01-01的除ct,cr以外的影像,.   3月1,2,3   ４月９
#20150218之前的压缩时jpeg压缩,没有转jpeg2000
#已上传 :20150101/ 20150308

'''
配置项目
'''

# 查询开始时间
STUDYDONEDATE = datetime.datetime.strptime('2015-06-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#查询结束时间
STUDYENDDATE = datetime.datetime.strptime('2015-06-15 00:00:00', '%Y-%m-%d %H:%M:%S')

#获取病人列表
# 获取病人列表的查询语句
# 获取指定病人的报告的查询语句
# 获取指定病人的影像路径的查询语句

STUDYLIST = []  # 检查的列表
STUDYINDEX = 0  # 发送的检查索引
SOCKETCONTENT = ''  # socket接收到的内容

# 查询数据库
def selSql(selStr):
    sqlresult = []
    print(selStr)
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
        sqlresult.append(list(row))
        if sum == 111:
            pass
        print(row)
    connection.close()
    return sqlresult

# 更新本地数据库
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

#计算年龄
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
    return  age

# 发送报告内容
def sendSocket(content):
    HOST = '127.0.0.1'  # The remote host
    PORT = 6700  # The same port as used by the server
    # uid = r'studyuid=\\192.9.216.23\pacsimage2\NearLine\201603\20160316\X354954\A2614136'
    # uid = r'studyuid=end'
    uid = r'%s' % content
    s = socket.socket(socket.AF_INET,
                      socket.SOCK_DGRAM)  # socket.SOCK_DGRAM -for udp   socket.SOCK_STREAM- for tcp
    s.connect((HOST, PORT))
    s.sendall(bytes(uid, encoding='utf8', errors='字符串错误'))
    #data = s.recv(1024)
    s.close()
    time.sleep(0.01)
    #print('Received', repr(data))




# 获取病人列表
def getpatientlist():
    global  STUDYDONEDATE
    selstr = 'select STUDIESINSTUID,ACCESSIONNUMBER  from VHIS_JDYX WHERE  REPORTSSTATUS = 100 and STUDIESDONEDATE>=\'%s\' and STUDIESDONEDATE< \'%s\'  order by StudiesDoneTime' % (STUDYDONEDATE.strftime('%Y%m%d'), (STUDYDONEDATE + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
    #print(selstr)
    patientlistsql = selSql(selstr)
    #print(selstr)
    return patientlistsql


# 获取检查的所有image路径
def getimages(accessionnumber):
    selstr = 'SELECT IMAGESFILENAME,SERIESMODALITY FROM vpacsimages  where AccessionNumber= \'%s\' ' % accessionnumber
    #print (selstr)
    imagelistsql = selSql(selstr)
    # imagelist = []
    #
    # for temp in imagelistsql:
    #     imagelist.append(temp[0])
    #print(imagelist)
    return imagelistsql

'''
获取报告
'''
def getreport():
    global  STUDYDONEDATE
    selstr = 'select STUDIESINSTUID,STUDIESMODALITIES,PATIENTSALIAS,ACCESSIONNUMBER,STUDIESDONEDATE,STUDIESDONETIME,RESULTSEXAMINEALIAS,REPORTSDOCTORALIAS,REPORTSEVIDENCES,REPORTSCONCLUSION,APPROVEDATE,APPROVETIME,APPROVEDOCTORALIAS,PATIENTSSEX,PATIENTSDOB,PATIENTSID,REPORTSDATE,REPORTSTIME  from VHIS_JDYX WHERE  REPORTSSTATUS = 100 and STUDIESDONEDATE>=\'%s\' and STUDIESDONEDATE< \'%s\' order by StudiesDoneTime' % (STUDYDONEDATE.strftime('%Y%m%d'), (STUDYDONEDATE + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
    reportlistsql = selSql(selstr)
    reportdic = {}
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
        #report['ACCESSIONNUMBER'] = temp[3]
        report['studyDate'] = datetime.datetime.strptime(temp[4] + temp[5], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        report['reportBody'] = temp[6]
        report['reportDoctorName'] = temp[7]
        report['imageShow'] = temp[8]
        report['diagnosis'] = temp[9]
        report['reportDate'] = datetime.datetime.strptime(temp[16] + temp[17], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        report['auditDoctorName'] = temp[12]
        if temp[13]:
            report['patientSex'] = temp[13].replace('F', '女').replace('M', '男')
        else:
            report['patientSex'] ='/'
        report['patientAge'] = calculate_age(datetime.datetime.strptime(temp[14], '%Y%m%d'),datetime.datetime.strptime(report['reportDate'], '%Y-%m-%d %H:%M:%S'))
        report['patientId'] = temp[3]
        report['clinicId'] = '/'
        report['typeName'] = '/'
        report['officeName'] = '/'
        report['patientPhone'] = '/'
        report['hospitalName'] = '建德市第一人民医院'
        report['pacsCode'] = 'JDRMYY'
        report['applyDoctorName'] = '/'
        report['auditDate']  = datetime.datetime.strptime(temp[10] + temp[11], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        reportdic[report['uuid']] = report
    return reportdic

# 发送一个study的image路径
def sendimages():
    global STUDYINDEX, SOCKETCONTENT
    study = STUDYLIST[STUDYINDEX]
    print('sendimages')
    imagelist = getimages(study[1])
    studyimagesifull = 1   # 是否study的image有丢失0有丢失1没有丢失
    studyimagesisexist = 0 # 是否study的有image   0没有1有
    if len(imagelist) == 0:
        print('没有影像')     # error
        SOCKETCONTENT = study[0] + '=0'
        return
    extimages = []
    for image in imagelist:  # 逐一发送image路径
        if os.path.exists(image[0]):
            studyimagesisexist = 1
            if image[1] == 'SR' or image[1] =='REQUEST' or image[1] == 'SC' or image[1] == 'PR':   # 'SR''REGUEST'的最后发送
                extimages.append(image)
            else:
                content = study[0] + '=' + image[0]
                print(content)
                sendSocket(content)
        else:
            studyimagesifull = 0
    for extimage in extimages:
        content = study[0] + '=' + extimage[0]
        print(content)
        sendSocket(content)
    if studyimagesisexist == 1:
        contentend = study[0] + '=end'  # 一个stduy的路径全发送完成后，发送一个完成标识
        print(contentend)
        sendSocket(contentend)
    studyimagestatus = 0    # 0图像空1图像不全2图像全
    if studyimagesifull == 1:
        studyimagestatus =2
    elif studyimagesisexist ==1:
        studyimagestatus = 1
    print(datetime.datetime.now())
    # 记录状态到数据库
    sqlstr = (
        "UPDATE vhis_jdyx SET SENDIMAGES = %s "
        "WHERE AccessionNumber = %s ")
    values = (studyimagestatus, study[1])
    updatemysql(sqlstr, values)

# socket服务
class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global SOCKETCONTENT
        data = self.request[0].strip()
        socket = self.request[1]
        # print("{} wrote:".format(self.client_address[0]))
        print(data)
        SOCKETCONTENT = data.decode()
        socket.sendto(data.upper(), self.client_address)

# socketserver 打开
def startsocketserver():
    HOST, PORT = "127.0.0.1", 6701
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()


# 提交报告
def submitreport(reportdic):
    # 接口地址
    url = 'http://app.jdimage.cn/api/report/upload'
    reportdata = urllib.parse.urlencode(reportdic)
    if len(reportdic['reportBody']) < 500:
        reportdata = reportdata.encode('utf-8')


        with urllib.request.urlopen(url, reportdata) as f:
            tmp = (f.read().decode('utf-8')).replace('true', 'True').replace('false', 'False')
            postResult = eval(tmp)  # {"flag":true}{"msg":"有参数未传","flag":false}
            print(postResult)
            if 'flag' in postResult.keys():
                if True == postResult['flag']:
                    print(postResult['flag'])
                    # 记录状态到数据库
                    sqlstr = (
                        "UPDATE vhis_jdyx SET SENDREPORT = %s  "
                        "WHERE AccessionNumber = %s  ")
                    values = ( 1, reportdic['patientId'])
                    updatemysql(sqlstr, values)
                else:  # 发送报告失败，保存到数据库
                    pass
            print(f.read().decode('utf-8'))



if __name__ == "__main__":
    os.environ['nls_lang'] = 'AMERICAN_AMERICA.AL32UTF8' #解决CX_ORACLE查询出错的编码问题,
    # print(reportlist)
    # 开启socket服务
    try:
        _thread.start_new_thread(startsocketserver, ())
    except:
        print( "Error: unable to start thread socketServer")

    reportdic = getreport()        # 获取一天的报告
    STUDYLIST = getpatientlist()   # 获取一条的检查
    # print(STUDYLIST)
    if STUDYINDEX < len(STUDYLIST):
        sendimages()               # 发送一个检查的所有图像
    #else:
        # STUDYDONEDATE = STUDYDONEDATE + datetime.timedelta(hours=24)  # 日期 +1天
    while True:
        time.sleep(2)
        print('SOCKETCONTENT %s'% SOCKETCONTENT)
        if SOCKETCONTENT != '':
            socketresult = re.split('=', SOCKETCONTENT)
            if socketresult[1] == '1' or socketresult[1] == '0':    # 接收到socketserver的返回消息:图像上传到云的结果
                # 保存发送结果到数据库
                STUDYINDEX += 1
                if socketresult[1] == '1' and socketresult[0] != '':  #
                    m1 = hashlib.md5()
                    m1.update(socketresult[0].encode('utf_8'))
                    studyuid = m1.hexdigest()  # md5 加密
                    report = reportdic[studyuid]  # 获取报告
                    print(report)
                    # time.sleep(3)
                    submitreport(report)                 # 提交报告
                if STUDYINDEX < len(STUDYLIST):
                    SOCKETCONTENT = ''
                    print(STUDYINDEX)
                    sendimages()  # 发送一个检查的所有图像
                else:                                                            # 重新开始一天
                    STUDYINDEX = 0
                    print('开始第二天')
                    if  STUDYDONEDATE < STUDYENDDATE:
                        STUDYDONEDATE = STUDYDONEDATE + datetime.timedelta(hours=24)  # 日期 +1天
                        STUDYLIST = getpatientlist()  # 获取一条的检查
                        reportdic = getreport()  # 获取一天的报告
                        if STUDYINDEX < len(STUDYLIST):
                            sendimages()  # 发送一个检查的所有图像
                        time.sleep(60 * 5)
                        print(STUDYINDEX)
                    else:
                        print('发送完成!')
                        break

    #
    #     print(socketresult)