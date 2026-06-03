import { createApp } from 'vue'
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community'
import App from './App.vue'

ModuleRegistry.registerModules([AllCommunityModule])

createApp(App).mount('#app')
