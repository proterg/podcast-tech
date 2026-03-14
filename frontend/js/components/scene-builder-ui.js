/**
 * Scene Builder UI Component
 */
const SceneBuilderUI = {
    container: null,

    init() {
        this.container = document.getElementById('scene-builder-templates');
        this.load();
    },

    async load() {
        try {
            const data = await API.getTemplates();
            this.render(data.templates);
        } catch (e) {
            console.error('Failed to load scene templates:', e);
        }
    },

    render(templates) {
        this.container.innerHTML = '';

        Object.entries(templates).forEach(([key, tmpl]) => {
            const card = document.createElement('div');
            card.className = 'template-card';

            const title = document.createElement('h4');
            title.textContent = tmpl.label || key;

            const preview = document.createElement('div');
            preview.className = 'template-preview';

            // Render mini layout preview
            const canvas = { width: 1920, height: 1080 };
            tmpl.layout.forEach(slot => {
                const el = document.createElement('div');
                el.className = 'template-slot';
                el.style.left = (slot.x / canvas.width * 100) + '%';
                el.style.top = (slot.y / canvas.height * 100) + '%';
                el.style.width = (slot.width / canvas.width * 100) + '%';
                el.style.height = (slot.height / canvas.height * 100) + '%';
                el.textContent = slot.source;
                preview.appendChild(el);
            });

            card.appendChild(title);
            card.appendChild(preview);

            card.addEventListener('click', async () => {
                try {
                    await API.buildScene(key);
                    await API.switchScene(tmpl.label || key);
                    SceneSwitcher.loadScenes();
                } catch (e) {
                    console.error('Failed to build scene:', e);
                }
            });

            this.container.appendChild(card);
        });
    },
};
