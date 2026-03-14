/**
 * Audio Meters Component
 */
const AudioMeters = {
    container: null,
    mapping: [],
    bars: [],

    init() {
        this.container = document.getElementById('audio-meters');
    },

    setMapping(mapping) {
        this.mapping = mapping;
        this.render();
    },

    render() {
        this.container.innerHTML = '';
        this.bars = [];

        this.mapping.forEach((ch, i) => {
            const row = document.createElement('div');
            row.className = 'meter-row';

            const label = document.createElement('span');
            label.className = 'meter-label';
            label.textContent = ch.person ? ch.person.split(' ')[0] : `Ch${ch.channel + 1}`;
            label.title = ch.person || `Channel ${ch.channel + 1}`;

            const barContainer = document.createElement('div');
            barContainer.className = 'meter-bar-container';

            const bar = document.createElement('div');
            bar.className = 'meter-bar';
            barContainer.appendChild(bar);

            const dbLabel = document.createElement('span');
            dbLabel.className = 'meter-db';
            dbLabel.textContent = '-∞';

            row.appendChild(label);
            row.appendChild(barContainer);
            row.appendChild(dbLabel);
            this.container.appendChild(row);

            this.bars.push({ bar, dbLabel });
        });
    },

    update(levelsDb) {
        this.mapping.forEach((ch, i) => {
            if (i >= this.bars.length || ch.channel >= levelsDb.length) return;

            const db = levelsDb[ch.channel];
            const { bar, dbLabel } = this.bars[i];

            // Map dB to percentage: -60 dB = 0%, 0 dB = 100%
            const pct = Math.max(0, Math.min(100, ((db + 60) / 60) * 100));
            bar.style.width = pct + '%';

            // Color based on level
            bar.className = 'meter-bar';
            if (db > -6) bar.className += ' clip';
            else if (db > -20) bar.className += ' warn';

            // Display dB value
            if (db <= -60) {
                dbLabel.textContent = '-∞';
            } else {
                dbLabel.textContent = db.toFixed(0) + ' dB';
            }
        });
    },
};
