/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80032
 Source Host           : localhost:3306
 Source Schema         : station_monitoring

 Target Server Type    : MySQL
 Target Server Version : 80032
 File Encoding         : 65001

 Date: 05/06/2025 20:20:26


    1. camara-已插入
    2. user-已插入
    3. alarm_info-已插入
    4. preset_point-已插入
    5. ballmachine-已插入
    6. camera_alarm-已插入
    7. gunmachine-已插入
    8. switch_preset_point-已插入
    9. switch-已插入
    10. task-已插入
    11. task_attachment-已插入
    12. task_history-已插入
*/
create database station_monitoring;
use station_monitoring;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alarm_info
-- 01
-- ----------------------------
DROP TABLE IF EXISTS `alarm_info`;
CREATE TABLE `alarm_info`
(
    `id`           bigint                                                        NOT NULL AUTO_INCREMENT COMMENT 'id',
    `content`      varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '报警信息',
    `camera_id`    bigint                                                        NOT NULL COMMENT '外键，报警设备id',
    `type`         bit(2)                                                        NULL DEFAULT NULL COMMENT '非法事物类型，0入侵警告， 1障碍物警告',
    `deal_flag`    bit(1)                                                        NULL DEFAULT NULL COMMENT '0未处理 1已处理',
    `create_time`  datetime                                                      NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '报警时间',
    `deal_time`    datetime                                                      NULL DEFAULT NULL COMMENT '处理时间',
    `deal_user_id` bigint                                                        NULL DEFAULT NULL COMMENT '外键，处理人id',
    `level`        bit(2)                                                        NULL DEFAULT NULL COMMENT '0轻度  1中度  2重度',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `user_id_2` (`deal_user_id` ASC) USING BTREE,
    INDEX `camera_id5` (`camera_id` ASC) USING BTREE,
    CONSTRAINT `camera_id5` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT `user_id_2` FOREIGN KEY (`deal_user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  AUTO_INCREMENT = 8116
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of alarm_info
-- 02 已插入
-- ----------------------------

-- ----------------------------
-- Table structure for ballmachine
-- 02
-- ----------------------------
DROP TABLE IF EXISTS `ballmachine`;
CREATE TABLE `ballmachine`
(
    `id`              bigint NOT NULL AUTO_INCREMENT,
    `camera_id`       bigint NULL DEFAULT NULL COMMENT '摄像头id',
    `track_id`        bigint NULL DEFAULT NULL COMMENT '股道id',
    `preset_point_id` bigint NULL DEFAULT NULL COMMENT '预置点id',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `unique_camera_track_preset` (`camera_id` ASC, `track_id` ASC, `preset_point_id` ASC) USING BTREE,
    INDEX `preset_point_id` (`preset_point_id` ASC) USING BTREE,
    INDEX `camera_id` (`camera_id` ASC) USING BTREE,
    CONSTRAINT `camera_id3` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT `preset_point_id` FOREIGN KEY (`preset_point_id`) REFERENCES `preset_point` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of ballmachine
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for camera
-- 03
-- ----------------------------
DROP TABLE IF EXISTS `camera`;
CREATE TABLE `camera`
(
    `id`             bigint                                                        NOT NULL AUTO_INCREMENT COMMENT '摄像头ID',
    `name`           varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '摄像头名称',
    `product_number` int                                                           NULL DEFAULT NULL COMMENT '产品编号',
    `status`         int                                                           NOT NULL,
    `ip`             varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NOT NULL COMMENT 'IP地址',
    `type`           int                                                           NOT NULL COMMENT '类型，0球机，1枪机',
    `create_time`    datetime                                                      NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`    datetime                                                      NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `port`           int                                                           NOT NULL COMMENT '端口号',
    `username`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NOT NULL COMMENT '用户名',
    `password`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码',
    `bridgeType`     int                                                           NOT NULL COMMENT '桥接类型',
    `initViewPoint`  int                                                           NOT NULL COMMENT '初始视角',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 5
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of camera
-- 01：已插入
-- ----------------------------

-- ----------------------------
-- Table structure for camera_alarm
-- 04
-- ----------------------------
DROP TABLE IF EXISTS `camera_alarm`;
CREATE TABLE `camera_alarm`
(
    `id`          bigint                                                       NOT NULL AUTO_INCREMENT COMMENT 'id',
    `camera_id`   bigint                                                       NOT NULL COMMENT '摄像头id',
    `user_id`     bigint                                                       NULL DEFAULT NULL COMMENT '处理人id',
    `create_time` datetime                                                     NULL DEFAULT NULL COMMENT '报警时间',
    `deal_time`   datetime                                                     NULL DEFAULT NULL COMMENT '处理时间',
    `deal_flag`   varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '0' COMMENT '处理状态，0未处理，1已处理',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `user_id` (`user_id` ASC) USING BTREE,
    INDEX `camera_id2` (`camera_id` ASC) USING BTREE,
    CONSTRAINT `camera_id2` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  AUTO_INCREMENT = 59
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of camera_alarm
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for gunmachine
-- 05
-- ----------------------------
DROP TABLE IF EXISTS `gunmachine`;
CREATE TABLE `gunmachine`
(
    `id`          bigint NOT NULL AUTO_INCREMENT COMMENT '预置点id',
    `camera_id`   bigint NULL DEFAULT NULL COMMENT '摄像头id',
    `track_id`    bigint NULL DEFAULT NULL COMMENT '股道id',
    `small_range` int    NULL DEFAULT NULL COMMENT '小范围',
    `wide_range`  int    NULL DEFAULT NULL COMMENT '大范围',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `camera_id4` (`camera_id` ASC) USING BTREE,
    CONSTRAINT `camera_id4` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of gunmachine
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for preset_point
-- 06
-- ----------------------------
DROP TABLE IF EXISTS `preset_point`;
CREATE TABLE `preset_point`
(
    `id`            bigint NOT NULL AUTO_INCREMENT COMMENT ' 预置点id',
    `pan_position`  int    NULL DEFAULT NULL COMMENT '水平坐标',
    `tilt_position` int    NULL DEFAULT NULL COMMENT '垂直距离',
    `zoom`          int    NULL DEFAULT NULL COMMENT '变焦系数',
    `small_range`   int    NULL DEFAULT NULL COMMENT '最小范围',
    `wide_range`    int    NULL DEFAULT NULL COMMENT '最高范围',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 36
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of preset_point
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for switch
-- 07
-- ----------------------------
DROP TABLE IF EXISTS `switch`;
CREATE TABLE `switch`
(
    `id`                     bigint                                                        NOT NULL AUTO_INCREMENT COMMENT 'id',
    `track_id`               bigint                                                        NULL DEFAULT NULL COMMENT '轨道id',
    `field`                  int                                                           NULL DEFAULT NULL COMMENT '场别',
    `throat`                 varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '0表示上，1表示下',
    `switch_preset_point_id` bigint                                                        NULL DEFAULT NULL COMMENT '道岔预置点id',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `check_unique` (`track_id` ASC, `field` ASC, `throat` ASC, `switch_preset_point_id` ASC) USING BTREE,
    INDEX `switch_preset_point_id` (`switch_preset_point_id` ASC) USING BTREE,
    CONSTRAINT `switch_preset_point_id` FOREIGN KEY (`switch_preset_point_id`) REFERENCES `switch_preset_point` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  AUTO_INCREMENT = 10
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of switch
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for switch_preset_point
-- 08
-- ----------------------------
DROP TABLE IF EXISTS `switch_preset_point`;
CREATE TABLE `switch_preset_point`
(
    `id`            bigint                                                        NOT NULL AUTO_INCREMENT,
    `pan_position`  int                                                           NULL DEFAULT NULL COMMENT '水平坐标',
    `tilt_position` int                                                           NULL DEFAULT NULL COMMENT '垂直坐标',
    `zoom`          int                                                           NULL DEFAULT NULL COMMENT '变焦系数',
    `switch_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '道岔编号',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 16
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of switch_preset_point
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for task
-- 09
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task`
(
    `id`                 bigint                                                        NOT NULL AUTO_INCREMENT COMMENT '主键id',
    `title`              varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务标题',
    `description`        varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务描述',
    `type`               varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务类型：\r\n0  日常巡检\r\n1  维修任务\r\n2  异常处理\r\n3  设备安装',
    `priority`           varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务优先级，high 2, medium 1,low 0',
    `status`             varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '待分配(已创建) 0，\r\n已接受 1，\r\n进行中 2，\r\n待审核 3，\r\n审核完成 4，\r\n审核驳回 5\r\n',
    `create_by_id`       bigint                                                        NULL DEFAULT NULL COMMENT '任务创造者',
    `assigned_to_id`     bigint                                                        NULL DEFAULT NULL COMMENT '任务执行者',
    `deal_by_id`         bigint                                                        NULL DEFAULT NULL COMMENT '审核人的id',
    `create_time`        datetime                                                      NULL DEFAULT NULL COMMENT '任务创建时间',
    `end_time`           datetime                                                      NULL DEFAULT NULL COMMENT '任务截止时间',
    `start_time`         datetime                                                      NULL DEFAULT NULL COMMENT '任务开始执行时间',
    `finish_time`        datetime                                                      NULL DEFAULT NULL COMMENT '任务完成时间',
    `operation_feedback` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '操作人员添加的任务反馈',
    `review_feedback`    varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '审核员添加的审核反馈，0表示通过，1表示未通过',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `create_by_id` (`create_by_id` ASC) USING BTREE,
    INDEX `assigned_to_id` (`assigned_to_id` ASC) USING BTREE,
    CONSTRAINT `assigned_to_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT `create_by_id` FOREIGN KEY (`create_by_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  AUTO_INCREMENT = 139
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of task
-- 插入了前4条数据
-- ----------------------------

-- ----------------------------
-- Table structure for task_attachment
-- 10
-- ----------------------------
DROP TABLE IF EXISTS `task_attachment`;
CREATE TABLE `task_attachment`
(
    `id`          bigint                                                        NOT NULL AUTO_INCREMENT COMMENT 'id',
    `task_id`     bigint                                                        NULL DEFAULT NULL COMMENT '外键任务id',
    `name`        varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '附件名称',
    `file_path`   varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '附件路径',
    `upload_time` datetime                                                      NULL DEFAULT NULL COMMENT '上传时间',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 10
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of task_attachment
-- 已处理
-- ----------------------------

-- ----------------------------
-- Table structure for task_history
-- 11
-- ----------------------------
DROP TABLE IF EXISTS `task_history`;
CREATE TABLE `task_history`
(
    `id`          bigint                                                        NOT NULL AUTO_INCREMENT COMMENT '主键 id',
    `task_id`     bigint                                                        NULL DEFAULT NULL COMMENT '任务外键id',
    `status`      varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务变更后的状态',
    `status_time` datetime                                                      NULL DEFAULT NULL COMMENT '操作变更后的时间',
    `feedback`    varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '反馈',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `task_id1` (`task_id` ASC) USING BTREE,
    CONSTRAINT `task_id1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  AUTO_INCREMENT = 50
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of task_history
-- 已插入将132换成87的数据,即前面四条数据
-- ----------------------------

-- ----------------------------
-- Table structure for user
-- 12
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`
(
    `id`              bigint                                                        NOT NULL AUTO_INCREMENT COMMENT 'id',
    `username`        varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NULL DEFAULT NULL COMMENT '用户名',
    `account`         varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NULL DEFAULT NULL COMMENT '账户,最多10位，最少5位，可以数字和字母混合',
    `password`        varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NULL DEFAULT NULL COMMENT '密码，最多15位，最少6位',
    `email`           varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮件地址',
    `avatar`          varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'defaultPicture.jpg' COMMENT '头像',
    `sex`             bit(1)                                                        NULL DEFAULT NULL COMMENT '0女1男',
    `phone_number`    varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NULL DEFAULT NULL COMMENT '电话',
    `last_login_time` datetime                                                      NULL DEFAULT NULL COMMENT '上次登录时间',
    `register_time`   datetime                                                      NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `del_flag`        bit(1)                                                        NULL DEFAULT b'0' COMMENT '0没删1已删除',
    `role`            varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci  NULL DEFAULT NULL COMMENT '角色, 1为管理员，0为普通操作人员',
    `state`           bit(1)                                                        NULL DEFAULT b'0' COMMENT '账号状态，0正常，1异常',
    `update_time`     datetime                                                      NULL DEFAULT NULL COMMENT '修改时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `unique_account` (`account` ASC) USING BTREE COMMENT '账号唯一',
    UNIQUE INDEX `unique_email` (`email` ASC) USING BTREE COMMENT '邮件唯一'
) ENGINE = InnoDB
  AUTO_INCREMENT = 333341
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- 插入了前面两个用户
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
