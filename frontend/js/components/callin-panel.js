/**
 * Call-In Panel Component
 * Manages up to 2 VDO.Ninja call-in slots for remote guests/reporters.
 */
const CallInPanel = {
    slots: [],

    init() {
        this.loadSlots();

        document.getElementById('callin-create-1').addEventListener('click', () => this.createInvite(1));
        document.getElementById('callin-create-2').addEventListener('click', () => this.createInvite(2));
    },

    async loadSlots() {
        try {
            const data = await API.getCallInSlots();
            this.slots = data.slots || [];
            this.render();
        } catch (e) {
            console.error('Failed to load call-in slots:', e);
        }
    },

    render() {
        for (let i = 1; i <= 2; i++) {
            const slot = this.slots[i - 1] || { slot_id: i, active: false, stream_id: '', guest_name: '' };
            this.renderSlot(i, slot);
        }
    },

    renderSlot(slotId, slot) {
        const container = document.getElementById(`callin-slot-${slotId}`);
        const hasInvite = !!slot.stream_id;

        let html = '';

        if (!hasInvite) {
            // No invite yet - show name input and create button
            html = `
                <div class="callin-empty">
                    <input type="text" id="callin-name-${slotId}" placeholder="Guest name" class="input callin-name-input">
                    <button id="callin-create-${slotId}" class="btn btn-primary callin-create-btn">Create Invite</button>
                </div>
            `;
        } else {
            // Invite exists
            const statusClass = slot.active ? 'connected' : 'disconnected';
            const statusText = slot.active ? 'Live in OBS' : 'Invite sent';

            html = `
                <div class="callin-info">
                    <div class="callin-header">
                        <strong>${slot.guest_name || 'Guest ' + slotId}</strong>
                        <span class="status-indicator ${statusClass}">
                            <span class="dot"></span> ${statusText}
                        </span>
                    </div>
                    <div class="callin-link-row">
                        <input type="text" class="input callin-link" value="${slot.guest_url}" readonly id="callin-url-${slotId}">
                        <button class="btn" onclick="CallInPanel.copyLink(${slotId})" title="Copy invite link">Copy</button>
                    </div>
                    <div class="callin-actions">
                        ${!slot.active
                            ? `<button class="btn btn-primary" onclick="CallInPanel.activate(${slotId})">Go Live</button>`
                            : `<button class="btn" onclick="CallInPanel.deactivate(${slotId})">Remove from OBS</button>`
                        }
                        <button class="btn callin-clear-btn" onclick="CallInPanel.clear(${slotId})">Clear</button>
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;

        // Re-bind create button if slot was empty (innerHTML replaced the original button)
        if (!hasInvite) {
            document.getElementById(`callin-create-${slotId}`).addEventListener('click', () => this.createInvite(slotId));
        }
    },

    async createInvite(slotId) {
        const nameInput = document.getElementById(`callin-name-${slotId}`);
        const guestName = nameInput ? nameInput.value.trim() : '';

        try {
            const slot = await API.createCallInInvite(slotId, guestName);
            this.slots[slotId - 1] = slot;
            this.renderSlot(slotId, slot);
        } catch (e) {
            console.error('Failed to create invite:', e);
        }
    },

    async activate(slotId) {
        try {
            const slot = await API.activateCallIn(slotId);
            this.slots[slotId - 1] = slot;
            this.renderSlot(slotId, slot);
        } catch (e) {
            console.error('Failed to activate call-in:', e);
        }
    },

    async deactivate(slotId) {
        try {
            const slot = await API.deactivateCallIn(slotId);
            this.slots[slotId - 1] = slot;
            this.renderSlot(slotId, slot);
        } catch (e) {
            console.error('Failed to deactivate call-in:', e);
        }
    },

    async clear(slotId) {
        try {
            const slot = await API.clearCallIn(slotId);
            this.slots[slotId - 1] = slot;
            this.renderSlot(slotId, slot);
        } catch (e) {
            console.error('Failed to clear call-in:', e);
        }
    },

    copyLink(slotId) {
        const input = document.getElementById(`callin-url-${slotId}`);
        if (input) {
            navigator.clipboard.writeText(input.value).then(() => {
                // Brief visual feedback
                const btn = input.nextElementSibling;
                const orig = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = orig; }, 1500);
            });
        }
    },
};
