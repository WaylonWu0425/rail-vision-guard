package com.zzy.sms.stationmonitoringbanckend.controller;


import cn.dev33.satoken.stp.StpUtil;
import com.zzy.sms.stationmonitoringbanckend.entity.User;
import com.zzy.sms.stationmonitoringbanckend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;


import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@RestController
@RequestMapping("/upload")
public class FileUploadController {

    private static final String UPLOAD_DIR = "uploads/";
//    @Value("${server.url}") // 从配置文件中读取服务器地址
//    private String serverUrl;
    @Autowired
    UserService userService;

    @PostMapping("/uploadAvatar")
    public ResponseEntity<String> uploadAvatar(@RequestParam("file") MultipartFile file) {
        Long loginId = StpUtil.getLoginIdAsLong();
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("文件为空");
        }

        try {
            // 创建上传目录（如果不存在）
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }
            // 生成唯一的文件名
            String originalFileName = file.getOriginalFilename();
            String fileExtension = originalFileName.substring(originalFileName.lastIndexOf(".")); // 获取文件扩展名
            String uniqueFileName = UUID.randomUUID() + fileExtension; // 使用 UUID 作为文件名

            // 保存文件
            Path filePath = uploadPath.resolve(uniqueFileName);
            Files.copy(file.getInputStream(), filePath);

            // 返回文件路径或URL
//            String fileUrl = serverUrl + "/" + UPLOAD_DIR + uniqueFileName;
            String fileUrl = uniqueFileName;
            User user = new User(loginId, null,null,null,null,fileUrl, null, null,null,null,null,null,null,null);
            userService.update(user);
            return ResponseEntity.ok(fileUrl);
        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("文件上传失败");
        }
    }
    @GetMapping("/getAvatar")
    public ResponseEntity<Resource> getAvatar(@RequestParam("filename") String filename) {
        try {
            Path filePath = Paths.get(UPLOAD_DIR).resolve(filename).normalize();
            Resource resource = new UrlResource(filePath.toUri()); // 使用 Resource 类型

            if (resource.exists() || resource.isReadable()) {
                return ResponseEntity.ok()
                        .header(HttpHeaders.CONTENT_TYPE, "image/jpeg") // 根据文件类型设置 Content-Type
                        .body(resource);
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
}