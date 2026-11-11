import os
import pymysql
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 有效的用户ID
VALID_USER_ID = 39

def write_test_record():
    """写入一条测试记录到alarm_info表"""
    conn = None
    try:
        # 数据库连接
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=os.environ.get("DB_PASSWORD", ""),
            database='station_monitoring',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 获取当前时间戳作为内容的一部分，确保每条记录都不同
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"连续测试写入 {timestamp}"
        
        # 写入记录
        sql = """INSERT INTO alarm_info 
                (content, camera_id, type, deal_flag, deal_user_id, level) 
                VALUES (%s, %s, b'01', b'0', %s, b'01')"""
        
        cursor.execute(sql, (content, 1, VALID_USER_ID))
        conn.commit()
        
        # 查询刚写入的记录
        cursor.execute("SELECT id FROM alarm_info WHERE content = %s", (content,))
        result = cursor.fetchone()
        if result:
            record_id = result[0]
            logger.info(f"成功写入记录，ID: {record_id}, 内容: {content}")
            return True
        else:
            logger.error(f"写入记录失败，未能查询到记录: {content}")
            return False
    except Exception as e:
        logger.error(f"写入记录异常: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """主函数，每秒写入一条记录"""
    try:
        logger.info("开始连续写入测试...")
        count = 0
        while count < 10:  # 写入10条记录后停止
            if write_test_record():
                count += 1
            time.sleep(1)  # 每秒写入一条
        logger.info(f"连续写入测试完成，共写入 {count} 条记录")
    except KeyboardInterrupt:
        logger.info("用户中断，停止写入")
    except Exception as e:
        logger.error(f"连续写入测试异常: {e}")

if __name__ == "__main__":
    main() 