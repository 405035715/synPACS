import pyodbc
import datetime
import cx_Oracle
import sys

# 连接oracle数据库
# 读取视图，按每次1000条记录读取，
# 读取后，把记录写到web服务器。


if __name__ == "__main__":
    connection = cx_Oracle.Connection("system/Jdimage123@192.168.1.128/ypacs")
    cursor = connection.cursor()
    try:
        c = cursor.execute("select * from study")
        print(c.fetchone())
    except cx_Oracle.DatabaseError:
        print('error')
        # error, = exc.args
        # print >> sys.stderr, "Oracle-Error-Code:", error.code
        # print >> sys.stderr, "Oracle-Error-Message:", error.message


