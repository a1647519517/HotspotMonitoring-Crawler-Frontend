<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="120px">
      <el-form-item label="设备id">
        <el-input v-model="form.deviceId"/>
      </el-form-item>
      <el-form-item label="设备类型">
        <el-input v-model="form.deviceType"/>
      </el-form-item>
      <el-form-item label="使用单位">
        <el-input v-model="form.useUnit"/>
      </el-form-item>
      <el-form-item label="生产商">
        <el-input v-model="form.producer"/>
      </el-form-item>
      <el-form-item label="序列号">
        <el-input v-model="form.serialNumber"/>
      </el-form-item>
      <el-form-item label="设备地址">
        <el-input v-model="form.location"/>
      </el-form-item>
      <el-form-item label="修理工人" prop="repairmanName">
        <el-select v-model="form.repairmanName" class="filter-item" placeholder="Please select">
          <el-option v-for="repairman in repairmanList" :key="repairman.staff_id" :label="repairman.name" :value="repairman.name"/>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">Create</el-button>
        <el-button @click="onCancel">Cancel</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { createDevice, getRepairmanList } from '@/api/form'
export default {
  data() {
    return {
      form: {
        deviceId: '',
        deviceType: '',
        useUnit: '',
        producer: '',
        serialNumber: '',
        location: '',
        repairmanName: []
      },
      repairmanList: []
    }
  },
  created() {
    this.fetchRepairmanList()
  },
  methods: {
    onSubmit() {
      this.$refs['form'].validate(valid => {
        if (valid) {
          createDevice(this.form).then(response => {
            console.log(response)
          })
        }
      })
      this.$message('创建成功!')
    },
    onCancel() {
      this.$message({
        message: 'cancel!',
        type: 'warning'
      })
    },
    fetchRepairmanList() {
      getRepairmanList({}).then(response => {
        console.log(response)
        this.repairmanList = response.repairmanList
      })
    }
  }
}
</script>

<style scoped>
  .el-form {
    max-width: 500px;
  }

  .line {
    text-align: center;
  }
</style>

