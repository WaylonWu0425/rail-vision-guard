import os
import pymysql
import time
from datetime import datetime
import logging
import sys
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("manual_write.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 有效的用户ID
VALID_USER_ID = 39

def write_test_record():
    """写入一条测试记录到alarm_info表"""
    conn = None
    try:
        logger.info("开始尝试写入测试记录...")
        
        # 数据库连接
        logger.info("尝试连接数据库...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=os.environ.get("DB_PASSWORD", ""),
            database='station_monitoring',
            charset='utf8mb4'
        )
        logger.info("数据库连接成功")
        
        cursor = conn.cursor()
        
        # 获取当前时间戳作为内容的一部分，确保每条记录都不同
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"手动测试写入 {timestamp}"
        logger.info(f"生成内容: {content}")
        
        # 写入记录
        sql = """INSERT INTO alarm_info 
                (content, camera_id, type, deal_flag, deal_user_id, level) 
                VALUES (%s, %s, b'01', b'0', %s, b'01')"""
        
        logger.info(f"准备执行SQL: {sql}")
        logger.info(f"参数: {content}, 1, {VALID_USER_ID}")
        
        cursor.execute(sql, (content, 1, VALID_USER_ID))
        logger.info("SQL执行成功，准备提交事务")
        
        conn.commit()
        logger.info("事务提交成功")
        
        # 查询刚写入的记录
        query_sql = "SELECT id FROM alarm_info WHERE content = %s"
        logger.info(f"查询SQL: {query_sql}, 参数: {content}")
        
        cursor.execute(query_sql, (content,))
        result = cursor.fetchone()
        
        if result:
            record_id = result[0]
            logger.info(f"成功写入记录，ID: {record_id}, 内容: {content}")
            return True
        else:
            logger.error(f"写入记录失败，未能查询到记录: {content}")
            return False
    except pymysql.MySQLError as sql_error:
        logger.error(f"MySQL错误: {sql_error}")
        error_code = getattr(sql_error, 'args', [None])[0]
        if error_code:
            logger.error(f"MySQL错误码: {error_code}")
        logger.error(f"MySQL错误堆栈: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"写入记录一般异常: {e}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return False
    finally:
        if conn:
            try:
                conn.close()
                logger.info("数据库连接已关闭")
            except Exception as close_error:
                logger.error(f"关闭数据库连接时出错: {close_error}")

def main():
    """主函数，手动写入一条记录"""
    try:
        logger.info("开始手动写入测试...")
        if write_test_record():
            logger.info("手动写入测试成功")
        else:
            logger.error("手动写入测试失败")
    except Exception as e:
        logger.error(f"手动写入测试异常: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 