/**
 * Run of Show Panel Component
 * Pre-production segment editor for organizing the show.
 * Supports drag-and-drop reordering and file drops for assets.
 */
const RunOfShowPanel = {
    segments: [],
    _saveTimeout: null,
    _dragSrcIndex: null,

    init() {
        this.load();
        document.getElementById('ros-add-segment').addEventListener('click', () => this.addSegment());
    },

    async load() {
        try {
            const data = await API.getRunOfShow();
            this.segments = data.segments || [];
            this.render();
        } catch (e) {
            console.error('Failed to load run of show:', e);
        }
    },

    render() {
        const list = document.getElementById('ros-segment-list');
        if (!this.segments.length) {
            list.innerHTML = '<div class="ros-empty">No segments yet. Click "+ Add Segment" to start building the run of show.</div>';
            return;
        }

        list.innerHTML = this.segments.map((seg, i) => {
            const displayLabel = this._displayLabel(seg.label);
            const assets = seg.assets || [];

            return `
            <div class="ros-segment" draggable="true" data-id="${seg.id}" data-index="${i}" data-label="${seg.label.toLowerCase()}">
                <div class="ros-drag-handle" title="Drag to reorder">&#9776;</div>
                <div class="ros-label">${displayLabel}</div>
                <div class="ros-body">
                    <div class="ros-fields">
                        <input type="text" class="input ros-title" placeholder="Topic / description"
                               value="${this._esc(seg.title)}" data-id="${seg.id}" data-field="title">
                        <textarea class="input ros-notes" placeholder="Notes"
                                  data-id="${seg.id}" data-field="notes" rows="2">${this._esc(seg.notes)}</textarea>
                    </div>
                    <div class="ros-asset-drop" id="ros-drop-${seg.id}" data-segid="${seg.id}">
                        ${assets.length ? `
                            <div class="ros-asset-chips">
                                ${assets.map((a, ai) => `
                                    <div class="ros-asset-chip" title="${this._esc(a.path)}">
                                        <span class="ros-asset-icon">${this._fileIcon(a.path)}</span>
                                        <span class="ros-asset-name">${this._esc(a.name || this._filename(a.path))}</span>
                                        <button class="ros-asset-remove" onclick="event.stopPropagation(); RunOfShowPanel.removeAsset('${seg.id}', ${ai})" title="Remove">&times;</button>
                                    </div>
                                `).join('')}
                            </div>
                            <div class="ros-drop-hint">Drop files here or click to add more</div>
                        ` : `
                            <div class="ros-drop-empty">
                                <div class="ros-drop-icon">+</div>
                                <div class="ros-drop-text">Add Assets</div>
                                <div class="ros-drop-subtext">Drop files here or click to browse</div>
                            </div>
                        `}
                        <input type="file" class="ros-file-input" id="ros-file-${seg.id}" data-segid="${seg.id}" multiple style="display:none;">
                    </div>
                </div>
                <div class="ros-actions">
                    <button class="btn ros-btn-sm ros-btn-del" onclick="RunOfShowPanel.deleteSegment('${seg.id}')" title="Remove segment">&#10005;</button>
                </div>
            </div>`;
        }).join('');

        // Bind input events for auto-save
        list.querySelectorAll('.ros-title, .ros-notes').forEach(el => {
            el.addEventListener('input', (e) => {
                this.onFieldChange(e.target.dataset.id, e.target.dataset.field, e.target.value);
            });
        });

        // Bind drag-and-drop for reordering
        this._bindDragEvents(list);

        // Bind file drop zones and click-to-browse
        this._bindFileDropZones();
    },

    // --- File drop zones ---

    _bindFileDropZones() {
        document.querySelectorAll('.ros-asset-drop').forEach(zone => {
            const segId = zone.dataset.segid;
            const fileInput = document.getElementById('ros-file-' + segId);

            // Click to browse
            zone.addEventListener('click', (e) => {
                // Don't trigger if clicking a chip remove button
                if (e.target.closest('.ros-asset-remove')) return;
                fileInput.click();
            });

            // File input change
            fileInput.addEventListener('change', (e) => {
                this._handleFiles(segId, e.target.files);
                e.target.value = ''; // Reset so same file can be re-added
            });

            // Drag over
            zone.addEventListener('dragover', (e) => {
                // Only handle file drags, not segment reorder drags
                if (e.dataTransfer.types.includes('Files')) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.dataTransfer.dropEffect = 'copy';
                    zone.classList.add('ros-drop-active');
                }
            });

            zone.addEventListener('dragleave', (e) => {
                // Only remove if actually leaving the zone
                if (!zone.contains(e.relatedTarget)) {
                    zone.classList.remove('ros-drop-active');
                }
            });

            // Drop files
            zone.addEventListener('drop', (e) => {
                if (e.dataTransfer.types.includes('Files')) {
                    e.preventDefault();
                    e.stopPropagation();
                    zone.classList.remove('ros-drop-active');
                    this._handleFiles(segId, e.dataTransfer.files);
                }
            });
        });
    },

    async _handleFiles(segId, fileList) {
        if (!fileList || !fileList.length) return;

        for (const file of fileList) {
            try {
                await API.uploadSegmentAsset(segId, file);
            } catch (e) {
                console.error('Failed to upload asset:', e);
            }
        }
        // Reload to get updated segment data
        await this.load();
    },

    // --- Segment drag and drop reordering ---

    _bindDragEvents(list) {
        const segments = list.querySelectorAll('.ros-segment');
        segments.forEach(el => {
            el.addEventListener('dragstart', (e) => {
                this._dragSrcIndex = parseInt(el.dataset.index);
                el.classList.add('ros-dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', el.dataset.index);
            });

            el.addEventListener('dragend', () => {
                el.classList.remove('ros-dragging');
                list.querySelectorAll('.ros-segment').forEach(s => s.classList.remove('ros-drag-over'));
            });

            el.addEventListener('dragover', (e) => {
                // Only handle segment reordering, not file drops
                if (e.dataTransfer.types.includes('Files')) return;
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                list.querySelectorAll('.ros-segment').forEach(s => s.classList.remove('ros-drag-over'));
                el.classList.add('ros-drag-over');
            });

            el.addEventListener('dragleave', () => {
                el.classList.remove('ros-drag-over');
            });

            el.addEventListener('drop', (e) => {
                if (e.dataTransfer.types.includes('Files')) return; // Let file drop handle it
                e.preventDefault();
                el.classList.remove('ros-drag-over');
                const fromIndex = this._dragSrcIndex;
                const toIndex = parseInt(el.dataset.index);
                if (fromIndex === null || fromIndex === toIndex) return;

                const [moved] = this.segments.splice(fromIndex, 1);
                this.segments.splice(toIndex, 0, moved);
                this.render();
                this.save();
            });
        });
    },

    _displayLabel(label) {
        const upper = label.toUpperCase();
        if (upper === 'INTRO') return 'Intro';
        if (upper === 'OUTRO') return 'Outro';
        return upper + ' Block';
    },

    onFieldChange(id, field, value) {
        const seg = this.segments.find(s => s.id === id);
        if (seg) seg[field] = value;
        this._debounceSave();
    },

    _debounceSave() {
        clearTimeout(this._saveTimeout);
        this._saveTimeout = setTimeout(() => this.save(), 500);
    },

    async save() {
        try {
            await API.saveRunOfShow(this.segments);
        } catch (e) {
            console.error('Failed to save run of show:', e);
        }
    },

    async addSegment() {
        const label = this._nextLabel();
        try {
            const data = await API.addSegment(label);
            this.segments = data.segments || [];
            this.render();
        } catch (e) {
            console.error('Failed to add segment:', e);
        }
    },

    async deleteSegment(id) {
        try {
            const data = await API.deleteSegment(id);
            this.segments = data.segments || [];
            this.render();
        } catch (e) {
            console.error('Failed to delete segment:', e);
        }
    },

    removeAsset(segId, assetIndex) {
        const seg = this.segments.find(s => s.id === segId);
        if (!seg || !seg.assets) return;
        seg.assets.splice(assetIndex, 1);
        this.render();
        this.save();
    },

    // --- Helpers ---

    _nextLabel() {
        const used = new Set(this.segments.map(s => s.label.toUpperCase()));
        for (let i = 0; i < 26; i++) {
            const letter = String.fromCharCode(65 + i);
            if (!used.has(letter)) return letter;
        }
        return 'X' + (this.segments.length + 1);
    },

    _filename(path) {
        return path.split('/').pop().split('\\').pop();
    },

    _fileIcon(path) {
        const ext = path.split('.').pop().toLowerCase();
        if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext)) return '&#128444;';
        if (['mp4', 'mov', 'avi', 'webm', 'mkv'].includes(ext)) return '&#127910;';
        if (['mp3', 'wav', 'ogg', 'flac', 'aac'].includes(ext)) return '&#127925;';
        return '&#128196;';
    },

    _esc(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },
};
