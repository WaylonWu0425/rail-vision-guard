import os
import pymysql
from datetime import datetime

# 数据库连接
connection = pymysql.connect(
    host='localhost',
    user='root',
    password=os.environ.get("DB_PASSWORD", ""),
    database='station_monitoring',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 创建一个新的记录
        sql = """INSERT INTO alarm_info 
                (content, camera_id, type, deal_flag, deal_user_id, level) 
                VALUES (%s, %s, b'01', b'0', %s, b'01')"""
        cursor.execute(sql, ('直接测试告警', 1, 39))  # 使用有效的用户ID
        connection.commit()
        print(f"成功插入数据，ID: {cursor.lastrowid}")
        
        # 查询刚插入的记录
        cursor.execute("SELECT * FROM alarm_info WHERE id = %s", (cursor.lastrowid,))
        result = cursor.fetchone()
        print("插入的数据:")
        for key, value in result.items():
            print(f"- {key}: {value}")
            
finally:
    connection.close()
    print("连接已关闭") 