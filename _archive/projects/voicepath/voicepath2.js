/**
 * ═══════════════════════════════════════════════════════════════════════════
 * VOICEPATH v2 — The Words ARE the Visualization
 * 
 * Typography as Trajectory
 * QuickDraw GX Reborn
 * 
 * The words transform based on meaning:
 *   - SIZE reflects TENSION (bigger = more intense)
 *   - VERTICAL POSITION reflects VALENCE (higher = positive, lower = negative)
 *   - COLOR shifts with emotion
 *   - The sentence BENDS visually
 * 
 * You don't watch a dot. You watch the words dance.
 * 
 * ═══════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════
// DEMO SONGS — Each word has tension (-1 to 1) and valence (-1 to 1)
// ═══════════════════════════════════════════════════════════════════════════

const SONGS = {
    dayinthelife: {
        title: "A Day in the Life",
        artist: "Kinematic Demo",
        duration: 65,
        lines: [
            {
                startTime: 0,
                words: [
                    { text: "I", tension: -0.3, valence: 0.1, duration: 0.3 },
                    { text: "read", tension: -0.2, valence: 0.1, duration: 0.4 },
                    { text: "the", tension: -0.3, valence: 0.0, duration: 0.2 },
                    { text: "news", tension: -0.1, valence: 0.0, duration: 0.5 },
                    { text: "today,", tension: -0.2, valence: 0.0, duration: 0.5 },
                    { text: "oh", tension: -0.4, valence: -0.2, duration: 0.6 },
                    { text: "boy", tension: -0.5, valence: -0.3, duration: 0.8 },
                ]
            },
            {
                startTime: 6,
                words: [
                    { text: "About", tension: 0.0, valence: 0.2, duration: 0.4 },
                    { text: "a", tension: 0.0, valence: 0.2, duration: 0.2 },
                    { text: "lucky", tension: 0.3, valence: 0.5, duration: 0.5 },
                    { text: "man", tension: 0.4, valence: 0.4, duration: 0.4 },
                    { text: "who", tension: 0.2, valence: 0.3, duration: 0.3 },
                    { text: "made", tension: 0.3, valence: 0.5, duration: 0.4 },
                    { text: "the", tension: 0.2, valence: 0.4, duration: 0.2 },
                    { text: "grade", tension: 0.4, valence: 0.6, duration: 0.7 },
                ]
            },
            {
                startTime: 13,
                words: [
                    { text: "And", tension: 0.1, valence: 0.1, duration: 0.3 },
                    { text: "though", tension: 0.2, valence: 0.0, duration: 0.4 },
                    { text: "the", tension: 0.1, valence: -0.1, duration: 0.2 },
                    { text: "news", tension: 0.2, valence: -0.2, duration: 0.4 },
                    { text: "was", tension: 0.1, valence: -0.3, duration: 0.3 },
                    { text: "rather", tension: 0.0, valence: -0.4, duration: 0.5 },
                    { text: "sad", tension: -0.2, valence: -0.7, duration: 0.8 },
                ]
            },
            {
                startTime: 20,
                words: [
                    { text: "Well,", tension: 0.2, valence: 0.1, duration: 0.4 },
                    { text: "I", tension: 0.3, valence: 0.2, duration: 0.2 },
                    { text: "just", tension: 0.4, valence: 0.3, duration: 0.3 },
                    { text: "had", tension: 0.5, valence: 0.4, duration: 0.3 },
                    { text: "to", tension: 0.5, valence: 0.4, duration: 0.2 },
                    { text: "laugh", tension: 0.7, valence: 0.6, duration: 0.9 },
                ]
            },
            {
                startTime: 27,
                words: [
                    { text: "I", tension: -0.1, valence: -0.1, duration: 0.3 },
                    { text: "saw", tension: -0.2, valence: -0.2, duration: 0.4 },
                    { text: "the", tension: -0.3, valence: -0.3, duration: 0.2 },
                    { text: "photograph", tension: -0.4, valence: -0.5, duration: 1.2 },
                ]
            },
            // Second movement
            {
                startTime: 35,
                words: [
                    { text: "Woke", tension: 0.3, valence: 0.1, duration: 0.4 },
                    { text: "up,", tension: 0.4, valence: 0.2, duration: 0.4 },
                    { text: "fell", tension: 0.5, valence: -0.1, duration: 0.4 },
                    { text: "out", tension: 0.6, valence: -0.2, duration: 0.3 },
                    { text: "of", tension: 0.5, valence: -0.1, duration: 0.2 },
                    { text: "bed", tension: 0.4, valence: 0.0, duration: 0.5 },
                ]
            },
            {
                startTime: 42,
                words: [
                    { text: "Dragged", tension: 0.3, valence: -0.1, duration: 0.5 },
                    { text: "a", tension: 0.2, valence: 0.0, duration: 0.2 },
                    { text: "comb", tension: 0.2, valence: 0.1, duration: 0.4 },
                    { text: "across", tension: 0.3, valence: 0.1, duration: 0.4 },
                    { text: "my", tension: 0.2, valence: 0.0, duration: 0.2 },
                    { text: "head", tension: 0.3, valence: 0.1, duration: 0.5 },
                ]
            },
            {
                startTime: 49,
                words: [
                    { text: "Found", tension: 0.1, valence: 0.2, duration: 0.4 },
                    { text: "my", tension: 0.0, valence: 0.2, duration: 0.2 },
                    { text: "way", tension: 0.1, valence: 0.3, duration: 0.3 },
                    { text: "downstairs", tension: 0.0, valence: 0.2, duration: 0.6 },
                    { text: "and", tension: -0.1, valence: 0.2, duration: 0.2 },
                    { text: "drank", tension: -0.2, valence: 0.3, duration: 0.4 },
                    { text: "a", tension: -0.2, valence: 0.3, duration: 0.2 },
                    { text: "cup", tension: -0.3, valence: 0.4, duration: 0.5 },
                ]
            },
            {
                startTime: 57,
                words: [
                    { text: "Looking", tension: 0.2, valence: 0.3, duration: 0.5 },
                    { text: "up,", tension: 0.3, valence: 0.4, duration: 0.4 },
                    { text: "I", tension: 0.4, valence: 0.2, duration: 0.2 },
                    { text: "noticed", tension: 0.5, valence: 0.0, duration: 0.5 },
                    { text: "I", tension: 0.6, valence: -0.2, duration: 0.2 },
                    { text: "was", tension: 0.7, valence: -0.3, duration: 0.3 },
                    { text: "late", tension: 0.8, valence: -0.4, duration: 0.8 },
                ]
            },
        ]
    },
    
    spiral: {
        title: "Descending Spiral",
        artist: "Verified Trajectory",
        duration: 50,
        lines: [
            {
                startTime: 0,
                words: [
                    { text: "Circle", tension: -0.3, valence: 0.4, duration: 0.5 },
                    { text: "one", tension: -0.2, valence: 0.4, duration: 0.4 },
                    { text: "begins", tension: -0.1, valence: 0.3, duration: 0.6 },
                ]
            },
            {
                startTime: 4,
                words: [
                    { text: "Rising", tension: 0.1, valence: 0.5, duration: 0.5 },
                    { text: "on", tension: 0.2, valence: 0.5, duration: 0.3 },
                    { text: "the", tension: 0.2, valence: 0.4, duration: 0.2 },
                    { text: "surface", tension: 0.3, valence: 0.4, duration: 0.6 },
                ]
            },
            {
                startTime: 9,
                words: [
                    { text: "Seeming", tension: 0.4, valence: 0.3, duration: 0.5 },
                    { text: "to", tension: 0.4, valence: 0.2, duration: 0.2 },
                    { text: "climb", tension: 0.5, valence: 0.2, duration: 0.6 },
                ]
            },
            {
                startTime: 13,
                words: [
                    { text: "But", tension: 0.3, valence: 0.0, duration: 0.3 },
                    { text: "underneath...", tension: 0.2, valence: -0.2, duration: 1.0 },
                ]
            },
            {
                startTime: 17,
                words: [
                    { text: "...we", tension: 0.1, valence: -0.3, duration: 0.4 },
                    { text: "descend", tension: 0.0, valence: -0.5, duration: 0.8 },
                ]
            },
            {
                startTime: 22,
                words: [
                    { text: "Circle", tension: -0.2, valence: 0.2, duration: 0.5 },
                    { text: "two", tension: -0.1, valence: 0.2, duration: 0.4 },
                ]
            },
            {
                startTime: 26,
                words: [
                    { text: "The", tension: 0.0, valence: 0.1, duration: 0.2 },
                    { text: "pattern", tension: 0.1, valence: 0.1, duration: 0.5 },
                    { text: "repeats", tension: 0.2, valence: 0.0, duration: 0.6 },
                ]
            },
            {
                startTime: 30,
                words: [
                    { text: "Higher,", tension: 0.4, valence: 0.1, duration: 0.5 },
                    { text: "they", tension: 0.3, valence: 0.0, duration: 0.3 },
                    { text: "say", tension: 0.2, valence: -0.1, duration: 0.5 },
                ]
            },
            {
                startTime: 34,
                words: [
                    { text: "Lower", tension: 0.1, valence: -0.4, duration: 0.5 },
                    { text: "we", tension: 0.0, valence: -0.5, duration: 0.3 },
                    { text: "go", tension: -0.1, valence: -0.6, duration: 0.6 },
                ]
            },
            {
                startTime: 39,
                words: [
                    { text: "Final", tension: -0.2, valence: -0.3, duration: 0.5 },
                    { text: "circle", tension: -0.3, valence: -0.4, duration: 0.5 },
                ]
            },
            {
                startTime: 43,
                words: [
                    { text: "We", tension: -0.1, valence: -0.5, duration: 0.3 },
                    { text: "were", tension: 0.0, valence: -0.6, duration: 0.3 },
                    { text: "always", tension: 0.1, valence: -0.7, duration: 0.5 },
                    { text: "falling", tension: 0.0, valence: -0.8, duration: 0.8 },
                ]
            },
            {
                startTime: 48,
                words: [
                    { text: "Down", tension: -0.3, valence: -0.9, duration: 1.5 },
                ]
            },
        ]
    },

    emotional: {
        title: "Emotional Journey",
        artist: "Newton Engine",
        duration: 40,
        lines: [
            {
                startTime: 0,
                words: [
                    { text: "Quiet", tension: -0.8, valence: -0.3, duration: 0.6 },
                    { text: "sorrow", tension: -0.7, valence: -0.6, duration: 0.7 },
                    { text: "sits", tension: -0.6, valence: -0.5, duration: 0.4 },
                ]
            },
            {
                startTime: 5,
                words: [
                    { text: "Then", tension: -0.4, valence: -0.2, duration: 0.3 },
                    { text: "something", tension: -0.2, valence: 0.0, duration: 0.5 },
                    { text: "stirs", tension: 0.0, valence: 0.2, duration: 0.5 },
                ]
            },
            {
                startTime: 10,
                words: [
                    { text: "Hope", tension: 0.2, valence: 0.5, duration: 0.5 },
                    { text: "rises", tension: 0.3, valence: 0.6, duration: 0.5 },
                    { text: "gentle", tension: 0.1, valence: 0.7, duration: 0.6 },
                ]
            },
            {
                startTime: 15,
                words: [
                    { text: "Peace", tension: -0.5, valence: 0.8, duration: 0.6 },
                    { text: "settles", tension: -0.6, valence: 0.7, duration: 0.5 },
                    { text: "soft", tension: -0.7, valence: 0.6, duration: 0.5 },
                ]
            },
            {
                startTime: 20,
                words: [
                    { text: "But", tension: 0.0, valence: 0.3, duration: 0.3 },
                    { text: "then—", tension: 0.3, valence: 0.1, duration: 0.4 },
                ]
            },
            {
                startTime: 23,
                words: [
                    { text: "RAGE", tension: 0.9, valence: -0.7, duration: 0.8 },
                    { text: "erupts", tension: 0.95, valence: -0.6, duration: 0.6 },
                ]
            },
            {
                startTime: 27,
                words: [
                    { text: "FIRE", tension: 1.0, valence: -0.5, duration: 0.6 },
                    { text: "and", tension: 0.9, valence: -0.4, duration: 0.2 },
                    { text: "FURY", tension: 1.0, valence: -0.6, duration: 0.7 },
                ]
            },
            {
                startTime: 32,
                words: [
                    { text: "slowly", tension: 0.5, valence: -0.3, duration: 0.6 },
                    { text: "fading", tension: 0.3, valence: -0.2, duration: 0.6 },
                ]
            },
            {
                startTime: 36,
                words: [
                    { text: "to", tension: 0.0, valence: 0.0, duration: 0.3 },
                    { text: "stillness", tension: -0.5, valence: 0.1, duration: 0.8 },
                ]
            },
        ]
    }
};


// ═══════════════════════════════════════════════════════════════════════════
// VOICEPATH ENGINE
// ═══════════════════════════════════════════════════════════════════════════

class VoicePath {
    constructor() {
        this.stage = document.getElementById('stage');
        this.playBtn = document.getElementById('btn-play');
        this.playIcon = document.getElementById('play-icon');
        this.timeFill = document.getElementById('time-fill');
        this.demoSelect = document.getElementById('demo-select');
        this.titleEl = document.getElementById('song-title');
        this.artistEl = document.getElementById('song-artist');
        
        this.song = null;
        this.words = [];  // DOM elements
        this.wordData = []; // Flattened word data with absolute times
        this.isPlaying = false;
        this.currentTime = 0;
        this.startTimestamp = null;
        this.animationId = null;
        
        this.init();
    }
    
    init() {
        this.playBtn.addEventListener('click', () => this.toggle());
        this.demoSelect.addEventListener('change', (e) => {
            this.stop();
            this.loadSong(e.target.value);
        });
        
        document.querySelector('.time-bar').addEventListener('click', (e) => {
            if (!this.song) return;
            const rect = e.target.getBoundingClientRect();
            const pct = (e.clientX - rect.left) / rect.width;
            this.seekTo(pct * this.song.duration);
        });
        
        // Load default
        this.loadSong('dayinthelife');
    }
    
    loadSong(id) {
        this.song = SONGS[id];
        if (!this.song) return;
        
        this.titleEl.textContent = this.song.title;
        this.artistEl.textContent = this.song.artist;
        this.currentTime = 0;
        this.timeFill.style.width = '0%';
        
        // Flatten words with absolute times
        this.wordData = [];
        let wordIndex = 0;
        
        for (const line of this.song.lines) {
            let time = line.startTime;
            for (const word of line.words) {
                this.wordData.push({
                    ...word,
                    startTime: time,
                    endTime: time + word.duration,
                    index: wordIndex++,
                    lineStart: line.startTime
                });
                time += word.duration;
            }
            // Mark line end
            this.wordData.push({ lineBreak: true, startTime: time });
        }
        
        this.buildStage();
        this.render();
    }
    
    buildStage() {
        this.stage.innerHTML = '';
        this.words = [];
        
        for (const data of this.wordData) {
            if (data.lineBreak) {
                const br = document.createElement('div');
                br.className = 'line-break';
                this.stage.appendChild(br);
                this.words.push(null);
            } else {
                const el = document.createElement('span');
                el.className = 'word';
                el.textContent = data.text;
                this.stage.appendChild(el);
                this.words.push(el);
            }
        }
    }
    
    toggle() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    play() {
        if (!this.song) return;
        this.isPlaying = true;
        this.startTimestamp = performance.now() - (this.currentTime * 1000);
        this.playIcon.textContent = '❚❚';
        this.animate();
    }
    
    pause() {
        this.isPlaying = false;
        this.playIcon.textContent = '▶';
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    stop() {
        this.pause();
        this.currentTime = 0;
        this.timeFill.style.width = '0%';
        this.render();
    }
    
    seekTo(time) {
        this.currentTime = Math.max(0, Math.min(time, this.song.duration));
        if (this.isPlaying) {
            this.startTimestamp = performance.now() - (this.currentTime * 1000);
        }
        this.render();
    }
    
    animate() {
        if (!this.isPlaying) return;
        
        this.currentTime = (performance.now() - this.startTimestamp) / 1000;
        
        if (this.currentTime >= this.song.duration) {
            this.stop();
            return;
        }
        
        this.timeFill.style.width = (this.currentTime / this.song.duration * 100) + '%';
        this.render();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    render() {
        const t = this.currentTime;
        
        for (let i = 0; i < this.wordData.length; i++) {
            const data = this.wordData[i];
            const el = this.words[i];
            
            if (!el || data.lineBreak) continue;
            
            // Determine state
            const isCurrent = t >= data.startTime && t < data.endTime;
            const isPast = t >= data.endTime;
            const isFuture = t < data.startTime;
            const isVisible = t >= data.lineStart - 0.5; // Show slightly early
            
            // Set classes
            el.classList.toggle('visible', isVisible);
            el.classList.toggle('current', isCurrent);
            el.classList.toggle('past', isPast);
            el.classList.toggle('future', isFuture && isVisible);
            
            if (!isVisible) continue;
            
            // Apply kinematic styling
            this.styleWord(el, data, isCurrent, isPast);
        }
    }
    
    styleWord(el, data, isCurrent, isPast) {
        const { tension, valence } = data;
        
        // SIZE from tension: -1 (small) to +1 (large)
        // Base size 1.5rem, range from 1rem to 3rem
        const size = 1.5 + tension * 1.0;
        
        // VERTICAL OFFSET from valence: -1 (down) to +1 (up)
        // Range: -40px to +40px
        const yOffset = -valence * 40;
        
        // FONT WEIGHT from tension
        // Range: 300 (light) to 800 (bold)
        const weight = Math.round(400 + tension * 300);
        
        // COLOR from both dimensions
        const color = this.getColor(tension, valence);
        
        // LETTER SPACING from tension
        // Tight when calm, spread when intense
        const spacing = tension * 0.05;
        
        // Apply styles
        el.style.fontSize = size + 'rem';
        el.style.transform = `translateY(${yOffset}px)`;
        el.style.fontWeight = weight;
        el.style.color = color;
        el.style.letterSpacing = spacing + 'em';
        
        // Glow for current word
        if (isCurrent) {
            el.style.textShadow = `0 0 30px ${color}, 0 0 60px ${color}`;
        } else {
            el.style.textShadow = 'none';
        }
    }
    
    getColor(tension, valence) {
        // Map tension/valence to color
        // Quadrants:
        //   Top-left (calm positive): soft green #81c784
        //   Top-right (intense positive): gold #ffb74d
        //   Bottom-left (calm negative): indigo #5c6bc0
        //   Bottom-right (intense negative): red #ef5350
        
        // Normalize to 0-1
        const tx = (tension + 1) / 2;  // 0 = calm, 1 = intense
        const vy = (valence + 1) / 2;  // 0 = negative, 1 = positive
        
        // Interpolate colors
        // Top row: green to gold
        const topR = Math.round(129 + (255 - 129) * tx);
        const topG = Math.round(199 + (183 - 199) * tx);
        const topB = Math.round(132 + (77 - 132) * tx);
        
        // Bottom row: indigo to red
        const botR = Math.round(92 + (239 - 92) * tx);
        const botG = Math.round(107 + (83 - 107) * tx);
        const botB = Math.round(192 + (80 - 192) * tx);
        
        // Blend top and bottom based on valence
        const r = Math.round(botR + (topR - botR) * vy);
        const g = Math.round(botG + (topG - botG) * vy);
        const b = Math.round(botB + (topB - botB) * vy);
        
        return `rgb(${r}, ${g}, ${b})`;
    }
}


// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    window.voicePath = new VoicePath();
    console.log('VoicePath v2 — The words ARE the visualization');
});
