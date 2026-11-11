<template>
  <div class="user">
    <div class="aside">
        <div class="user-avatar">
            <el-upload
                class="avatar-uploader"
                :http-request="uploadUserAvatar"
                :show-file-list="false"
                :on-success="handleAvatarSuccess"
                :before-upload="beforeAvatarUpload"
            >
                <img v-if="imageUrl" :src="imageUrl" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus/></el-icon>
            </el-upload>
        </div>
    </div>
    <div class="main">
        <div class="form">
            <el-form :model="form" label-width="auto" style="width: 35%">
                <el-form-item label="昵称">
                    <el-input v-model="form.username" :disabled="!isEditMode"/>
                </el-form-item>

                <el-form-item label="账号">
                    <el-input v-model="form.account" :disabled="!isEditMode"/>
                </el-form-item>

                <el-form-item label="密码" v-if="!showPasswordFields">
                    <el-input v-model="pwd" show-password disabled/>
                </el-form-item>
                <el-form-item label="旧密码" v-if="showPasswordFields">
                    <el-input v-model="oldPassword" show-password :disabled="!isEditMode"/>
                </el-form-item>
                <el-form-item label="新密码" v-if="showPasswordFields">
                    <el-input v-model="form.password" show-password :disabled="!isEditMode"/>
                </el-form-item>
                
                <el-form-item label="性别">
                    <el-select v-model="form.sex" :disabled="!isEditMode">
                        <el-option label="男" :value="1" />
                        <el-option label="女" :value="0" />
                    </el-select>
                </el-form-item>
                <el-form-item label="电话">
                    <el-input v-model="form.phoneNumber" :disabled="!isEditMode"/>
                </el-form-item>
                <el-form-item label="邮件">
                    <el-input v-model="form.email" :disabled="!isEditMode"/>
                </el-form-item>
                <el-form-item>
                <el-button type="primary" @click="editForm()" v-if="!showPasswordFields">修改</el-button>
                <el-button @click="cancelEdit" v-if="showPasswordFields">取消</el-button>
                <el-button @click="onSubmit" v-if="showPasswordFields">确认</el-button>
                </el-form-item>
            </el-form>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {uploadAvatar, getAvatar, updateUser} from '@/http/api/user'
import { useStore } from 'vuex';

const imageUrl = ref('');
const store = useStore()
const handleAvatarSuccess = (response, uploadFile) => {
    imageUrl.value = URL.createObjectURL(uploadFile.raw);
};

const beforeAvatarUpload = (rawFile) => {
    if (rawFile.type !== 'image/jpeg') {
        ElMessage.error('头像必须是jpg格式!');
        return false;
    } else if (rawFile.size / 1024 / 1024 > 2) {
        ElMessage.error('头像图片大小不能超过 2MB!');
        return false;
    }
    return true;
};
const uploadUserAvatar = async(file)=> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await uploadAvatar(file);
    store.dispatch('user/changeAvatar', response.data);
}

const fetchAvatar = async()=> {
    const response = await getAvatar(store.state.user.userInfo.avatar);
    if (response.data instanceof Blob) {
      imageUrl.value = URL.createObjectURL(response.data)
    } else {
      console.error('API 返回的数据不是 Blob:', response.data);
    }
    
}

//用户信息表单
const form = reactive({
  username: '',
  account: '',
  password: '',
  sex: '',
  phoneNumber: '',
  email: '',
})


const pwd = ref('******')
const oldPassword = ref('')
//获取用户数据
const getUserInfo = ()=> {
    form.username = store.state.user.userInfo.username;
    form.account = store.state.user.userInfo.account;
    oldPassword.value = '';
    form.password = '';
    form.sex = store.state.user.userInfo.sex;
    form.phoneNumber = store.state.user.userInfo.phoneNumber;
    form.email = store.state.user.userInfo.email;
}
// 显示密码输入框状态
const showPasswordFields = ref(false);
const isEditMode = ref(false);

const editForm  = ()=> {
    isEditMode.value = true;
    showPasswordFields.value = true; // 显示密码输入框
}
const cancelEdit = ()=> {
    isEditMode.value = false;
    showPasswordFields.value = false; // 隐藏密码输入框
    getUserInfo();
}
const onSubmit = async() => {
    isEditMode.value = false; // 关闭编辑模式
    showPasswordFields.value = false; // 隐藏密码输入框
    try {
        const response = await updateUser(form, oldPassword.value);
        if(response.data.success) {
            store.commit("updateUserInfo", form);
            ElMessage({
                message: '修改成功',
                type: 'success',
                plain: true,
            })
        }else if(response.data.success==false) {
            ElMessage({
                message: '密码不正确',
                type: 'error',
                plain: true,
            })
        }
    }catch {
        const response = await updateUser(form, oldPassword.value);
        if(response.data.success) {
            ElMessage({
                message: '修改失败',
                type: 'error',
                plain: true,
            })
        }
    }
}

onMounted(() => {
    fetchAvatar();
    getUserInfo();
    console.log(store.state.user.userInfo);
    
})
</script>

<style scoped>
.user {
    width: 100%;
    height: 100%;
    display: flex;
}
.aside {
    position: relative;
    width: 35%;
    height: 100%;
}
.user-avatar {
    position: absolute;
    transform: translate(-50%, -50%);
    top: 50%;
    left: 50%;
    width: 300px;
    height: 300px;
}
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  background-color: #adb0b5;
}
.main {
    flex: 1;
}
.avatar{
    height: 300px;
    width: 300px;
    object-fit: cover; /* 让图片按照比例填充 */
}
.main {
    position: relative;
    height: 100%;
    /* background-color: green; */
}
.form {
    width: 100%;
    position: absolute;
    top: 50%;
    left: 15%;
    transform: translateY(-50%);
}
</style>