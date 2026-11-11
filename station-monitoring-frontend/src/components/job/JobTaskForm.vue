<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑任务' : '创建新任务'"
    width="50%"
    destroy-on-close
  >
    <el-form 
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="任务标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入任务标题" />
      </el-form-item>

      <el-form-item label="任务描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          rows="4"
          placeholder="请输入任务描述" 
        />
      </el-form-item>

      <el-form-item label="任务类型" prop="type">
        <el-select v-model="form.type" placeholder="请选择任务类型">
          <el-option label="维护" value="维护" />
          <el-option label="安装" value="安装" />
          <el-option label="检查" value="检查" />
          <el-option label="配置" value="配置" />
        </el-select>
      </el-form-item>

      <el-form-item label="优先级" prop="priority">
        <el-select v-model="form.priority" placeholder="请选择优先级">
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
      </el-form-item>

      <el-form-item label="指派给" prop="assignedTo">
        <el-select 
          v-model="form.assignedTo"
          placeholder="请选择任务执行人员"
          filterable
        >
          <el-option 
            v-for="employee in employees" 
            :key="employee.id" 
            :label="employee.name" 
            :value="employee.id" 
          />
        </el-select>
      </el-form-item>

      <el-form-item label="截止日期" prop="dueDate">
        <el-date-picker 
          v-model="form.dueDate" 
          type="datetime" 
          placeholder="选择截止日期时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';

// 属性定义
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  task: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  employees: {
    type: Array,
    default: () => []
  }
});

// 事件定义
const emit = defineEmits(['close', 'submit']);

// 表单引用
const formRef = ref(null);
const dialogVisible = ref(props.visible);
const submitting = ref(false);

// 表单数据
const form = reactive({
  id: null,
  title: '',
  description: '',
  type: '',
  priority: 'medium',
  assignedTo: null,
  dueDate: null
});

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入任务描述', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  assignedTo: [
    { required: true, message: '请选择任务执行人员', trigger: 'change' }
  ],
  dueDate: [
    { required: true, message: '请选择截止日期', trigger: 'change' }
  ]
};

// 重置表单
const resetForm = () => {
  Object.keys(form).forEach(key => {
    form[key] = key === 'priority' ? 'medium' : null;
  });
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

// 监听任务数据变化
watch(() => props.task, (newTask) => {
  if (newTask) {
    Object.keys(form).forEach(key => {
      if (key in newTask) {
        form[key] = newTask[key];
      }
    });
  } else {
    resetForm();
  }
}, { immediate: true });

// 监听对话框可见性
watch(() => props.visible, (val) => {
  dialogVisible.value = val;
}, { immediate: true });

// 监听内部对话框可见性
watch(dialogVisible, (val) => {
  if (!val) {
    emit('close');
  }
});

// 取消操作
const handleCancel = () => {
  dialogVisible.value = false;
};

// 提交表单
const handleSubmit = () => {
  if (!formRef.value) return;
  
  formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        // 如果有ID，说明是编辑模式，否则是创建模式
        const submitData = { ...form };
        emit('submit', submitData);
      } finally {
        submitting.value = false;
      }
    }
  });
};
</script>

<style scoped>
.el-select {
  width: 100%;
}
</style> 