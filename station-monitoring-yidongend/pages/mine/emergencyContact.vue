<template>
  <view class="emergency-contact-container">
    <!-- 顶部提示 -->
    <view class="top-tips">
      <uv-icon name="info-circle-fill" size="16" color="#6467D2"></uv-icon>
      <text class="tip-text">紧急联系人将在您健康异常时收到通知</text>
    </view>

    <!-- 紧急联系人列表 -->
    <view class="contact-list" v-if="contacts.length > 0">
      <view class="section-title">
        <text>紧急联系人 ({{ contacts.length }}/{{ maxContacts }})</text>
        <text class="add-btn" @click="showAddModal" v-if="contacts.length < maxContacts">
          <uv-icon name="plus" size="14" color="#6467D2"></uv-icon>
          添加
        </text>
      </view>

      <view class="contacts-container">
        <view
            v-for="(contact, index) in contacts"
            :key="contact.id || index"
            class="contact-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <view class="contact-header">
            <view class="contact-avatar" :style="{ backgroundColor: getAvatarColor(contact.name) }">
              <text class="avatar-text">{{ getAvatarText(contact.name) }}</text>
              <view v-if="contact.isPrimary" class="primary-badge">
                <uv-icon name="star-fill" size="8" color="#fff"></uv-icon>
              </view>
            </view>
            <view class="contact-info">
              <view class="name-row">
                <text class="contact-name">{{ contact.name }}</text>
                <text v-if="contact.relationship" class="relationship">{{ contact.relationship }}</text>
              </view>
              <text class="contact-phone">{{ formatPhone(contact.phone) }}</text>
              <text v-if="contact.email" class="contact-email">{{ contact.email }}</text>
            </view>
          </view>

          <view class="contact-actions">
            <view class="action-btn" @click="setAsPrimary(contact)" v-if="!contact.isPrimary">
              <uv-icon name="star" size="14" color="#FFC107"></uv-icon>
              <text>设为主联系人</text>
            </view>
            <view class="action-btn" @click="editContact(contact)">
              <uv-icon name="edit-pen" size="14" color="#6467D2"></uv-icon>
              <text>编辑</text>
            </view>
            <view class="action-btn delete-btn" @click="showDeleteConfirm(contact)">
              <uv-icon name="trash" size="14" color="#FF6B6B"></uv-icon>
              <text>删除</text>
            </view>
          </view>

          <view class="notification-settings" v-if="contact.isPrimary">
            <view class="setting-item">
              <text class="setting-label">接收通知类型：</text>
              <text class="setting-value">{{ getNotificationTypes(contact) }}</text>
            </view>
            <view class="setting-item">
              <text class="setting-label">通知方式：</text>
              <text class="setting-value">{{ getNotificationMethods(contact) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <image class="empty-icon" src="/static/images/emergency-contact.png" mode="aspectFit"></image>
      <text class="empty-title">暂无紧急联系人</text>
      <text class="empty-desc">添加紧急联系人，在您健康异常时将自动通知他们</text>
      <button class="add-first-btn" @click="showAddModal">添加第一个联系人</button>
    </view>

    <!-- 添加/编辑联系人模态框 -->
    <uv-modal ref="contactModal" :title="modalTitle" :showConfirmButton="false">
      <view class="modal-content">
        <uv-form :model="contactForm" :rules="formRules" ref="formRef" labelPosition="left">
          <uv-form-item label="姓名" prop="name" labelWidth="80">
            <uv-input
                v-model="contactForm.name"
                placeholder="请输入联系人姓名"
                border="none"
                :customStyle="{ background: '#f5f7ff', borderRadius: '8px', padding: '8px 12px' }"
            ></uv-input>
          </uv-form-item>

          <uv-form-item label="关系" prop="relationship" labelWidth="80">
            <uv-input
                v-model="contactForm.relationship"
                placeholder="如：家人、朋友、医生等"
                border="none"
                :customStyle="{ background: '#f5f7ff', borderRadius: '8px', padding: '8px 12px' }"
            ></uv-input>
          </uv-form-item>

          <uv-form-item label="手机号" prop="phone" labelWidth="80">
            <uv-input
                v-model="contactForm.phone"
                placeholder="请输入11位手机号码"
                type="number"
                maxlength="11"
                border="none"
                :customStyle="{ background: '#f5f7ff', borderRadius: '8px', padding: '8px 12px' }"
            ></uv-input>
          </uv-form-item>

          <uv-form-item label="邮箱" labelWidth="80">
            <uv-input
                v-model="contactForm.email"
                placeholder="选填，用于邮件通知"
                border="none"
                :customStyle="{ background: '#f5f7ff', borderRadius: '8px', padding: '8px 12px' }"
            ></uv-input>
          </uv-form-item>

          <!-- 通知设置 -->
          <view class="form-section">
            <text class="section-label">通知设置</text>

            <view class="checkbox-group">
              <text class="checkbox-label">通知类型：</text>
              <view class="checkboxes">
                <view
                    v-for="type in notificationTypes"
                    :key="type.value"
                    class="checkbox-item"
                    @click="toggleNotificationType(type.value)"
                >
                  <view class="checkbox" :class="{ checked: contactForm.notificationTypes.includes(type.value) }">
                    <uv-icon v-if="contactForm.notificationTypes.includes(type.value)"
                             name="checkmark" size="10" color="#fff"></uv-icon>
                  </view>
                  <text class="checkbox-text">{{ type.label }}</text>
                </view>
              </view>
            </view>

            <view class="checkbox-group">
              <text class="checkbox-label">通知方式：</text>
              <view class="checkboxes">
                <view
                    v-for="method in notificationMethods"
                    :key="method.value"
                    class="checkbox-item"
                    @click="toggleNotificationMethod(method.value)"
                >
                  <view class="checkbox" :class="{ checked: contactForm.notificationMethods.includes(method.value) }">
                    <uv-icon v-if="contactForm.notificationMethods.includes(method.value)"
                             name="checkmark" size="10" color="#fff"></uv-icon>
                  </view>
                  <text class="checkbox-text">{{ method.label }}</text>
                </view>
              </view>
            </view>
          </view>

          <view class="modal-actions">
            <button class="cancel-btn" @click="closeModal">取消</button>
            <button class="confirm-btn" @click="saveContact">{{ isEditing ? '更新' : '添加' }}</button>
          </view>
        </uv-form>
      </view>
    </uv-modal>

    <!-- 删除确认 -->
    <uv-modal
        ref="deleteModal"
        title="删除联系人"
        content="确定要删除该紧急联系人吗？"
        confirmColor="#FF6B6B"
        showCancelButton
        @confirm="confirmDelete"
    ></uv-modal>

<!--    &lt;!&ndash; 底部提示 &ndash;&gt;-->
<!--    <view class="bottom-tips">-->
<!--      <uv-icon name="shield-check-fill" size="14" color="#5BCEBD"></uv-icon>-->
<!--      <text class="tip-text">紧急联系人信息将加密存储，保障您的隐私安全</text>-->
<!--    </view>-->
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const contactModal = ref(null);
const deleteModal = ref(null);
const formRef = ref(null);

// 数据
const contacts = ref([]);
const contactForm = ref({
  id: null,
  name: '',
  relationship: '',
  phone: '',
  email: '',
  notificationTypes: ['emergency', 'abnormal'], // 默认通知类型
  notificationMethods: ['sms', 'call'] // 默认通知方式
});
const isEditing = ref(false);
const contactToDelete = ref(null);

// 常量
const maxContacts = 5;
const notificationTypes = [
  { label: '紧急警报', value: 'emergency', icon: 'alert' },
  { label: '数据异常', value: 'abnormal', icon: 'chart' },
  { label: '每日报告', value: 'daily', icon: 'calendar' },
  { label: '健康建议', value: 'advice', icon: 'heart' }
];
const notificationMethods = [
  { label: '短信通知', value: 'sms', icon: 'message' },
  { label: '电话呼叫', value: 'call', icon: 'phone' },
  { label: '邮件通知', value: 'email', icon: 'email' }
];

// 计算属性
const modalTitle = computed(() => {
  return isEditing.value ? '编辑紧急联系人' : '添加紧急联系人';
});

// 验证规则
const formRules = {
  name: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度2-10个字', trigger: 'blur' }
  ],
  relationship: [
    { required: true, message: '请输入关系', trigger: 'blur' },
    { min: 2, max: 10, message: '关系长度2-10个字', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    // {
    //   validator: (rule, value, callback) => {
    //     if (!/^1[3-9]\d{9}$/.test(value)) {
    //       callback(new Error('请输入正确的手机号'));
    //     } else {
    //       callback();
    //     }
    //   },
    //   trigger: 'blur'
    // }
  ]
};

// 生命周期
onMounted(() => {
  loadContacts();
});

// 方法
async function loadContacts() {
  // 模拟加载数据，实际应调用API
  contacts.value = [
    {
      id: 1,
      name: '张医生',
      relationship: '家庭医生',
      phone: '13800138000',
      email: 'doctor@hospital.com',
      isPrimary: true,
      notificationTypes: ['emergency', 'abnormal'],
      notificationMethods: ['sms', 'call', 'email']
    },
    {
      id: 2,
      name: '李女士',
      relationship: '家人',
      phone: '13900139000',
      email: 'family@example.com',
      isPrimary: false,
      notificationTypes: ['emergency'],
      notificationMethods: ['sms', 'call']
    }
  ];
}

function showAddModal() {
  isEditing.value = false;
  resetForm();
  contactModal.value.open();
}

function editContact(contact) {
  isEditing.value = true;
  contactForm.value = {
    id: contact.id,
    name: contact.name,
    relationship: contact.relationship,
    phone: contact.phone,
    email: contact.email || '',
    notificationTypes: [...contact.notificationTypes],
    notificationMethods: [...contact.notificationMethods]
  };
  contactModal.value.open();
}

function resetForm() {
  contactForm.value = {
    id: null,
    name: '',
    relationship: '',
    phone: '',
    email: '',
    notificationTypes: ['emergency', 'abnormal'],
    notificationMethods: ['sms', 'call']
  };
}

async function saveContact() {
  try {
    await formRef.value.validate();

    // 模拟API调用
    if (isEditing.value) {
      // 更新联系人
      const index = contacts.value.findIndex(c => c.id === contactForm.value.id);
      if (index !== -1) {
        contacts.value[index] = {
          ...contacts.value[index],
          ...contactForm.value
        };
        uni.showToast({ title: '更新成功', icon: 'success' });
      }
    } else {
      // 添加联系人
      const newContact = {
        id: Date.now(),
        ...contactForm.value,
        isPrimary: contacts.value.length === 0 // 第一个联系人设为主联系人
      };
      contacts.value.unshift(newContact);
      uni.showToast({ title: '添加成功', icon: 'success' });
    }

    closeModal();
  } catch (error) {
    console.error('表单验证失败:', error);
  }
}

function setAsPrimary(contact) {
  contacts.value.forEach(c => {
    c.isPrimary = c.id === contact.id;
  });
  uni.showToast({ title: '已设为主联系人', icon: 'success' });
}

function showDeleteConfirm(contact) {
  contactToDelete.value = contact;
  deleteModal.value.open();
}

function confirmDelete() {
  if (contactToDelete.value) {
    contacts.value = contacts.value.filter(c => c.id !== contactToDelete.value.id);

    // 如果删除的是主联系人，自动设置第一个为主联系人
    if (contactToDelete.value.isPrimary && contacts.value.length > 0) {
      contacts.value[0].isPrimary = true;
    }

    contactToDelete.value = null;
    uni.showToast({ title: '删除成功', icon: 'success' });
  }
}

function closeModal() {
  contactModal.value.close();
  resetForm();
}

// 工具方法
function getAvatarColor(name) {
  const colors = ['#6467D2', '#5BCEBD', '#FF724B', '#FB1374', '#FFC107'];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

function getAvatarText(name) {
  return name.length >= 2 ? name.substring(0, 2) : name;
}

function formatPhone(phone) {
  return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3');
}

function toggleNotificationType(type) {
  const index = contactForm.value.notificationTypes.indexOf(type);
  if (index > -1) {
    contactForm.value.notificationTypes.splice(index, 1);
  } else {
    contactForm.value.notificationTypes.push(type);
  }
}

function toggleNotificationMethod(method) {
  const index = contactForm.value.notificationMethods.indexOf(method);
  if (index > -1) {
    contactForm.value.notificationMethods.splice(index, 1);
  } else {
    contactForm.value.notificationMethods.push(method);
  }
}

function getNotificationTypes(contact) {
  const typeNames = {
    emergency: '紧急警报',
    abnormal: '数据异常',
    daily: '每日报告',
    advice: '健康建议'
  };
  return contact.notificationTypes.map(t => typeNames[t] || t).join('、');
}

function getNotificationMethods(contact) {
  const methodNames = {
    sms: '短信',
    call: '电话',
    email: '邮件'
  };
  return contact.notificationMethods.map(m => methodNames[m] || m).join('、');
}
</script>

<style lang="scss" scoped>
.emergency-contact-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9fe 0%, #ffffff 100%);
  padding: 16px;
}

// 顶部提示
.top-tips {
  background: rgba(100, 103, 210, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;

  .tip-text {
    font-size: 12px;
    color: #6467D2;
    flex: 1;
  }
}

// 列表标题
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  text {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .add-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #6467D2;
    padding: 4px 10px;
    border-radius: 12px;
    background: rgba(100, 103, 210, 0.1);
  }
}

// 联系人卡片
.contacts-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.03);
  animation: slideIn 0.3s ease forwards;
  opacity: 0;
  transform: translateY(10px);

  .contact-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;

    .contact-avatar {
      width: 48px;
      height: 48px;
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      position: relative;

      .avatar-text {
        color: #fff;
        font-size: 16px;
        font-weight: 600;
      }

      .primary-badge {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 16px;
        height: 16px;
        border-radius: 8px;
        background: #FFC107;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #fff;
      }
    }

    .contact-info {
      flex: 1;

      .name-row {
        display: flex;
        align-items: center;
        margin-bottom: 4px;

        .contact-name {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-right: 8px;
        }

        .relationship {
          font-size: 10px;
          color: #6467D2;
          padding: 2px 6px;
          background: rgba(100, 103, 210, 0.1);
          border-radius: 8px;
        }
      }

      .contact-phone {
        display: block;
        font-size: 14px;
        color: #666;
        margin-bottom: 2px;
      }

      .contact-email {
        display: block;
        font-size: 12px;
        color: #999;
      }
    }
  }

  .contact-actions {
    display: flex;
    justify-content: flex-end;
    gap: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: #909399;
      padding: 4px 8px;
      border-radius: 8px;

      &:active {
        background: rgba(0, 0, 0, 0.05);
      }

      &.delete-btn {
        color: #FF6B6B;
      }
    }
  }

  .notification-settings {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px dashed #f0f0f0;

    .setting-item {
      display: flex;
      margin-bottom: 8px;

      .setting-label {
        font-size: 12px;
        color: #909399;
        min-width: 80px;
      }

      .setting-value {
        font-size: 12px;
        color: #666;
        flex: 1;
      }
    }
  }
}

