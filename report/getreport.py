import pyodbc
import datetime

# 连接oracle数据库
# 读取视图，按每次1000条记录读取，
# 读取后，把记录写到web服务器。


if __name__ == "__main__":
    print('test')

# 功能：查询最大count数的记录的报告
# 查询条件：patientid; 查询数量：count
# 查询结果：patientid;name;sex;age;检查部位:bodypart;所见：diagfind;印象conclusion；检查医生:doctor
def getReportOfFSK(patientid):
    swhere = ' \'\'\'\' ,\'\'\'\' , \'\'%s\'\'   ' % (patientid)
    patientsql = 'SET NOCOUNT ON; EXEC  tj_P_RUN_PROCDURE_WITH_SELECTRETURN  \'sp_get_study_info3\' ,\' %s  \' ' % swhere
    patientlist = selSql(patientsql, 'FSKDB')
    reportDic = {}
    if 1 == len(patientlist):  # 只有一条记录时
        patient = patientlist[0]
        print(patient)
        reportDic['patientid'] = patient[0]  # patientid
        reportDic['name'] = patient[1]  # name
        if patient[2] == 0 :
            reportDic['sex'] = '男'  # sex
        elif patient[2] == 1 :
            reportDic['sex'] = '女'  # sex
        else:
            reportDic['sex'] = '其他'  # sex
        reportDic['age'] = patient[3]  # age
        reportDic['bodypart'] = patient[15]  # bodypart
        reportDic['time'] = datetime.datetime.strftime(patient[16], "%Y-%m-%d %H:%M:%S")  # 报告时间
        reportDic['diagfind'] = patient[13]  # diagfind 所见
        reportDic['conclusion'] = patient[14]  # conclusion 印象
        reportDic['doctor'] = patient[7]  # 检查医生
        reportDic['modality'] = patient[17] #检查方式
    return reportDic


#查询数据库
def selSql(selStr, sqldbtype):
    sqlresult =[]
    connectStr = 'DRIVER={SQL Server};SERVER=192.168.1.4;PORT=1433;DATABASE=espacs;UID=sa;PWD=easy'
    cnxn = pyodbc.connect(connectStr)
    cursor = cnxn.cursor()
    try:
        cursor.execute(selStr)
    except Exception as e:
        print(e)
    sum = 0
    while 1:
        row = cursor.fetchone()
        #sum = sum + 1
        if not row:
            break
        sqlresult.append(list(row))
        #print(row)
    #print(sum)
    cnxn.close
    return sqlresult