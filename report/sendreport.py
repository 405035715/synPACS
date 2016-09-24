import urllib.request
import urllib.parse


# 提交报告
def submitreport():
    # 接口地址
    url = 'http://app.jdimage.cn/api/report/upload'
    # 报告内容
    reportdic = {'appKey': '', 'uuid': '', 'patientPhone': '', 'modality': '', 'hospitalName': '', 'pacsCode': '',
                 'patientName': '', 'patientSex': '', 'patientAge': '', 'typeName': '', 'clinicId': '',
                 'applyDoctorName': '', 'officeName': '', 'patientId': '', 'studyDate': '', 'reportBody': '',
                 'reportDoctorName': '', 'imageShow': '', 'diagnosis': '', 'reportDate': '', 'auditDoctorName': '', }
    reportdata = urllib.parse.urlencode(reportdic)
    reportdata = reportdata.encode('utf-8')
    with urllib.request.urlopen(url, reportdata) as f:
        print(f.read().decode('utf-8'))


if __name__ == "__main__":
    submitreport()

