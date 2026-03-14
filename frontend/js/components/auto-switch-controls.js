/**
 * Auto-Switch Controls Component
 */
const AutoSwitchControls = {
    init() {
        const onBtn = document.getElementById('auto-switch-on');
        const offBtn = document.getElementById('auto-switch-off');

        onBtn.addEventListener('click', () => this.toggle(true));
        offBtn.addEventListener('click', () => this.toggle(false));

        // Sliders
        this.initSlider('threshold-slider', 'threshold-value', 'threshold_db', v => v + ' dB');
        this.initSlider('debounce-slider', 'debounce-value', 'debounce_ms', v => v + ' ms');
        this.initSlider('cooldown-slider', 'cooldown-value', 'cooldown_ms', v => v + ' ms');
    },

    initSlider(sliderId, valueId, configKey, format) {
        const slider = document.getElementById(sliderId);
        const display = document.getElementById(valueId);

        slider.addEventListener('input', () => {
            display.textContent = format(slider.value);
        });

        slider.addEventListener('change', () => {
            const val = Number(slider.value);
            API.updateSwitchConfig({ [configKey]: val }).catch(console.error);
        });
    },

    async toggle(enabled) {
        try {
            const state = await API.toggleAutoSwitch(enabled);
            this.update(state);
        } catch (e) {
            console.error('Failed to toggle auto-switch:', e);
        }
    },

    update(state) {
        const onBtn = document.getElementById('auto-switch-on');
        const offBtn = document.getElementById('auto-switch-off');

        onBtn.classList.toggle('active', state.enabled);
        offBtn.classList.toggle('active', !state.enabled);

        if (state.threshold_db !== undefined) {
            document.getElementById('threshold-slider').value = state.threshold_db;
            document.getElementById('threshold-value').textContent = state.threshold_db + ' dB';
        }
        if (state.debounce_ms !== undefined) {
            document.getElementById('debounce-slider').value = state.debounce_ms;
            document.getElementById('debounce-value').textContent = state.debounce_ms + ' ms';
        }
        if (state.cooldown_ms !== undefined) {
            document.getElementById('cooldown-slider').value = state.cooldown_ms;
            document.getElementById('cooldown-value').textContent = state.cooldown_ms + ' ms';
        }
    },
};
