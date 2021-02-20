<template>
  <div>
    <div id="myChart"></div>
  </div>
</template>

<script>

import { constantRouterMap } from '../../router'
import axios from 'axios'

export default {
  name: '',
  data() {
    return {
      list: []
    }
  },
  mounted() {
    axios({
      method: 'get',
      url: 'http://47.103.216.159/admin/getData'
    })
      .then(res => {
        console.log(res.data.slice(0, 30))
        // this.list = res.data.slice(0, 30)
        this.queryData(res.data.slice(0, 30))
      })
  },
  methods: {
    compare(prop) {
      return function (obj1, obj2) {
        var val1 = obj1[prop];
        var val2 = obj2[prop];if (val1 > val2) {
          return -1;
        } else if (val1 < val2) {
          return 1;
        } else {
          return 0;
        }
      }
    },
    queryData(list) {
      let keywords = []
      let related_content_count = []
      let keysentences = []
      let heat = []
      console.log('list')
      console.log(list)
      list.sort(this.compare('heat'))
      for (let i = 0; i < list.length; i++) {
        keywords.push(list[i].keywords)
        related_content_count.push(list[i].count)
        keysentences.push(list[i].keysentences)
        heat.push(list[i].heat)
      }
      this.showBar(keywords, related_content_count, keysentences, heat)
    },
    showBar(keywords, related_content_count, keysentences, heat) {
      let myChart = this.$echarts.init(document.getElementById('myChart'))
      let format = (e) => {
        return e.substr(0, 20) + '...';
      }
      myChart.setOption({
        title: { text: '热点舆情' },
        legend: {
          data: ['相关新闻数']
        },
        grid:{//直角坐标系内绘图网格
          show: false,//是否显示直角坐标系网格
          left: '20%',
          borderColor:"#c45455",//网格的边框颜色
        },
        tooltip: {
          formatter: function(params, callback) {
            return params.name +'<br/>' + '相关新闻数： ' + params.value
          }
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: keywords,
          axisLabel: {
            interval: 0,
            formatter: format,
            color: '#333'
          },
          inverse: true
        },
        series: [
          {
            name: '热点舆情',
            type: 'bar',
            data: heat
          }
        ]
      })
    }
  }
}
</script>

<style scoped>
#myChart {
  width: 100%;
  height: 860px;
}
</style>
