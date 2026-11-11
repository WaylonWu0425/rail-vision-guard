package com.zzy.sms.stationmonitoringbanckend.mapper;

import com.zzy.sms.stationmonitoringbanckend.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface UserMapper {
    User queryAllByLimit(User user);
    int insertUser(User user);
    @Select("select * from user where id = #{id}")
    User getUserById(Long id);
    int update(User user);
    @Select("select * from user where role = '0'")
    List<User> getAllUser();
    @Update("update user set state = 1 - state where id = #{user_id}")
    Boolean forbiddenUser(Long id);
    Boolean deleteUser(Long id);
    @Select("select * from user where id = #{id}")
    List<User> searchUser(Long id);
}
