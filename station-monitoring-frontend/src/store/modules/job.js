// 作业任务管理的Vuex模块

const state = {
  // 任务列表
  tasks: [],
  // 任务类型列表
  taskTypes: ['常规巡检', '设备维护', '故障处理', '数据采集', '系统升级'],
  // 任务状态列表
  taskStatuses: ['待分配', '进行中', '暂停中', '已完成', '审核通过', '审核不通过'],
  // 当前任务状态
  currentTask: null,
  // 任务统计信息
  statistics: {
    completed: 0,
    pending: 0,
    inProgress: 0,
    rejected: 0
  }
};

const getters = {
  // 获取所有任务
  getTasks: state => state.tasks,
  
  // 根据任务ID获取任务
  getTaskById: state => id => state.tasks.find(task => task.id === id),
  
  // 根据任务分配人获取任务
  getTasksByAssignee: state => assigneeId => state.tasks.filter(task => task.assignee === assigneeId),
  
  // 根据状态获取任务
  getTasksByStatus: state => status => state.tasks.filter(task => task.status === status),
  
  // 根据任务类型获取任务
  getTasksByType: state => type => state.tasks.filter(task => task.type === type),
  
  // 获取任务类型列表
  getTaskTypes: state => state.taskTypes,
  
  // 获取任务状态列表
  getTaskStatuses: state => state.taskStatuses,
  
  // 获取任务统计信息
  getTaskStatistics: (state) => state.statistics,
  
  // 获取当前选中的任务
  getCurrentTask: (state) => state.currentTask
};

const mutations = {
  // 设置所有任务
  setTasks(state, tasks) {
    state.tasks = tasks;
    updateStatistics(state);
  },
  
  // 添加新任务
  addTask(state, task) {
    state.tasks.push(task);
    updateStatistics(state);
  },
  
  // 更新任务
  updateTask(state, updatedTask) {
    const index = state.tasks.findIndex(task => task.id === updatedTask.id);
    if (index !== -1) {
      state.tasks.splice(index, 1, updatedTask);
      updateStatistics(state);
    }
  },
  
  // 删除任务
  deleteTask(state, taskId) {
    state.tasks = state.tasks.filter(task => task.id !== taskId);
    updateStatistics(state);
  },
  
  // 设置当前任务
  SET_CURRENT_TASK(state, task) {
    state.currentTask = task;
  },
  
  // 更新任务状态
  updateTaskStatus(state, { taskId, status, feedback }) {
    const task = state.tasks.find(task => task.id === taskId);
    if (task) {
      task.status = status;
      if (feedback) {
        task.feedback = feedback;
      }
      if (status === '进行中' && !task.startTime) {
        task.startTime = new Date().toISOString();
      } else if (status === '已完成' && !task.endTime) {
        task.endTime = new Date().toISOString();
      }
      updateStatistics(state);
    }
  }
};

const actions = {
  // 获取所有任务
  fetchTasks({ commit }) {
    // 在实际应用中，这里应该从API获取任务列表
    // 这里使用模拟数据
    const mockTasks = [
      {
        id: 1,
        title: '监控设备日常检查',
        description: '检查所有监控设备是否正常运行',
        type: '常规巡检',
        status: '进行中',
        priority: '高',
        assignee: 101,
        assigneeName: '张工',
        createdBy: 1,
        createdByName: '系统管理员',
        createdAt: '2023-12-01T08:00:00Z',
        startTime: '2023-12-01T09:00:00Z',
        endTime: null,
        feedback: ''
      },
      {
        id: 2,
        title: '摄像头维修',
        description: '3号区域摄像头信号异常，需要进行检修',
        type: '故障处理',
        status: '已完成',
        priority: '紧急',
        assignee: 102,
        assigneeName: '李工',
        createdBy: 1,
        createdByName: '系统管理员',
        createdAt: '2023-12-02T10:30:00Z',
        startTime: '2023-12-02T11:00:00Z',
        endTime: '2023-12-02T14:00:00Z',
        feedback: '已更换信号线，设备恢复正常'
      }
    ];
    commit('setTasks', mockTasks);
  },
  
  // 创建新任务
  createTask({ commit }, taskData) {
    // 在实际应用中，这里应该调用API创建任务
    const newTask = {
      ...taskData,
      id: Date.now(), // 模拟ID生成
      createdAt: new Date().toISOString(),
      status: '待分配'
    };
    commit('addTask', newTask);
    return newTask;
  },
  
  // 分配任务
  assignTask({ commit, state }, { taskId, assigneeId, assigneeName }) {
    const task = state.tasks.find(task => task.id === taskId);
    if (task) {
      const updatedTask = {
        ...task,
        assignee: assigneeId,
        assigneeName,
        status: '进行中'
      };
      commit('updateTask', updatedTask);
      return updatedTask;
    }
    return null;
  },
  
  // 审核任务
  reviewTask({ commit, state }, { taskId, approved, feedback }) {
    const task = state.tasks.find(task => task.id === taskId);
    if (task) {
      const updatedTask = {
        ...task,
        status: approved ? '审核通过' : '审核不通过',
        feedback
      };
      commit('updateTask', updatedTask);
      return updatedTask;
    }
    return null;
  },
  
  // 更新任务状态
  updateTaskStatus({ commit }, payload) {
    commit('updateTaskStatus', payload);
  }
};

// 辅助函数：更新任务统计信息
function updateStatistics(state) {
  state.statistics = {
    completed: state.tasks.filter(task => task.status === '已完成').length,
    pending: state.tasks.filter(task => task.status === '待分配').length,
    inProgress: state.tasks.filter(task => task.status === '进行中').length,
    rejected: state.tasks.filter(task => task.status === '审核不通过').length
  };
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 