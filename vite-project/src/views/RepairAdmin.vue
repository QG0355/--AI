<template>
  <div class="admin-page">
    <h2>维修单管理面板</h2>

    <table border="1">
      <thead>
        <tr>
          <th>单号</th>
          <th>报修内容</th>
          <th>当前状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in orderList" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.description }}</td>
          
          <td>
            <span v-if="item.status === 0" style="color: red;">待接单</span>
            <span v-else-if="item.status === 1" style="color: blue;">维修中</span>
            <span v-else-if="item.status === 2" style="color: green;">已完成</span>
          </td>

          <td>
            <button v-if="item.status === 0" @click="handleStatusChange(item)">
              我要接单
            </button>

            <button v-else-if="item.status === 1" @click="handleStatusChange(item)">
              维修完成
            </button>

            <span v-else>无操作</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'; // 确保你安装了 axios

export default {
  data() {
    return {
      orderList: [] // 存放从后台获取的单子
    };
  },
  mounted() {
    this.fetchOrders(); // 页面一加载就去获取数据
  },
  methods: {
    // 1. 获取所有单子的函数（你需要自己写一个对应的Django接口）
    fetchOrders() {
      axios.get('http://127.0.0.1:8000/api/get_orders/') 
        .then(res => {
          this.orderList = res.data; 
        });
    },

    // 2. 核心功能：点击按钮修改状态
    handleStatusChange(item) {
      // 发送请求给刚才写的 Django 函数
      axios.get(`http://127.0.0.1:8000/change_status/${item.id}/`)
        .then(res => {
          if (res.data.code === 200) {
            alert('操作成功！');
            // 简单粗暴：操作成功后，重新获取一次列表，刷新状态
            // 也可以直接修改 item.status = res.data.new_status (这样不用刷新列表，更高级)
            this.fetchOrders(); 
          }
        })
        .catch(err => {
          alert('出错了，请检查网络');
        });
    }
  }
};
</script>