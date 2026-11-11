package com.zzy.sms.stationmonitoringbanckend.service;

import com.zzy.sms.stationmonitoringbanckend.entity.User;

import java.util.List;

public interface UserService {
    User getUserById(Long id);

    int insertUser(User user);
    User queryAllByLimit(User user);
    int update(User user);
    List<User> getAllUser();
    Boolean forbiddenUser(Long id);
    Boolean deleteUser(Long id);
    List<User> searchUser(Long username);
}
