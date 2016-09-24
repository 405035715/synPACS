import os
import datetime


# 从医院的his获取指定日期的所有检查
# 参数： startdate     开始时间
#        enddate       结束时间
def getstudiesfromhis(startdate, enddate):
    studylist = []  # 检查列表
    dic = {'AccessionNumber': '123123', 'STUDIESINSTUID': '1.2.840.473.8013.20091018.1075032.906.10142.1'}  # 一次检查
    return studylist


# 从医院的his获取一次检查的图片文件位置
# 参数：AccessionNumber 一次检查在his中的唯一号
def getimagesfromhis(accessionnumber):
    pass


# 从医院的his获取一次检查的报告
# 参数：AccessionNumber 一次检查在his中的唯一号
def getreportfromhis(accessionnumber):
    reportdic = {}
    return reportdic


if __name__ == '__main__':
    print(os.listdir(os.getcwd()))

    pass
