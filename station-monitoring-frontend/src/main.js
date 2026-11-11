import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';  // 引入 Element Plus 的样式
import './assets/style/global.css'
// The iframe reads these same source files from public. Bundle them in the app
// so a cached standalone stylesheet cannot override the workspace theme.
import '../public/spatial-scene/instrument-materials.css'
import '../public/spatial-scene/rail-language.css'
import '../public/spatial-scene/entrance.css'
import './assets/style/operations-dark.css'
import { formatDate } from './utils/dateFormatter';

const app = createApp(App);

app.use(router); // 使用路由
app.use(ElementPlus); // 使用 Element Plus
app.use(store);
app.config.globalProperties.$formatDate = formatDate

app.mount('#app');
