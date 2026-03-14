/**
 * Lower Thirds Component
 */
const LowerThirds = {
    init() {
        document.getElementById('lt-show').addEventListener('click', () => this.show());
        document.getElementById('lt-hide').addEventListener('click', () => this.hide());

        // Build presets from mic mapping once we have it
        this._checkMapping();
    },

    _checkMapping() {
        // Wait for mic mapping from WebSocket init
        const check = () => {
            if (App.state.micMapping && App.state.micMapping.length > 0) {
                this.buildPresets(App.state.micMapping);
            } else {
                setTimeout(check, 500);
            }
        };
        check();
    },

    buildPresets(mapping) {
        const container = document.getElementById('lt-presets');
        container.innerHTML = '';

        mapping.forEach(ch => {
            if (!ch.person) return;
            const btn = document.createElement('button');
            btn.className = 'lt-preset-btn';
            btn.textContent = ch.person.split('(')[0].trim();
            btn.addEventListener('click', () => {
                document.getElementById('lt-name').value = ch.person.split('(')[0].trim();
                document.getElementById('lt-title').value = '';
                this.show();
            });
            container.appendChild(btn);
        });
    },

    async show() {
        const name = document.getElementById('lt-name').value.trim();
        const title = document.getElementById('lt-title').value.trim();
        if (!name) return;

        try {
            await API.showLowerThird(name, title);
        } catch (e) {
            console.error('Failed to show lower third:', e);
        }
    },

    async hide() {
        try {
            await API.hideLowerThird();
        } catch (e) {
            console.error('Failed to hide lower third:', e);
        }
    },
};
