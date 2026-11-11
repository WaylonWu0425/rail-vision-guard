<template>
  <div class="list">
    <header class="ops-page-header"><div><span class="ops-eyebrow">USER ADMINISTRATION / 权限管理</span><h1>用户管理</h1><p>查看用户状态并维护系统使用权限。</p></div></header>
    <div class="search">
      <div class="search-box">
        <el-form-item label="用户账号" :label-width="formLabelWidth">
          <el-select-v2
              v-model="searchKey.id"
              filterable
              :options="userList"
              placeholder="请输入"
              style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="股道" :label-width="formLabelWidth">
          <el-input v-model="searchKey.trackId" style="width: 100%" placeholder="请输入"/>
        </el-form-item>
        <div class="search-btn">
          <el-button round @click="search">搜索</el-button>
        </div>
      </div>
    </div>
    <div class="camera-list">
      <el-table :data="userInfo" style="width: 100%; height: 540px;">
        <el-table-column fixed prop="id" label="序号" min-width="5%">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" align="center" min-width="10%"/>
        <el-table-column prop="account" label="账户" align="center" min-width="10%"/>
        <el-table-column prop="email" label="邮箱" align="center" min-width="10%"/>
        <el-table-column prop="sex" label="性别" align="center" min-width="10%">
          <template #default="{ row }">
                        <span v-if="row.sex !== null && row.sex !== undefined">
                            {{ row.sex == 0 ? '女' : '男' }}
                        </span>
          </template>
        </el-table-column>
        <el-table-column prop="state" label="账号状态" align="center" min-width="10%">
          <template #default="{ row }">
            <el-tag :type="row.state == 0 ? 'success' : 'error'">
              {{ row.state == 0 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginTime" label="上次登录时间" align="center" min-width="10%"/>
        <el-table-column fixed="right" label="操作" align="center" min-width="12%">
          <template #default="{row}">
            <el-button link type="primary" size="middle" @click=editData(row)>
              <span v-if="row.state==0">禁用</span>
              <span v-if="row.state==1">解除禁用</span>
            </el-button>
            <el-button link type="primary" size="middle" @click=deleteData(row.id)>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="editForm">
      <el-dialog v-model="editFormVisible" width="500">
                <span :value="userState">
                    {{ userState == 0 ? '确认禁用?' : '确认解除禁用？' }}
                </span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="editFormVisible = false">取消</el-button>
            <el-button type="primary" @click=forbiddenUserById()>确认</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
    <div class="delete">
      <el-dialog v-model="deleteVisible" width="300" center>
        <span>确认删除？</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="deleteVisible = false">取消</el-button>
            <el-button type="primary" @click=deleteUserById()>确认</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {getAllUser, forbiddenUser, deleteUser, searchUser} from '@/http/api/user.js'

const formLabelWidth = '140px'
//编辑预置点
const editFormVisible = ref(false)
const editForm = ref('')
const userState = ref()
const editData = (row) => {
  editFormVisible.value = true;
  editForm.value = row.id;
  userState.value = row.state;
}
const forbiddenUserById = async () => {
  try {
    const response = await forbiddenUser(editForm.value);
    if (response.data.success) {
      editFormVisible.value = false;
      fetchUsers();
      ElMessage({
        message: '操作成功',
        type: 'success',
        plain: true,
      })
    }
  } catch (error) {
    ElMessage({
      message: '操作失败',
      type: 'error',
      plain: true,
    })
    console.log('修改失败:', error);
  }
}
//删除预置点
const deleteVisible = ref(false)
const deleteId = ref("")
const deleteData = (id) => {
  deleteId.value = id;
  deleteVisible.value = true;
}
const deleteUserById = async () => {
  try {
    const response = await deleteUser(deleteId.value);
    if (response.data.success) {
      ElMessage({
        message: '删除成功',
        type: 'success',
        plain: true,
      })
      deleteVisible.value = false;
      fetchUsers();
    }
  } catch (error) {
    ElMessage({
      message: '删除成功',
      type: 'success',
      plain: true,
    })
    console.log('预置点信息删除该失败:', error);
  }
}
//获取用户信息
const userList = reactive([])
const userInfo = reactive([])
const fetchUsers = async () => {
  try {
    const response = await getAllUser();
    userInfo.splice(0, userInfo.length, ...response.data.data);
    userList.splice(0, userList.length, ...response.data.data.map(user => ({
      label: user.username,
      value: user.id,
    })));
    console.log(userList);

  } catch (error) {
    console.error('获取列表失败:', error);
  }
}
//搜索
const searchKey = reactive({
  id: '',
})
const search = async () => {
  try {
    const response = await searchUser(searchKey.id);
    userInfo.splice(0, userInfo.length, ...response.data.data);
  } catch (error) {
    console.error("搜索失败：", error);
  }
}

onMounted(() => {
  fetchUsers();
})


</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.search {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 98%;
  height: 12%;
  margin: 1%;
  padding: 0 2% 0 2%;
  background-color: #fff;
}

.search-box {
  display: flex;
}

.search-btn {
  margin-left: 4%;
}

.camera-list {
  height: 86%;
  width: 98%;
  margin: 0 1% 1% 1%;
  background-color: #fff;
}

.ops-page-header { flex:0 0 auto;min-height:80px;margin-bottom:12px;padding:6px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.4px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:24px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }

.list { min-height:0;padding:16px;gap:12px;background:#f2f7fb; }
.search { flex:0 0 auto;width:100%;height:auto;min-height:66px;margin:0;padding:12px 16px;border-left:3px solid #54afcf;border-radius:5px;background:#fff; }
.camera-list { flex:1;min-height:0;overflow:auto;margin:0;padding:0;background:#fff;border-top:2px solid #58b5d2;border-radius:8px;box-shadow:0 8px 30px rgba(21,63,99,.05); }
.camera-list :deep(.el-table) { --el-table-header-bg-color:#edf5fa;--el-table-row-hover-bg-color:#f0f8fb; }
</style>