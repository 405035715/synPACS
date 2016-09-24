#encoding = 'utf-8'


import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import datetime
import schedule
import pyodbc

#数据库
# 用户: jd  密码: jd,1234
# 地址: 121.40.123.131
# 存储过程: jd_GetLatestFirstRecord

# 发送邮件
# 参数1：content：邮件内容
# 参数2：receivers：接收邮件地址
def sendEmail(content, receivers) :
    print('sendEmail')
    sender = '405035715@qq.com'
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "405035715@qq.com"  # 用户名
    mail_pass = "yoaemizwjxfqcagj"  # 口令
    # sender = 'wherever644@163.com'
    # mail_host = "smtp.163.com"  # 设置服务器
    # mail_user = "wherever644@163.com"  # 用户名
    # mail_pass = "zyh19870910"  # 口令
    #receivers = ['3131118228@qq.com', '1024972547@qq.com', '10138412@qq.com', '405035715@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEText(content, 'plain', 'utf-8')  # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message['From'] = Header("张跃华", 'utf-8')
    message['To'] = ";".join(receivers)
    subject = '钜典邮件'  # 标题
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        # smtpObj = smtplib.SMTP()
        # smtpObj.connect(mail_host, 25)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.close()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print("Error: 无法发送邮件")

#查询数据库
def selSql(selStr):
    sqlresult =[]
    connectStr = 'DRIVER={SQL Server};SERVER=121.40.123.131;PORT=1433;DATABASE=espacs;UID=jd;PWD=jd,1234; '
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
        #print(row)
    #print(sum)
    cnxn.close
    return sqlresult

def checkHospital():
    exceptHospital = ''  # 有问题的医院
    #allHospital = ''  # 全部的医院
    hospitalList = ['JDIMAGE', 'JDRMYY']  # 不需要检查异常的医院
    # sendEmail()
    selstr_doctors = 'SET NOCOUNT ON; EXEC  tj_P_RUN_PROCDURE_WITH_SELECTRETURN  \'jd_GetLatestFirstRecord\' ,\'\'  '  # 查询每个医院的影像的最晚时间
    doctors_tmp = selSql(selstr_doctors)
    nowTime = datetime.datetime.now()
    if len(doctors_tmp) == 0:
        mainreceivers = ['405035715@qq.com']    #连接数据库异常时，通知主邮箱
        maincontent = '无法连接云数据库，请检查！'
        sendEmail(maincontent,mainreceivers)
    for hospital in doctors_tmp:
        # strTemp1 = '%s上传影像有异常，请注意！最后一次上传影像时间：%s \n' % (hospital[1], hospital[0])
        # allHospital += strTemp1
        if hospital[1] not in hospitalList:
            if (nowTime - hospital[0]).seconds > 60 * 60 * 2:  # 最后一次上传影像的时间大于2小时的判定为异常
                strTemp2 = '%s上传影像有异常，请注意！最后一次上传影像时间：%s \n' % (hospital[1], hospital[0])
                exceptHospital += strTemp2
    if len(exceptHospital) > 0:
        receivers = ['3131118228@qq.com', '1024972547@qq.com', '10138412@qq.com', '405035715@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        sendEmail(exceptHospital, receivers)
        print(exceptHospital)

if __name__ == '__main__':
    print('监控医院数据是否正常发生，请误关闭！')
    schedule.every().day.at("11:00").do(checkHospital)  # 每天的11点、15点执行： 查询数据库
    schedule.every().day.at("15:00").do(checkHospital)
    while True:
        schedule.run_pending()
        time.sleep(1)



