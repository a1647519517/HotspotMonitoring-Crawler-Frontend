import request from '@/utils/request'

export function getData() {
  return request({
    url: '/admin/getData',
    method: 'get'
  })
}

// export function getRepairmanList(params) {
//   return request({
//     url: '/admin/repairmanList',
//     method: 'get',
//     params
//   })
// }
//
// export function setRepairman(logId, repairmanName, deviceId) {
//   return request({
//     url: '/admin/setRepairman',
//     method: 'post',
//     data: {
//       logId,
//       repairmanName,
//       deviceId
//     }
//   })
// }

export function deleteLog(logId) {
  return request({
    url: '/admin/deleteRepairlog',
    method: 'post',
    data: { logId }
  })
}
