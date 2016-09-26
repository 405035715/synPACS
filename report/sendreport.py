import urllib.request
import urllib.parse
import hashlib


# 提交报告
def submitreport(reportdic):
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
    submitreport()
