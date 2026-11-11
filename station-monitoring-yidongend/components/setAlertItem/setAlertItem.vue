<template>
  <view class="container">
    <view class="warning">
      <view class="header">
        <text class="title">{{ label }}预警</text>
        <switch
            :checked="modelValue.enabled"
            @change="toggleWarning"
            class="switch"
        />
      </view>

      <view :class="modelValue.enabled ? 'settings active' : 'settings'">
        <view class="setting-item" v-for="(setting, index) in modelValue.settings" :key="index">
          <text class="label">{{ setting.label }}</text>
          <input
              v-model.number="modelValue.settings[index].value"
              @input="updateSetting(index, $event.detail.value)"
              type="number"
              class="input"
          />
          <text>{{ setting.unit }}</text>
        </view>
        <view class="setting-item">
          <text class="label">预警时段</text>
          <radio-group @change="radioChange">
            <radio class="radio" value="false" :checked="isCustom === 'false'">08时 - 当日22时</radio>
            <radio class="radio" value="true" :checked="isCustom === 'true'">自定义时段</radio>
            <view v-if="isCustom=='true'" class="custom-period">
              <picker mode="time" :value="start" start="00:00" end="23:59" @change="updateCustomStart">
                <view class="picker">{{ start }}</view>
              </picker>
              <text>-</text>
              <picker mode="time" :value="end" start="00:00" end="23:59" @change="updateCustomEnd">
                <view class="picker">{{ end }}</view>
              </picker>
            </view>
          </radio-group>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { defineProps, defineEmits, ref, computed, watchEffect } from 'vue';

const props = defineProps({
  label: {
    type: String,
    default: '心率'
  },
  modelValue: {
    type: Object,
    required: true,
    // 增加默认值校验
    validator: (val) => {
      return val && typeof val === 'object' && ('enabled' in val) && ('settings' in val);
    }
  }
});

const emits = defineEmits(['update:modelValue']);

// 初始化时段（从父组件取值，无则用默认）
let start = ref(props.modelValue.warningPeriod?.split('-')[0] || '08:00')
let end = ref(props.modelValue.warningPeriod?.split('-')[1] || '22:00')
let isCustom = ref(props.modelValue.warningPeriod && props.modelValue.warningPeriod !== '08:00-22:00' ? 'true' : 'false')

let customTime = computed(() => {
  return start.value + '-' + end.value
})

// 监听父组件值变化，同步时段
watchEffect(() => {
  if (props.modelValue.warningPeriod) {
    const [s, e] = props.modelValue.warningPeriod.split('-');
    if (s) start.value = s;
    if (e) end.value = e;
    isCustom.value = props.modelValue.warningPeriod !== '08:00-22:00' ? 'true' : 'false';
  }
});

const toggleWarning = () => {
  emits('update:modelValue', {
    ...props.modelValue,
    enabled: !props.modelValue.enabled
  });
};

const updateSetting = (index, value) => {
  // 确保值为数字
  const numValue = Number(value) || 0;
  const newSettings = [...props.modelValue.settings];
  newSettings[index].value = numValue;
  emits('update:modelValue', {
    ...props.modelValue,
    settings: newSettings
  });
};

const updateCustomStart = (e) => {
  start.value = e.detail.value;
  emits('update:modelValue', {
    ...props.modelValue,
    warningPeriod: customTime.value
  });
};

const updateCustomEnd = (e) => {
  end.value = e.detail.value;
  emits('update:modelValue', {
    ...props.modelValue,
    warningPeriod: customTime.value
  });
};

const radioChange = (e) => {
  isCustom.value = e.detail.value;
  // 切换回默认时段时重置值
  if (e.detail.value === 'false') {
    start.value = '08:00';
    end.value = '22:00';
    emits('update:modelValue', {
      ...props.modelValue,
      warningPeriod: '08:00-22:00'
    });
  }
};
</script>

<style scoped>
.container {
  padding: 10px;
}

.warning {
  background-color: #fff;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.switch {
  margin-left: 10px;
}

.settings {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  margin-top: 10px;
  overflow: hidden;
  height: 0;
  opacity: 0;
  transition: all 0.3s ease;
}

.active {
  height: auto; /* 改为auto，适配内容高度 */
  min-height: 280px;
  opacity: 1;
  padding-top: 10px;
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.label {
  flex: 1;
  font-size: 16px;
}

.input {
  width: 60px;
  margin-left: 10px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: center;
}

.radio {
  display: block;
  margin-top: 10px;
}

.custom-period {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.picker {
  margin: 0 5px;
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  min-width: 60px;
  text-align: center;
}
</style>