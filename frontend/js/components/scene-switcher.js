/**
 * Scene Switcher Component
 */
const SceneSwitcher = {
    container: null,
    templateContainer: null,

    init() {
        this.container = document.getElementById('scene-buttons');
        this.templateContainer = document.getElementById('template-buttons');
        this.loadScenes();
        this.loadTemplates();
    },

    async loadScenes() {
        try {
            const data = await API.getScenes();
            this.renderScenes(data.scenes, data.current);
        } catch (e) {
            console.error('Failed to load scenes:', e);
            // Show default camera buttons even without OBS
            this.renderScenes(['Camera 1', 'Camera 2', 'Camera 3', 'Camera 4'], null);
        }
    },

    renderScenes(scenes, current) {
        this.container.innerHTML = '';
        scenes.forEach(name => {
            const btn = document.createElement('button');
            btn.className = 'scene-btn' + (name === current ? ' active' : '');
            btn.textContent = name;
            btn.addEventListener('click', () => this.switchTo(name));
            this.container.appendChild(btn);
        });
    },

    async switchTo(sceneName) {
        try {
            await API.switchScene(sceneName);
            this.updateActive(sceneName);
        } catch (e) {
            console.error('Failed to switch scene:', e);
        }
    },

    updateActive(sceneName) {
        document.querySelectorAll('.scene-btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent === sceneName);
        });
        document.getElementById('current-scene-label').textContent = sceneName || 'No Scene';
    },

    async loadTemplates() {
        try {
            const data = await API.getTemplates();
            this.renderTemplates(data.templates);
        } catch (e) {
            console.error('Failed to load templates:', e);
        }
    },

    renderTemplates(templates) {
        this.templateContainer.innerHTML = '';
        Object.entries(templates).forEach(([key, tmpl]) => {
            const btn = document.createElement('button');
            btn.className = 'scene-btn';
            btn.textContent = tmpl.label || key;
            btn.addEventListener('click', async () => {
                try {
                    await API.buildScene(key);
                    // After building, switch to the new scene
                    await API.switchScene(tmpl.label || key);
                    this.loadScenes();
                } catch (e) {
                    console.error('Failed to build scene:', e);
                }
            });
            this.templateContainer.appendChild(btn);
        });
    },
};