// 空状态
.empty-state {
  text-align: center;
  padding: 60px 20px;

  .empty-icon {
    width: 120px;
    height: 120px;
    margin-bottom: 24px;
  }

  .empty-title {
    display: block;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .empty-desc {
    display: block;
    font-size: 13px;
    color: #909399;
    line-height: 1.5;
    margin-bottom: 32px;
  }

  .add-first-btn {
    background: linear-gradient(135deg, #6467D2 0%, #8E91FF 100%);
    color: #fff;
    border: none;
    height: 48px;
    border-radius: 24px;
    font-size: 15px;
    font-weight: 600;
    width: 200px;
  }
}

// 模态框内容
.modal-content {
  padding: 0 16px;

  .form-section {
    margin: 20px 0;

    .section-label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 12px;
    }

    .checkbox-group {
      margin-bottom: 16px;

      .checkbox-label {
        display: block;
        font-size: 12px;
        color: #666;
        margin-bottom: 8px;
      }

      .checkboxes {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;

        .checkbox-item {
          display: flex;
          align-items: center;
          gap: 6px;

          .checkbox {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #DCDFE6;
            display: flex;
            align-items: center;
            justify-content: center;

            &.checked {
              background: #6467D2;
              border-color: #6467D2;
            }
          }

          .checkbox-text {
            font-size: 12px;
            color: #303133;
          }
        }
      }
    }
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    padding: 20px 0;

    .cancel-btn {
      flex: 1;
      background: #f5f7ff;
      color: #6467D2;
      border: none;
      height: 44px;
      border-radius: 22px;
      font-size: 15px;
      font-weight: 600;
    }

    .confirm-btn {
      flex: 1;
      background: linear-gradient(135deg, #6467D2 0%, #8E91FF 100%);
      color: #fff;
      border: none;
      height: 44px;
      border-radius: 22px;
      font-size: 15px;
      font-weight: 600;
    }
  }
}

// 底部提示
.bottom-tips {
  margin-top: 30px;
  padding: 12px 16px;
  background: rgba(91, 206, 189, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;

  .tip-text {
    font-size: 11px;
    color: #5BCEBD;
    flex: 1;
  }
}

// 动画
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 每个卡片延迟
.contact-card {
  @for $i from 1 through 5 {
    &:nth-child(#{$i}) {
      animation-delay: #{$i * 0.1}s;
    }
  }
}
</style>