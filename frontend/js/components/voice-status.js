/**
 * Voice Status Component
 */
const VoiceStatus = {
    init() {
        document.getElementById('voice-on').addEventListener('click', () => this.toggle(true));
        document.getElementById('voice-off').addEventListener('click', () => this.toggle(false));
    },

    async toggle(enabled) {
        try {
            const resp = await API.toggleVoice(enabled);
            this.update(resp.running);
        } catch (e) {
            console.error('Failed to toggle voice:', e);
        }
    },

    update(running) {
        App.state.voiceRunning = running;

        const onBtn = document.getElementById('voice-on');
        const offBtn = document.getElementById('voice-off');
        onBtn.classList.toggle('active', running);
        offBtn.classList.toggle('active', !running);

        const indicator = document.getElementById('voice-listening-indicator');
        const footerIndicator = document.getElementById('voice-indicator');

        if (running) {
            indicator.className = 'status-indicator connected';
            indicator.innerHTML = '<span class="dot"></span> Listening';
            footerIndicator.className = 'status-indicator connected';
            footerIndicator.innerHTML = '<span class="dot"></span> Voice: On';
        } else {
            indicator.className = 'status-indicator';
            indicator.innerHTML = '<span class="dot"></span> Not Listening';
            footerIndicator.className = 'status-indicator';
            footerIndicator.innerHTML = '<span class="dot"></span> Voice: Off';
        }
    },

    updateLastCommand(cmd) {
        if (!cmd) return;
        const text = cmd.matched_text || '--';
        const action = cmd.action || '';
        const confidence = cmd.confidence ? Math.round(cmd.confidence * 100) + '%' : '';

        document.getElementById('voice-last-text').textContent = `"${text}" → ${action} (${confidence})`;
        document.getElementById('voice-footer-last').textContent = `Last: "${text}" → ${action}`;
    },
};
