import pyodbc
import datetime
import cx_Oracle
import sys
import socket
import socketserver

# 连接oracle数据库
# 读取视图，按每次1000条记录读取，
# 读取后，把记录写到web服务器。

# 当前查询日期
STUDYDONEDATE = datetime.datetime.strptime('2009-10-18 00:00:00', '%Y-%m-%d %H:%M:%S')
STUDYLIST = [] #检查的列表
STUDYINDEX = 0 #发送的检查索引


# socket服务
class MyUDPHandler(socketserver.BaseRequestHandler):
    # 当前查询日期
    STUDYDONEDATE = datetime.datetime.strptime('2009-10-18 00:00:00', '%Y-%m-%d %H:%M:%S')
    STUDYLIST = []  # 检查的列表
    STUDYINDEX = 0  # 发送的检查索引

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print("{} wrote:".format(self.client_address[0]))
        # print(data)

        if self.STUDYINDEX < len(self.STUDYLIST):
            sendimages(self.STUDYINDEX)
            self.STUDYINDEX = self.STUDYINDEX + 1
        elif self.STUDYINDEX == len(self.STUDYLIST)-1:
            self.STUDYDONEDATE = self.STUDYDONEDATE + datetime.timedelta(hours=24)  # 查询时间加1天
            self.STUDYLIST = getpatientlist(self.STUDYDONEDATE)
            sendimages(STUDYINDEX)
            self.STUDYINDEX = self.STUDYINDEX + 1

        socket.sendto(data.upper(), self.client_address)

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
    reportlist = []
    for temp in reportlistsql:
        report = {}
        report['uuid'] = temp[0]
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
        reportlist.append(report)
    return reportlist

# 发送一个study的image路径
def sendimages(STUDYINDEX):
    study = STUDYLIST[STUDYINDEX]
    imagelist = getimages(study[1])
    for image in imagelist:  # 逐一发送image路径
        content = study[0] + '=' + image
        sendSocket(content)
    contentend = study[0] + '=end'  # 一个stduy的路径全发送完成后，发送一个完成标识
    sendSocket(contentend)




if __name__ == "__main__":
    # print(reportlist)
    # 开启socket服务
    HOST, PORT = "192.168.1.107", 6701
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()

    STUDYLIST = getpatientlist(STUDYDONEDATE)



