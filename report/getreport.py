import pyodbc
import datetime
import cx_Oracle
import sys

# 连接oracle数据库
# 读取视图，按每次1000条记录读取，
# 读取后，把记录写到web服务器。

# 当前查询日期
StudiesDoneDate = datetime.datetime.strptime('2009-10-18 00:00:00', '%Y-%m-%d %H:%M:%S')


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
def getpatientlist(StudiesDoneDate):
    selstr = 'select STUDIESINSTUID,PATIENTSALIAS,ACCESSIONNUMBER  from vhis WHERE  REPORTSSTATUS = 100 and StudiesDoneDate>=%s and StudiesDoneDate< %s order by StudiesDoneTime' % (StudiesDoneDate.strftime('%Y%m%d'), (StudiesDoneDate + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
    patientlistsql = selSql(selstr)
    return patientlistsql


# 获取检查的所有image路径
def getimages(accessionnumber):
    selstr = 'SELECT IMAGESFILENAME FROM vpacsimages  where AccessionNumber= \'%s\' ' % accessionnumber
    imagelistsql = selSql(selstr)
    print(imagelistsql)

# 获取报告
def getreport(StudiesDoneDate):
    selstr = 'select STUDIESINSTUID,STUDIESMODALITIES,PATIENTSALIAS,ACCESSIONNUMBER,STUDIESDONEDATE,STUDIESDONETIME,RESULTSEXAMINEALIAS,REPORTSDOCTORALIAS,REPORTSEVIDENCES,REPORTSCONCLUSION,APPROVEDATE,APPROVETIME,RECORDSDOCTORALIAS  from vhis WHERE  REPORTSSTATUS = 100 and StudiesDoneDate>=%s and StudiesDoneDate< %s order by StudiesDoneTime' % (StudiesDoneDate.strftime('%Y%m%d'), (StudiesDoneDate + datetime.timedelta(hours=24)).strftime('%Y%m%d'))
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


if __name__ == "__main__":
    # print(reportlist)
    getpatientlist(StudiesDoneDate)
    getimages('X354954')
