/**
 * Uncapped Production Control - Main App
 */
const App = {
    state: {
        obsConnected: false,
        currentScene: null,
        scenes: [],
        micMapping: [],
        levelsDb: [],
        autoSwitch: { enabled: false },
        voiceRunning: false,
        voiceLastCommand: null,
        streamStartTime: null,
    },

    ws: null,

    init() {
        this.connectWebSocket();
        this.initGlobalNav();
        this.initTabs();
        this.initKeyboardShortcuts();

        // Initialize all components
        SceneSwitcher.init();
        AudioMeters.init();
        AutoSwitchControls.init();
        AssetBrowser.init();
        LowerThirds.init();
        VoiceStatus.init();
        SceneBuilderUI.init();
        CallInPanel.init();
        RunOfShowPanel.init();

        // Initial data fetch
        this.fetchInitialState();
    },

    initGlobalNav() {
        document.querySelectorAll('.global-nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.global-nav-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.global-view').forEach(v => v.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('view-' + btn.dataset.mode).classList.add('active');
            });
        });
    },

    async fetchInitialState() {
        try {
            const status = await API.getStatus();
            this.state.obsConnected = status.obs.connected;
            this.state.currentScene = status.obs.current_scene;
            this.state.autoSwitch = status.auto_switch;
            this.state.voiceRunning = status.voice.running;
            this.updateOBSStatus();
            AutoSwitchControls.update(status.auto_switch);
            VoiceStatus.update(status.voice.running);
        } catch (e) {
            console.error('Failed to fetch initial state:', e);
        }
    },

    connectWebSocket() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${location.host}/ws`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => console.log('WebSocket connected');

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWSMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting in 2s...');
            setTimeout(() => this.connectWebSocket(), 2000);
        };

        this.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
        };
    },

    handleWSMessage(data) {
        switch (data.type) {
            case 'init':
                this.state.micMapping = data.mic_mapping || [];
                this.state.obsConnected = data.obs_connected;
                this.state.currentScene = data.current_scene;
                this.state.autoSwitch = data.auto_switch;
                this.updateOBSStatus();
                AudioMeters.setMapping(this.state.micMapping);
                SceneSwitcher.updateActive(data.current_scene);
                break;

            case 'levels':
                this.state.levelsDb = data.levels_db || [];
                AudioMeters.update(this.state.levelsDb);
                break;

            case 'state':
                if (data.current_scene !== this.state.currentScene) {
                    this.state.currentScene = data.current_scene;
                    SceneSwitcher.updateActive(data.current_scene);
                    document.getElementById('current-scene-label').textContent = data.current_scene || 'No Scene';
                }
                this.state.obsConnected = data.obs_connected;
                this.state.autoSwitch = data.auto_switch;
                this.updateOBSStatus();
                if (data.voice_last_command) {
                    this.state.voiceLastCommand = data.voice_last_command;
                    VoiceStatus.updateLastCommand(data.voice_last_command);
                }
                break;
        }
    },

    updateOBSStatus() {
        const el = document.getElementById('obs-status');
        if (this.state.obsConnected) {
            el.className = 'status-indicator connected';
            el.innerHTML = '<span class="dot"></span> OBS Connected';
        } else {
            el.className = 'status-indicator disconnected';
            el.innerHTML = '<span class="dot"></span> OBS Disconnected';
        }

        const label = document.getElementById('current-scene-label');
        label.textContent = this.state.currentScene || 'No Scene';
    },

    initTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            });
        });
    },

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger if typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch (e.key) {
                case '1': API.switchScene('Camera 1').catch(console.error); break;
                case '2': API.switchScene('Camera 2').catch(console.error); break;
                case '3': API.switchScene('Camera 3').catch(console.error); break;
                case '4': API.switchScene('Camera 4').catch(console.error); break;
                case 'g':
                case 'G': API.switchScene('Gallery').catch(console.error); break;
                case 'a':
                case 'A':
                    API.toggleAutoSwitch(!App.state.autoSwitch.enabled).catch(console.error);
                    break;
                case 'v':
                case 'V':
                    API.toggleVoice(!App.state.voiceRunning).catch(console.error);
                    break;
            }
        });
    },

    // Stream timer
    startStreamTimer() {
        this.state.streamStartTime = Date.now();
        this._timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.state.streamStartTime;
            const h = String(Math.floor(elapsed / 3600000)).padStart(2, '0');
            const m = String(Math.floor((elapsed % 3600000) / 60000)).padStart(2, '0');
            const s = String(Math.floor((elapsed % 60000) / 1000)).padStart(2, '0');
            document.getElementById('stream-timer').textContent = `${h}:${m}:${s}`;
        }, 1000);
    },
};

// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
