import {defineConfig} from 'vite';import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],base:process.env.GITHUB_ACTIONS?'/engineering-intelligence-platform/':'/',test:{environment:'jsdom'},server:{proxy:{'/api':'http://localhost:8000','/health':'http://localhost:8000'}}});
