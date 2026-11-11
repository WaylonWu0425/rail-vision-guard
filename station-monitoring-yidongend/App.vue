<script>
export default {
    onLaunch: function() {
        // 检查本地存储中是否有登录状态
        const token = uni.getStorageSync('token');
        if (token) {
            // 如果已登录，延迟跳转到home页面
            setTimeout(() => {
                uni.reLaunch({
                    url: '/pages/home/home'
                });
            }, 500); // 延迟500毫秒
        } else {
            // 如果未登录，延迟跳转到index页面
            setTimeout(() => {
                uni.reLaunch({
                    url: '/pages/index/index'
                });
            }, 500); // 延迟500毫秒
        }
    }
}
</script>
