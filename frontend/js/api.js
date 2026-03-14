/**
 * Uncapped Production Control - API Client
 */
const API = {
    base: '',

    async get(path) {
        const resp = await fetch(this.base + path);
        if (!resp.ok) throw new Error(`GET ${path}: ${resp.status}`);
        return resp.json();
    },

    async post(path, body = {}) {
        const resp = await fetch(this.base + path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `POST ${path}: ${resp.status}`);
        }
        return resp.json();
    },

    async del(path) {
        const resp = await fetch(this.base + path, { method: 'DELETE' });
        if (!resp.ok) throw new Error(`DELETE ${path}: ${resp.status}`);
        return resp.json();
    },

    // Scenes
    getScenes: ()          => API.get('/api/scenes'),
    switchScene: (scene)   => API.post('/api/scenes/switch', { scene }),
    getTemplates: ()       => API.get('/api/scenes/templates'),
    buildScene: (template, sceneName) => API.post('/api/scenes/build', { template, scene_name: sceneName }),
    showLowerThird: (name, title) => API.post('/api/scenes/lower-third', { name, title }),
    hideLowerThird: ()     => API.del('/api/scenes/lower-third'),

    // Auto-Switch
    getSwitchState: ()     => API.get('/api/switching'),
    toggleAutoSwitch: (enabled) => API.post('/api/switching/toggle', { enabled }),
    updateSwitchConfig: (cfg) => API.post('/api/switching/config', cfg),

    // Assets
    getAssets: (category)  => API.get('/api/assets' + (category ? `?category=${category}` : '')),
    loadAsset: (filePath, sceneName, inputName) => API.post('/api/assets/load', {
        file_path: filePath, scene_name: sceneName, input_name: inputName
    }),
    removeAsset: (inputName) => API.post('/api/assets/remove', { input_name: inputName }),

    // Voice
    getVoiceStatus: ()     => API.get('/api/voice'),
    toggleVoice: (enabled) => API.post('/api/voice/toggle', { enabled }),

    // Status
    getStatus: ()          => API.get('/api/status'),
};
