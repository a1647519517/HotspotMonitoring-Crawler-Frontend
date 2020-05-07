import request from '@/utils/request'

export function getDeviceList(params) {
  return request({
    url: '/admin/deviceList',
    method: 'get',
    params
  })
}

export function getRepairmanList(params) {
  return request({
    url: '/admin/repairmanList',
    method: 'get',
    params
  })
}

export function updateDevice(deviceInfo) {
  return request({
    url: '/admin/editDevice',
    method: 'post',
    data: deviceInfo
  })
}

export function deleteDevice(deviceId) {
  return request({
    url: '/admin/deleteDevice',
    method: 'post',
    data: { deviceId }
  })
}
