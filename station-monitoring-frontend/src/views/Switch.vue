<template>
    <div class="list">
    <header class="ops-page-header"><div><span class="ops-eyebrow">SWITCH PRESETS / 站场配置</span><h1>道岔预置点</h1><p>查看场别、股道与道岔预置点。</p></div></header>
        <div class="search">
            <div class="search-box">
                <div>
                    <el-form-item label="场别" :label-width="formLabelWidth">
                        <el-input v-model="searchKey.field" style="width: 100%" placeholder="请输入" />
                    </el-form-item>
                </div>
                <div>
                    <el-form-item label="股道" :label-width="formLabelWidth">
                        <el-input v-model="searchKey.trackId" style="width: 100%" placeholder="请输入" />
                    </el-form-item>
                </div>
                <div>
                    <el-form-item label="咽喉" :label-width="formLabelWidth">
                        <el-select
                            v-model="searchKey.throat"
                            placeholder="请选择"
                            clearable
                            style="width: 120px;"
                        >
                            <el-option label="上" value="0" />
                            <el-option label="下" value="1" />
                        </el-select>
                    </el-form-item>
                </div>
                <div class="search-btn">
                    <el-button round @click="searchSwitch">搜索</el-button>
                </div>
            </div>
            <div class="add">
                <el-button round @click="addBtn">新增预置点</el-button>
            </div>
        </div>
        <div class="camera-list">
            <el-table :data="tableData" :border="parentBorder" >
                <el-table-column type="expand" >
                    <template #default="props">
                        <div class="presetPointTable">
                            <el-table :data="props.row.family" :border="childBorder" >
                                <el-table-column label="预置点ID" prop="id" align="center" min-width="50"/>
                                <el-table-column label="水平坐标" prop="panPosition" align="center" min-width="100"/>
                                <el-table-column label="垂直坐标" prop="tiltPosition" align="center" min-width="100"/>
                                <el-table-column label="变焦系数" prop="zoom" align="center" min-width="100"/>
                                <el-table-column label="道岔编号" prop="switchNumber" align="center" min-width="100"/>
                                <el-table-column fixed="right" label="操作" align="center" min-width="120">
                                    <template #default="{row: row2}">
                                        <el-button link type="primary" size="middle" @click=gotoPreset(row2)>转到预置点</el-button>
                                        <el-button link type="primary" size="middle" @click=editData(props.row,row2)>编辑</el-button>
                                        <el-button link type="primary" size="middle" @click=deleteData(props.row,row2)>删除</el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column label="场别" prop="field" />
                <el-table-column label="轨道ID" prop="trackId" />
                <el-table-column label="咽喉" prop="throat">
                    <template #default="{ row }">
                        <el-tag :type="row.throat === '0' ? 'success' : 'primary'">
                            {{ row.throat === '0' ? '上' : '下' }}
                        </el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </div>
        <div class="addForm">
            <el-dialog v-model="addFormVisible" title="添加预置点" width="500">
                <el-form :model="addForm">
                  <el-form-item label="场别" :label-width="formLabelWidth">
                      <el-input v-model="addSwitchForm.field" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="股道ID" :label-width="formLabelWidth">
                      <el-input v-model="addSwitchForm.trackId" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="咽喉" :label-width="formLabelWidth">
                    <el-select
                        v-model="addSwitchForm.throat"
                        placeholder="请选择"
                        clearable
                    >
                        <el-option label="上" value="0" />
                        <el-option label="下" value="1" />
                    </el-select>
                </el-form-item>
                  <el-form-item label="水平坐标" :label-width="formLabelWidth">
                      <el-input v-model="addSwitchPresetPointForm.panPosition" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="垂直坐标" :label-width="formLabelWidth">
                      <el-input v-model="addSwitchPresetPointForm.tiltPosition" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="变焦系数" :label-width="formLabelWidth">
                      <el-input v-model="addSwitchPresetPointForm.zoom" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="道岔编号" :label-width="formLabelWidth">
                    <div class="flex gap-2">
                        <el-tag
                            v-for="tag in listNumber"
                            :key="tag"
                            closable
                            :disable-transitions="false"
                            @close="handleClose(tag)"
                            style="margin-right: 5px;"
                        >
                        {{ tag }}
                        </el-tag>
                        <el-input
                            v-if="inputVisible"
                            ref="InputRef"
                            v-model="inputValue"
                            class="w-20"
                            size="small"
                            @keyup.enter="handleInputConfirm"
                            @blur="handleInputConfirm"
                            style="width: 100px;"
                        />
                        <el-button v-else class="button-new-tag" size="small" @click="showInput">
                            + 添加道岔编号
                        </el-button>
                    </div>
                  </el-form-item>

                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                      <el-button @click="addFormVisible = false">取消</el-button>
                      <el-button type="primary" @click=addPresetPoint()>确认</el-button>
                  </div>
                </template>
            </el-dialog>
        </div>

        <div class="editForm">
            <el-dialog v-model="editFormVisible" title="编辑预置点" width="500">
                <el-form :model="addForm">
                  <el-form-item label="水平坐标" :label-width="formLabelWidth">
                      <el-input v-model="editForm.panPosition" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="垂直坐标" :label-width="formLabelWidth">
                      <el-input v-model="editForm.tiltPosition" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="变焦系数" :label-width="formLabelWidth">
                      <el-input v-model="editForm.zoom" autocomplete="off" />
                  </el-form-item>
                  <el-form-item label="道岔编号" :label-width="formLabelWidth">
                    <div class="flex gap-2">
                        <el-tag
                            v-for="tag in listNumber"
                            :key="tag"
                            closable
                            :disable-transitions="false"
                            @close="handleClose(tag)"
                            style="margin-right: 5px;"
                        >
                        {{ tag }}
                        </el-tag>
                        <el-input
                            v-if="inputVisible"
                            ref="InputRef"
                            v-model="inputValue"
                            class="w-20"
                            size="small"
                            style="width: 100px;"
                            @keyup.enter="handleInputConfirm"
                            @blur="handleInputConfirm"
                        />
                        <el-button v-else class="button-new-tag" size="small" @click="showInput">
                            + 添加道岔编号
                        </el-button>
                    </div>
                  </el-form-item>

                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                      <el-button @click="editFormVisible = false">取消</el-button>
                      <el-button type="primary" @click=editPresetPoint()>确认</el-button>
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
                    <el-button type="primary" @click=deleteSwitchData()>确认</el-button>
                </div>
                </template>
            </el-dialog>
        </div>
    </div>
  </template>
  
  <script setup>
    import { ref, onMounted, reactive } from 'vue'
    import {ElMessage} from 'element-plus'
    import { getSwitch, getSwitchPresetPoint , insertSwitchPresetPoint, insertSwitch, updateSwitch, deleteSwitch, search} from '@/http/api/switch.js'

    import { ElInput } from 'element-plus'

    const formLabelWidth = '140px'
    const parentBorder = ref(false)
    const childBorder = ref(false)
    const tableData = reactive([]);

    //获取表格数据
    const getAllSwitch = async()=> {
        const response = await getSwitch();
        response.data.data.forEach(element => {
            getSwitchPresetPoint(element.trackId, element.field, element.throat).then(response=>{
                element.family = [...response.data.data];
            })
            tableData.push(element);
        });
    }
    //搜索数据
    const searchKey = reactive({
        field: "",
        trackId:"",
        throat: "",
    })

    const searchSwitch = async()=> {
        tableData.length = 0; // 清空当前表格数据
        const response = await search(searchKey.field, searchKey.trackId, searchKey.throat);
        response.data.data.forEach(element => {
            getSwitchPresetPoint(element.trackId, element.field, element.throat).then(response=>{
                element.family = [...response.data.data];
            })
            tableData.push(element);
        });
    }
    //添加数据
    const addFormVisible = ref(false)
    const addBtn = ()=> {
        addFormVisible.value = true;
    }
    const addSwitchForm = reactive({
        field: '',
        trackId: '',
        throat: '',
        switchPresetPointId: '',
    })

    const addSwitchPresetPointForm = reactive({
        id: '',
        panPosition: '',
        tiltPosition: '',
        zoom: '',
        switchNumber: {}
    })

    //道岔标签
    const inputValue = ref('')
    const listNumber = ref([])
    const inputVisible = ref(false)
    const InputRef = ref('')

    const handleClose = (tag) => {
        listNumber.value.splice(listNumber.value.indexOf(tag), 1)
    }

    const showInput = () => {
        inputVisible.value = true;
            setTimeout(() => {
                InputRef.value && InputRef.value.input && InputRef.value.input.focus();
            }, 0);
    };

    const handleInputConfirm = () => {
        if (inputValue.value) {
            listNumber.value.push(inputValue.value)
        }
        inputVisible.value = false
        inputValue.value = ''
    }

    // const removeDuplicates = () => {
    //     listNumber.value = [...new Set(listNumber.value)];
    // };

    const addPresetPoint = async()=>{
        try {
            addSwitchPresetPointForm.switchNumber = listNumber.value;
            console.log(addSwitchPresetPointForm);
            const response = await insertSwitchPresetPoint(addSwitchPresetPointForm);
            addSwitchForm.switchPresetPointId = response.data.data;
            const response2 = await insertSwitch(addSwitchForm);
            addFormVisible.value = false;
            resetaddData(); 
            tableData.length = 0; // 清空当前表格数据
            await getAllSwitch(); // 重新获取数据
        }catch {
            console.error("添加失败");
        }
        
    }

    const resetaddData = ()=> {
        addSwitchForm.field = '';
        addSwitchForm.throat = '',
        addSwitchForm.trackId = '',
        addSwitchForm.switchPresetPointId = '',
        addSwitchPresetPointForm.id = '';
        addSwitchPresetPointForm.panPosition = '',
        addSwitchPresetPointForm.tiltPosition = '';
        addSwitchPresetPointForm.zoom = '';
    }

    //编辑预置点
    const editFormVisible = ref(false)
    const editForm = reactive({
        id: '',
        panPosition:'',
        tiltPosition: '',
        zoom: '',
        switchNumber: ''
    })

    const editForm2 = reactive({
        id: '',
        field: '',
        trackId: '',
        throat: '',
        switchPresetPointId: '',
    })
    const editData = (row, row2)=> {
        editFormVisible.value = true
        editForm2.field = row.field;
        editForm2.trackId = row.trackId;
        editForm2.throat = row.throat;
        editForm2.switchPresetPointId = row2.id;

        editForm.id = row2.id;
        editForm.panPosition = row2.panPosition;
        editForm.tiltPosition = row2.tiltPosition;
        editForm.zoom = row2.zoom;
        listNumber.value = row2.switchNumber.split("、");
    }
    const editPresetPoint = async()=> {
        try {
            editForm.switchNumber = listNumber.value;
            const response = await insertSwitchPresetPoint(editForm);
            const response2 = await updateSwitch(editForm2, response.data.data);
            if(response2.success) {
                editFormVisible.value = false; 
                tableData.length = 0; // 清空当前表格数据
                await getAllSwitch(); // 重新获取数据
            }
        }catch(error) {
            console.log('预置点修改该失败:',error);   
        }
    }

    //删除预置点
    const deleteVisible = ref(false)
    const switchData = reactive({
        field: '',
        trackId: '',
        throat: '',
        switchPresetPointId: '',
    })
    //转到预置点（云台控制，需要摄像头在线）
    const gotoPreset = (row) => {
        ElMessage({
            message: '云台转到预置点需要摄像头在线，当前设备离线，暂无法执行',
            type: 'warning',
            plain: true,
        })
    }
    const deleteData = (row1, row2)=> {
        switchData.field = row1.field;
        switchData.trackId = row1.trackId;
        switchData.throat = row1.throat;
        switchData.switchPresetPointId = row2.id;
        deleteVisible.value = true;
        console.log(switchData);
        
    }
    const deleteSwitchData = async()=> { 
        try {
            const response = await deleteSwitch(switchData);
            if(response.data.success) {
                ElMessage({
                    message: '删除成功',
                    type: 'success',
                    plain: true,
                })
                deleteVisible.value = false; 
                tableData.length = 0; // 清空当前表格数据
                await getAllSwitch(); // 重新获取数据
            }
        }catch(error) {
            console.log('删除失败:',error);   
        }
    }

    onMounted(() => {
        getAllSwitch();
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
    .search-btn{
        margin-left: 4%;
    }
    .camera-list {
        height: 86%;
        width: 98%;
        margin: 0 1% 1% 1%;
        background-color: #fff;
    }
    .presetPointTable {
        overflow: auto; /* 防止内容溢出 */
        width: 100%;
    }

    ::v-deep .presetPointTable .el-table__header th {
        font-size: 12px; /* 设置字体大小 */
        font-weight: 500;
        color: #387bcd;
    }

.ops-page-header { flex:0 0 auto;min-height:80px;margin-bottom:10px;padding:6px 6px 14px;border-bottom:1px solid #cfdeeb; }
.ops-eyebrow { color:#157da6;font-size:11px;letter-spacing:1.4px;font-weight:700; }
.ops-page-header h1 { margin:4px 0 2px;color:#153b5b;font-size:24px;line-height:1.2; }
.ops-page-header p { margin:0;color:#6e879a;font-size:12px; }
.list { width:100%;height:100%;min-height:0;display:flex;flex-direction:column;padding:16px;background:linear-gradient(140deg,#f1f6fa,#f8fbfd); }
.search { flex:0 0 auto;width:100%;height:auto;min-height:66px;margin:0 0 12px;padding:12px 16px;border:0;border-left:3px solid #54afcf;border-radius:5px;background:#fff;box-shadow:0 6px 20px rgba(21,63,99,.045); }
.camera-list { flex:1;min-height:0;width:100%;height:auto;margin:0;padding:0;overflow:auto;background:#fff;border:0;border-top:2px solid #58b5d2;border-radius:8px;box-shadow:0 8px 30px rgba(21,63,99,.05); }
.camera-list :deep(.el-table) { --el-table-header-bg-color:#edf5fa;--el-table-row-hover-bg-color:#f0f8fb; }
</style>