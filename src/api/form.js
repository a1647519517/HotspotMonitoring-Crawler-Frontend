import request from '@/utils/request'

export function getRepairmanList(params) {
  return request({
    url: '/admin/repairmanList',
    method: 'get',
    params
  })
}

export function createDevice(deviceInfo) {
  return request({
    url: '/admin/device',
    method: 'post',
    data: deviceInfo
  })
}
