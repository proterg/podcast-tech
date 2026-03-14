/**
 * Asset Browser Component
 */
const AssetBrowser = {
    container: null,
    categorySelect: null,
    selectedAsset: null,

    init() {
        this.container = document.getElementById('asset-grid');
        this.categorySelect = document.getElementById('asset-category');

        document.getElementById('refresh-assets').addEventListener('click', () => this.load());
        this.categorySelect.addEventListener('change', () => this.load());

        this.load();
    },

    async load() {
        try {
            const category = this.categorySelect.value || undefined;
            const data = await API.getAssets(category);

            // Update category dropdown
            if (data.categories) {
                const current = this.categorySelect.value;
                this.categorySelect.innerHTML = '<option value="">All Categories</option>';
                data.categories.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat;
                    this.categorySelect.appendChild(opt);
                });
                this.categorySelect.value = current;
            }

            this.render(data.files || []);
        } catch (e) {
            console.error('Failed to load assets:', e);
        }
    },

    render(files) {
        this.container.innerHTML = '';

        if (files.length === 0) {
            this.container.innerHTML = '<div style="color: var(--text-secondary); font-size: 12px;">No assets found. Drop files in the assets/ directory.</div>';
            return;
        }

        files.forEach(file => {
            const card = document.createElement('div');
            card.className = 'asset-card';

            const icon = document.createElement('div');
            icon.className = 'asset-icon';
            icon.textContent = this.getIcon(file.extension);

            const name = document.createElement('div');
            name.className = 'asset-name';
            name.textContent = file.name;
            name.title = file.name;

            card.appendChild(icon);
            card.appendChild(name);

            card.addEventListener('click', () => {
                document.querySelectorAll('.asset-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.selectedAsset = file;
            });

            card.addEventListener('dblclick', () => this.loadAsset(file));

            this.container.appendChild(card);
        });
    },

    async loadAsset(file) {
        try {
            await API.loadAsset(file.path);
        } catch (e) {
            console.error('Failed to load asset:', e);
        }
    },

    getIcon(ext) {
        const icons = {
            '.png': '🖼', '.jpg': '🖼', '.jpeg': '🖼', '.gif': '🖼', '.webp': '🖼',
            '.mp4': '🎬', '.mkv': '🎬', '.mov': '🎬', '.avi': '🎬', '.webm': '🎬',
            '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵', '.flac': '🎵',
            '.html': '📄',
        };
        return icons[ext] || '📁';
    },
};
