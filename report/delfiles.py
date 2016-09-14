import os
import datetime

if __name__ == '__main__':
    print(os.listdir(os.getcwd()))

    path = 'F:\浙江钜典影像科技有限公司'
    childpathlist = os.listdir(path)    #列出目录下的所有文件
    for str in childpathlist:
        temppath = path + os.sep +str
        if os.path.isdir(temppath):  #判断是否目录
            print('目录:%s'%temppath)
        elif os.path.isfile(temppath):  #判断是否文件
            timestamp = os.path.getmtime(temppath) #文件的修改时间的时间戳
            date = datetime.datetime.fromtimestamp(timestamp)
            ##判断时间:早于三天前
            if date < (datetime.datetime.now() - datetime.timedelta(days=3)):
                pass
            print(date.strftime('%Y-%m-%d %H:%M:%S'))
            print('文件:%s'% temppath)
    # print (os.listdir(path))

    pass
