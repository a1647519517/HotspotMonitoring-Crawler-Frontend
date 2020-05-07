import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/admin/repairList',
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

export function setRepairman(logId, repairmanName, deviceId) {
  return request({
    url: '/admin/setRepairman',
    method: 'post',
    data: {
      logId,
      repairmanName,
      deviceId
    }
  })
}

export function deleteLog(logId) {
  return request({
    url: '/admin/deleteRepairlog',
    method: 'post',
    data: { logId }
  })
}
