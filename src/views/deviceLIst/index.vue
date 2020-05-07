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
          <span class="link-type">{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="设备类型" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.device_type }}</span>
        </template>
      </el-table-column>
      <el-table-column label="使用单位" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.use_unit }}
        </template>
      </el-table-column>
      <el-table-column label="序列号" >
        <template slot-scope="scope">
          {{ scope.row.serial_number }}
        </template>
      </el-table-column>
      <el-table-column label="使用地址" >
        <template slot-scope="scope">
          {{ scope.row.location }}
        </template>
      </el-table-column>
      <el-table-column label="维护人员" >
        <template slot-scope="scope">
          {{ scope.row.name || '无' }}
        </template>
      </el-table-column>
      <el-table-column label="生厂商" >
        <template slot-scope="scope">
          {{ scope.row.producer }}
        </template>
      </el-table-column>
      <el-table-column align="center" prop="repair_time" label="创建时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time"/>
          <span>{{ scope.row.update_time }}</span>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="设备状态" width="110" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status === 1? '正常' : '故障' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="200">
        <template slot-scope="scope">
          <el-button type="primary" plain size="small" @click="handleUpdate(scope.row)" >编辑</el-button>
          <el-button type="danger" plain size="small" @click="deleteDevice(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :model="deviceDetail" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="设备编号" prop="deviceId">
          <el-input v-model="deviceDetail.deviceId"/>
        </el-form-item>
        <el-form-item label="设备类型" prop="deviceType">
          <el-input v-model="deviceDetail.deviceType"/>
        </el-form-item>
        <el-form-item label="修理工人" prop="repairmanName">
          <el-select v-model="deviceDetail.repairmanName" class="filter-item" placeholder="Please select" clearable>
            <el-option v-for="repairman in repairmanList" :key="repairman.staff_id" :label="repairman.name" :value="repairman.name"/>
          </el-select>
        </el-form-item>
        <el-form-item label="使用单位" prop="useUnit">
          <el-input v-model="deviceDetail.useUnit"/>
        </el-form-item>
        <el-form-item label="生产商" prop="producer">
          <el-input v-model="deviceDetail.producer"/>
        </el-form-item>
        <el-form-item label="序列号" prop="serialNumber">
          <el-input v-model="deviceDetail.serialNumber"/>
        </el-form-item>
        <el-form-item label="使用地址" prop="location">
          <el-input v-model="deviceDetail.location"/>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="deviceDetail.status" class="filter-item" placeholder="Please select">
            <el-option key="1" label="正常" value="1"/>
            <el-option key="-1" label="故障" value="-1"/>
          </el-select>
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
  getDeviceList,
  getRepairmanList,
  updateDevice,
  deleteDevice
} from '@/api/deviceList'

export default {
  filters: {
    statusFilter(status) {
      const statusMap = {
        '1': 'success',
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
      deviceDetail: {
        deviceId: '',
        deviceType: '',
        useUnit: '',
        producer: '',
        serialNumber: '',
        location: '',
        repairmanName: '',
        status: ''
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
      getDeviceList({}).then(response => {
        this.list = response.list
        console.log(this.list)
        this.listLoading = false
      })
      getRepairmanList({}).then(response => {
        this.repairmanList = response.repairmanList
      })
    },
    updateData() {
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          const statusMap = {
            '正常': 1,
            '故障': -1
          }
          console.log(this.deviceDetail)
          if (!(this.deviceDetail.status * 1)) this.deviceDetail.status = statusMap[this.deviceDetail.status]
          updateDevice(this.deviceDetail)
          this.dialogFormVisible = false
          this.$router.go(0)
          this.$notify({
            title: '成功',
            message: '更新成功',
            type: 'success',
            duration: 2000
          })
        }
      })
    },
    handleUpdate(row) {
      this.deviceDetail = Object.assign({}, this.deviceDetail, {
        deviceId: row.id,
        deviceType: row.device_type,
        useUnit: row.use_unit,
        producer: row.producer,
        serialNumber: row.serial_number,
        location: row.location,
        repairmanName: row.name,
        status: row.status === 1 ? '正常' : '故障'
      })
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    deleteDevice(row) {
      deleteDevice(row.id).then(() => {
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
