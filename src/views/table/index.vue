<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column label="设备编号" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.device_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="报修用户" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.userInfo.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="修理工人" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.repairmanInfo? scope.row.repairmanInfo.name : '无' }}
        </template>
      </el-table-column>
      <el-table-column label="报修详情" >
        <template slot-scope="scope">
          {{ scope.row.detail }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="报修状态" width="110" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.log_status | statusFilter">{{ scope.row.log_status === 1? '已修复' : '维修中' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="repair_time" label="报修时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time"/>
          <span>{{ scope.row.repair_time }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="finish_time" label="结束时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time"/>
          <span>{{ scope.row.finish_time || '未完成' }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="200">
        <template slot-scope="scope">
          <el-button type="primary" plain size="small" @click="handleUpdate(scope.row)" >编辑</el-button>
          <el-button type="danger" plain size="small" @click="deleteRepairLog(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :model="repairDetail" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="设备编号" prop="deviceId">
          <el-input v-model="repairDetail.device_id" disabled="true"/>
        </el-form-item>
        <el-form-item label="报修用户" prop="userName">
          <el-input v-model="repairDetail.userInfo.name" disabled="true"/>
        </el-form-item>
        <el-form-item label="修理工人" prop="repairmanName">
          <el-select v-model="repairDetail.repairmanInfo.name" class="filter-item" placeholder="Please select">
            <el-option v-for="repairman in repairmanList" :key="repairman.staff_id" :label="repairman.name" :value="repairman.name"/>
          </el-select>
        </el-form-item>
        <el-form-item label="报修详情" prop="detail">
          <el-input v-model="repairDetail.detail" disabled="true"/>
        </el-form-item>
        <el-form-item label="报修时间" prop="repairTime">
          <el-input v-model="repairDetail.repair_time" disabled="true"/>
        </el-form-item>
        <el-form-item label="结束时间" prop="finishTime">
          <el-input v-model="repairDetail.finish_time" disabled="true"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">关闭</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getList,
  getRepairmanList,
  setRepairman,
  deleteLog
} from '@/api/table'

export default {
  filters: {
    statusFilter(status) {
      const statusMap = {
        '1': 'success',
        // draft: 'gray',
        '-1': 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      textMap: {
        update: 'Edit'
      },
      dialogFormVisible: false,
      dialogStatus: '',
      repairDetail: {
        device_id: '',
        userInfo: {
          name: ''
        },
        repairmanInfo: {
          name: ''
        },
        detail: '',
        repair_time: '',
        finish_time: ''
      },
      repairmanList: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getList({}).then(response => {
        this.list = response.list
        this.listLoading = false
      })
      getRepairmanList({}).then(response => {
        this.repairmanList = response.repairmanList
      })
    },
    updateData() {
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          setRepairman(this.repairDetail.log_id, this.repairDetail.repairmanInfo.name, this.repairDetail.device_id).then(() => {
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.fetchData()
            this.dialogFormVisible = false
          })
        }
      })
    },
    handleUpdate(row) {
      this.repairDetail = Object.assign({}, this.repairDetail, { ...row })
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    deleteRepairLog(row) {
      deleteLog(row.log_id).then(() => {
        this.fetchData()
        return this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
      })
    }
  }
}
</script>
