import os
import pymysql
from datetime import datetime

# 数据库连接信息
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'db': 'station_monitoring',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def main():
    print("开始测试数据库写入...")
    connection = None
    
    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        
        # 查看表结构
        with connection.cursor() as cursor:
            try:
                cursor.execute("DESC alarm_info")
                columns = cursor.fetchall()
                print("表结构:")
                for col in columns:
                    print(f"- {col['Field']}: {col['Type']}, Null: {col['Null']}, Default: {col.get('Default')}")
            except Exception as e:
                print(f"查询表结构失败: {e}")
        
        # 查询表数据
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT COUNT(*) as count FROM alarm_info")
                result = cursor.fetchone()
                print(f"当前表中有 {result['count']} 条记录")
            except Exception as e:
                print(f"查询表数据失败: {e}")
        
        # 插入测试数据
        with connection.cursor() as cursor:
            try:
                # 转换bit类型参数
                bit_type = (1).to_bytes(1, byteorder='big')
                bit_deal_flag = (0).to_bytes(1, byteorder='big')
                
                sql = """INSERT INTO alarm_info
                        (content, camera_id, type, deal_flag, create_time, deal_user_id, level)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql, (
                    "测试告警内容", 
                    1,                  # camera_id
                    bit_type,           # type: 1表示检测到人
                    bit_deal_flag,      # deal_flag: 0表示未处理
                    datetime.now(),     # create_time
                    0,                  # deal_user_id: 0表示默认用户
                    bit_type            # level: 1表示警告级别
                ))
                
                # 提交更改
                connection.commit()
                print(f"成功插入测试数据，ID: {cursor.lastrowid}")
            except Exception as e:
                print(f"插入数据失败: {e}")
                connection.rollback()
        
        # 再次查询表数据
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT COUNT(*) as count FROM alarm_info")
                result = cursor.fetchone()
                print(f"插入后表中有 {result['count']} 条记录")
                
                cursor.execute("SELECT * FROM alarm_info ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                if result:
                    print("最新一条记录:")
                    for key, value in result.items():
                        print(f"- {key}: {value}")
                else:
                    print("没有找到记录")
            except Exception as e:
                print(f"查询数据失败: {e}")
    
    except Exception as e:
        print(f"发生错误: {e}")
    
    finally:
        if connection:
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    main() 