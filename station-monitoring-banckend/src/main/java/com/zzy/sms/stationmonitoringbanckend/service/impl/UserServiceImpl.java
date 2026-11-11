package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.zzy.sms.stationmonitoringbanckend.entity.User;
import com.zzy.sms.stationmonitoringbanckend.mapper.UserMapper;
import com.zzy.sms.stationmonitoringbanckend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @description:
 * @author: zzy
 * @create: 2025-01-16 23:50
 **/
@Service
public class UserServiceImpl implements UserService {
    @Autowired
    private UserMapper userMapper;
    @Override
    public User getUserById(Long id) {
        return userMapper.getUserById(id);
    }

    @Override
    public int insertUser(User user) {
        return userMapper.insertUser(user);
    }

    @Override
    public User queryAllByLimit(User user) {
        return userMapper.queryAllByLimit(user);
    }

    @Override
    public int update(User user) {
        return userMapper.update(user);
    }

    @Override
    public List<User> getAllUser() {
        return userMapper.getAllUser();
    }

    @Override
    public Boolean forbiddenUser(Long id) {
        return userMapper.forbiddenUser(id);
    }

    @Override
    public Boolean deleteUser(Long id) {
        return userMapper.deleteUser(id);
    }

    @Override
    public List<User> searchUser(Long username) {
        return userMapper.searchUser(username);
    }


}
