<template>
  <div class="user">
    <header class="profile-heading">
      <span class="heading-kicker">账户设置 / ACCOUNT</span>
      <h1>个人资料</h1>
      <p>查看账户信息、更新头像与联系方式。</p>
    </header>
    <div class="profile-content">
    <div class="aside">
        <div class="section-caption">账户头像</div>
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
        <p class="avatar-hint">点击头像上传 JPG 图片，文件不超过 2 MB</p>
    </div>
    <div class="main">
        <div class="section-caption">基本信息</div>
        <div class="form">
            <el-form :model="form" label-width="96px" class="profile-form">
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
    if (!store.state.user.userInfo.avatar) return;
    try {
      const response = await getAvatar(store.state.user.userInfo.avatar);
      if (response.data instanceof Blob) {
        imageUrl.value = URL.createObjectURL(response.data)
      }
    } catch (error) {
      console.warn('头像暂时无法加载', error);
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
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: auto;
    padding: 28px 32px;
    background: #f3f7fc;
    box-sizing: border-box;
}
.profile-heading { margin-bottom: 22px; }
.heading-kicker { color: #2171bb; font-size: 11px; font-weight: 700; letter-spacing: .12em; }
.profile-heading h1 { margin: 7px 0 6px; color: #15395d; font-size: 24px; line-height: 1.25; }
.profile-heading p { margin: 0; color: #6d8197; font-size: 13px; }
.profile-content {
    display: grid;
    grid-template-columns: minmax(260px, 32%) minmax(0, 1fr);
    align-items: stretch;
    gap: 16px;
    min-height: 540px;
}
.section-caption { color: #15395d; font-size: 16px; font-weight: 700; margin-bottom: 24px; }
.aside, .main {
    border: 1px solid #dbe6f2;
    border-radius: 12px;
    background: #fff;
    box-shadow: 0 8px 28px rgba(22, 67, 110, .045);
    padding: 24px;
    box-sizing: border-box;
}
.aside {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.user-avatar {
    width: 208px;
    height: 208px;
    border-radius: 50%;
    overflow: hidden;
    box-shadow: 0 0 0 8px #edf5fc;
    margin: 28px 0 24px;
}
.avatar-hint { color: #8294a7; font-size: 12px; text-align: center; line-height: 1.6; }
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
  width: 208px;
  height: 208px;
  text-align: center;
  background-color: #adb0b5;
}
.main {
    flex: 1;
}
.avatar{
    height: 208px;
    width: 208px;
    object-fit: cover; /* 让图片按照比例填充 */
}
.main {
    min-width: 0;
}
.form {
    width: 100%;
    max-width: 620px;
}
.profile-form { width: 100%; }
.profile-form :deep(.el-form-item) { margin-bottom: 22px; }
.profile-form :deep(.el-input__wrapper), .profile-form :deep(.el-select__wrapper) { min-height: 38px; }
@media (max-width: 800px) {
    .user { padding: 18px; }
    .profile-content { grid-template-columns: 1fr; }
}
</style>
