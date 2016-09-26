import pyodbc
import datetime
import cx_Oracle
import sys
import socket
import socketserver
import _thread
import schedule
import time
import re
import hashlib
import urllib.request
import urllib.parse

# 连接oracle数据库
# 读取视图，按每次1000条记录读取，
# 读取后，把记录写到web服务器。

# 当前查询日期
STUDYDONEDATE = datetime.datetime.strptime('2009-10-18 00:00:00', '%Y-%m-%d %H:%M:%S')
STUDYLIST = []  # 检查的列表
STUDYINDEX = 0  # 发送的检查索引
SOCKETCONTENT = ''  # socket接收到的内容



# 发送报告内容
def sendSocket(content):
    HOST = '192.168.1.25'  # The remote host
    PORT = 6700  # The same port as used by the server
    # uid = r'studyuid=\\192.9.216.23\pacsimage2\NearLine\201603\20160316\X354954\A2614136'
    # uid = r'studyuid=end'
    uid = r'%s' % content
    s = socket.socket(socket.AF_INET,
                      socket.SOCK_DGRAM)  # socket.SOCK_DGRAM -for udp   socket.SOCK_STREAM- for tcp
    s.connect((HOST, PORT))
    s.sendall(bytes(uid, encoding='utf8', errors='字符串错误'))
    data = s.recv(1024)
    s.close()
    print('Received', repr(data))

# 查询数据库
def selSql(selStr):
    sqlresult = []
    connection = cx_Oracle.Connection("system/Jdimage123@192.168.2.112/ypacs")
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
        # print(row)
    # print(sum)
    connection.close()
    return sqlresult


# 获取病人列表
def getpatientlist(STUDYDONEDATE):
    selstr = 'select STUDIESINSTUID,ACCESSIONNUMBER  from vhis WHERE  REPORTSSTATUS = 100 and STUDYDONEDATE>=%s and STUDYDONEDATE< %s order by StudiesDoneTime' % (STUDYDONEDATE.strftime('%Y%m%d'), (STUDYDONEDATE + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
    patientlistsql = selSql(selstr)
    return patientlistsql


# 获取检查的所有image路径
def getimages(accessionnumber):
    selstr = 'SELECT IMAGESFILENAME FROM vpacsimages  where AccessionNumber= \'%s\' ' % accessionnumber
    imagelistsql = selSql(selstr)
    imagelist = []
    for temp in imagelistsql:
        imagelist.append(temp[0])
    print(imagelist)

# 获取报告
def getreport(STUDYDONEDATE):
    selstr = 'select STUDIESINSTUID,STUDIESMODALITIES,PATIENTSALIAS,ACCESSIONNUMBER,STUDYDONEDATE,STUDIESDONETIME,RESULTSEXAMINEALIAS,REPORTSDOCTORALIAS,REPORTSEVIDENCES,REPORTSCONCLUSION,APPROVEDATE,APPROVETIME,RECORDSDOCTORALIAS  from vhis WHERE  REPORTSSTATUS = 100 and STUDYDONEDATE>=%s and STUDYDONEDATE< %s order by StudiesDoneTime' % (STUDYDONEDATE.strftime('%Y%m%d'), (STUDYDONEDATE + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
    reportlistsql = selSql(selstr)
    reportdic = {}
    for temp in reportlistsql:
        report = {}
        m1 = hashlib.md5()
        m1.update(temp[0].encode('utf_8'))
        report['uuid'] = m1.hexdigest() # md5 加密
        report['modality'] = temp[1][1:-1]
        report['patientName'] = temp[2]
        report['patientId'] = temp[3]
        report['studyDate'] = datetime.datetime.strptime(temp[4] + temp[5], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        report['reportBody'] = temp[6]
        report['reportDoctorName'] = temp[7]
        report['imageShow'] = temp[8]
        report['diagnosis'] = temp[9]
        report['reportDate'] = datetime.datetime.strptime(temp[10] + temp[11], '%Y%m%d%H%M%S').strftime(
            '%Y-%m-%d %H:%M:%S')
        report['auditDoctorName'] = temp[12]

        reportdic['clinicId'] = ''
        reportdic['typeName'] = ''
        reportdic['patientSex'] = ''
        reportdic['patientPhone'] = ''
        reportdic['hospitalName'] = '影像云诊断中心'
        reportdic['pacsCode'] = 'jdimage'

        # reportdic['applyDoctorName'] = '张**'

        reportdic[report['uuid']] = report
    return reportdic

# 发送一个study的image路径
def sendimages(STUDYINDEX):
    study = STUDYLIST[STUDYINDEX]
    imagelist = getimages(study[1])
    for image in imagelist:  # 逐一发送image路径
        content = study[0] + '=' + image
        sendSocket(content)
    contentend = study[0] + '=end'  # 一个stduy的路径全发送完成后，发送一个完成标识
    sendSocket(contentend)

# socket服务
class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global SOCKETCONTENT
        data = self.request[0].strip()
        socket = self.request[1]
        # print("{} wrote:".format(self.client_address[0]))
        # print(data)
        SOCKETCONTENT = data.decode()
        socket.sendto(data.upper(), self.client_address)

# socketserver 打开
def startsocketserver():
    HOST, PORT = "192.168.1.138", 6701
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()


# 提交报告
def submitreport(reportdic):
    # 接口地址
    url = 'http://app.jdimage.cn/api/report/upload'
    reportdata = urllib.parse.urlencode(reportdic)
    reportdata = reportdata.encode('utf-8')
    with urllib.request.urlopen(url, reportdata) as f:
        postResult = eval(
            (f.read().decode('utf-8')).replace('true', 'True'))  # {"flag":true}{"msg":"有参数未传","flag":false}
        if 'flag' in postResult.keys():
            if True == postResult['flag']:
                print(postResult['flag'])
            else:  # 发送报告失败，保存到数据库
                pass
        print(f.read().decode('utf-8'))



if __name__ == "__main__":
    # print(reportlist)
    # 开启socket服务
    try:
        _thread.start_new_thread(startsocketserver, ())
    except:
        print( "Error: unable to start thread socketServer")

    reportdic = getreport(STUDYDONEDATE)      # 获取一天的报告
    STUDYLIST = getpatientlist(STUDYDONEDATE)  # 获取一条的检查
    if STUDYINDEX < len(STUDYLIST):
         sendimages(STUDYINDEX)                 # 发送一个检查的所有图像
    else:
        STUDYDONEDATE = STUDYDONEDATE + datetime.timedelta(hours=24)  # 日期 +1天

    while True:
        time.sleep(2)
        socketresult = re.split('=', SOCKETCONTENT)
        if socketresult[1] == '1':    # 一个检查发送图像成功
            STUDYINDEX += 1
            report = reportdic[socketresult[0]]  # 获取报告
            submitreport(report)                 # 提交报告
            if STUDYINDEX < len(STUDYLIST):
                sendimages(STUDYINDEX)  # 发送所有的检查
            else:                                                            # 一天的检查发完后
                STUDYINDEX = 0
                STUDYDONEDATE = STUDYDONEDATE + datetime.timedelta(hours=24)  # 日期 +1天
                STUDYLIST = getpatientlist(STUDYDONEDATE)  # 获取一条的检查
        elif socketresult[1] == '0':    # 一个检查发送图像成功
            pass
            #保存失败记录

        print(socketresult)




