/**
 * ═══════════════════════════════════════════════════════════════════════════
 * VOICEPATH — See What You Hear
 * Kinematic Music Visualization Engine
 * 
 * Newton/Ada Verified Computation
 * parcRI Research — 2026
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The trajectory IS the meaning.
 * The comet traces the feeling.
 * The envelope shows the possible.
 * 
 * ═══════════════════════════════════════════════════════════════════════════
 */

class VoicePath {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // State
        this.song = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.startTimestamp = null;
        this.pausedAt = 0;
        
        // Trail history (positions over time)
        this.trail = [];
        this.maxTrailLength = 100;
        
        // Animation
        this.animationId = null;
        
        // Visual settings
        this.colors = {
            background: '#12121a',
            grid: 'rgba(255, 255, 255, 0.05)',
            axes: 'rgba(255, 255, 255, 0.15)',
            envelope: 'rgba(168, 85, 247, 0.1)',
            envelopeBorder: 'rgba(168, 85, 247, 0.3)',
            trail: 'rgba(74, 158, 255, 0.6)',
            trailGradientEnd: 'rgba(168, 85, 247, 0.1)',
            comet: '#4a9eff',
            cometGlow: 'rgba(74, 158, 255, 0.5)',
            text: '#e8e8f0'
        };
        
        // Initialize
        this.setupCanvas();
        this.bindEvents();
        
        // Load default demo
        this.loadSong('dayinthelife');
    }
    
    // ═══════════════════════════════════════════════════════════════
    // SETUP
    // ═══════════════════════════════════════════════════════════════
    
    setupCanvas() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // High DPI support
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        this.ctx.scale(dpr, dpr);
        
        this.width = rect.width;
        this.height = rect.height;
        
        // Coordinate system: center origin, normalized -1 to 1
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
        this.scale = Math.min(this.width, this.height) * 0.4;
        
        // Redraw if we have a song
        if (this.song) {
            this.render();
        }
    }
    
    bindEvents() {
        // Play button
        document.getElementById('btn-play').addEventListener('click', () => {
            if (this.isPlaying) {
                this.pause();
            } else {
                this.play();
            }
        });
        
        // Stop button
        document.getElementById('btn-stop').addEventListener('click', () => {
            this.stop();
        });
        
        // Demo selector
        document.getElementById('demo-select').addEventListener('change', (e) => {
            this.stop();
            this.loadSong(e.target.value);
        });
        
        // Progress bar click
        document.querySelector('.progress-bar').addEventListener('click', (e) => {
            if (!this.song) return;
            const rect = e.target.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            this.seekTo(percent * this.song.duration);
        });
    }
    
    // ═══════════════════════════════════════════════════════════════
    // SONG MANAGEMENT
    // ═══════════════════════════════════════════════════════════════
    
    loadSong(songId) {
        if (!DEMO_SONGS[songId]) {
            console.error(`Song not found: ${songId}`);
            return;
        }
        
        this.song = DEMO_SONGS[songId];
        this.currentTime = 0;
        this.trail = [];
        
        // Update UI
        document.getElementById('song-title').textContent = this.song.title;
        document.getElementById('song-artist').textContent = this.song.artist;
        document.getElementById('time-total').textContent = this.formatTime(this.song.duration);
        document.getElementById('time-current').textContent = '0:00';
        document.getElementById('progress-fill').style.width = '0%';
        
        // Initial render
        this.render();
    }
    
    // ═══════════════════════════════════════════════════════════════
    // PLAYBACK CONTROL
    // ═══════════════════════════════════════════════════════════════
    
    play() {
        if (!this.song) return;
        
        this.isPlaying = true;
        this.startTimestamp = performance.now() - (this.pausedAt * 1000);
        
        // Update UI
        document.getElementById('btn-play').innerHTML = '<span class="play-icon">❚❚</span>';
        document.querySelector('.visualization-container').classList.add('playing');
        
        // Start animation loop
        this.animate();
    }
    
    pause() {
        this.isPlaying = false;
        this.pausedAt = this.currentTime;
        
        // Update UI
        document.getElementById('btn-play').innerHTML = '<span class="play-icon">▶</span>';
        document.querySelector('.visualization-container').classList.remove('playing');
        
        // Stop animation
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    stop() {
        this.pause();
        this.currentTime = 0;
        this.pausedAt = 0;
        this.trail = [];
        
        // Update UI
        document.getElementById('time-current').textContent = '0:00';
        document.getElementById('progress-fill').style.width = '0%';
        document.getElementById('current-lyric').classList.remove('visible');
        
        this.render();
    }
    
    seekTo(time) {
        this.currentTime = Math.max(0, Math.min(time, this.song.duration));
        this.pausedAt = this.currentTime;
        
        if (this.isPlaying) {
            this.startTimestamp = performance.now() - (this.currentTime * 1000);
        }
        
        // Rebuild trail up to this point
        this.rebuildTrail();
        this.render();
    }
    
    // ═══════════════════════════════════════════════════════════════
    // ANIMATION LOOP
    // ═══════════════════════════════════════════════════════════════
    
    animate() {
        if (!this.isPlaying) return;
        
        // Calculate current time
        const now = performance.now();
        this.currentTime = (now - this.startTimestamp) / 1000;
        
        // Check for end of song
        if (this.currentTime >= this.song.duration) {
            this.stop();
            return;
        }
        
        // Update trail
        const pos = this.getPositionAtTime(this.currentTime);
        if (pos) {
            this.trail.push({
                x: pos.x,
                y: pos.y,
                time: this.currentTime
            });
            
            // Trim trail
            if (this.trail.length > this.maxTrailLength) {
                this.trail.shift();
            }
        }
        
        // Update UI
        this.updateUI();
        
        // Render
        this.render();
        
        // Continue loop
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    updateUI() {
        // Time display
        document.getElementById('time-current').textContent = this.formatTime(this.currentTime);
        
        // Progress bar
        const percent = (this.currentTime / this.song.duration) * 100;
        document.getElementById('progress-fill').style.width = percent + '%';
        
        // Current lyric
        const lyric = this.getCurrentLyric();
        const lyricEl = document.getElementById('current-lyric');
        if (lyric && lyric.text && lyric.text !== '...') {
            lyricEl.textContent = lyric.text;
            lyricEl.classList.add('visible');
        } else {
            lyricEl.classList.remove('visible');
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // POSITION CALCULATION
    // ═══════════════════════════════════════════════════════════════
    
    getCurrentLyric() {
        if (!this.song) return null;
        
        let current = null;
        for (const lyric of this.song.lyrics) {
            if (lyric.time <= this.currentTime) {
                current = lyric;
            } else {
                break;
            }
        }
        return current;
    }
    
    getNextLyric() {
        if (!this.song) return null;
        
        for (const lyric of this.song.lyrics) {
            if (lyric.time > this.currentTime) {
                return lyric;
            }
        }
        return null;
    }
    
    getPositionAtTime(time) {
        if (!this.song) return null;
        
        // Find the two lyrics we're between
        let prev = null;
        let next = null;
        
        for (let i = 0; i < this.song.lyrics.length; i++) {
            if (this.song.lyrics[i].time <= time) {
                prev = this.song.lyrics[i];
                next = this.song.lyrics[i + 1] || prev;
            }
        }
        
        if (!prev) {
            prev = this.song.lyrics[0];
            next = this.song.lyrics[1] || prev;
        }
        
        // Interpolate between positions (using smoothstep for Bézier-like curve)
        const duration = next.time - prev.time;
        let t = duration > 0 ? (time - prev.time) / duration : 0;
        t = Math.max(0, Math.min(1, t));
        
        // Smoothstep interpolation
        t = t * t * (3 - 2 * t);
        
        return {
            x: prev.tension + (next.tension - prev.tension) * t,
            y: prev.valence + (next.valence - prev.valence) * t,
            lyric: prev
        };
    }
    
    rebuildTrail() {
        this.trail = [];
        const step = 0.1; // seconds
        for (let t = 0; t < this.currentTime; t += step) {
            const pos = this.getPositionAtTime(t);
            if (pos) {
                this.trail.push({ x: pos.x, y: pos.y, time: t });
            }
        }
        
        // Trim to max length
        while (this.trail.length > this.maxTrailLength) {
            this.trail.shift();
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // RENDERING
    // ═══════════════════════════════════════════════════════════════
    
    render() {
        const ctx = this.ctx;
        
        // Clear
        ctx.fillStyle = this.colors.background;
        ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw layers
        this.drawGrid();
        this.drawAxes();
        this.drawEnvelope();
        this.drawTrail();
        this.drawComet();
        this.drawLyricMarkers();
    }
    
    drawGrid() {
        const ctx = this.ctx;
        ctx.strokeStyle = this.colors.grid;
        ctx.lineWidth = 1;
        
        const gridCount = 10;
        const gridSpacing = this.scale * 2 / gridCount;
        
        for (let i = -gridCount / 2; i <= gridCount / 2; i++) {
            const offset = i * gridSpacing;
            
            // Vertical lines
            ctx.beginPath();
            ctx.moveTo(this.centerX + offset, this.centerY - this.scale);
            ctx.lineTo(this.centerX + offset, this.centerY + this.scale);
            ctx.stroke();
            
            // Horizontal lines
            ctx.beginPath();
            ctx.moveTo(this.centerX - this.scale, this.centerY + offset);
            ctx.lineTo(this.centerX + this.scale, this.centerY + offset);
            ctx.stroke();
        }
    }
    
    drawAxes() {
        const ctx = this.ctx;
        ctx.strokeStyle = this.colors.axes;
        ctx.lineWidth = 2;
        
        // X axis (tension)
        ctx.beginPath();
        ctx.moveTo(this.centerX - this.scale - 20, this.centerY);
        ctx.lineTo(this.centerX + this.scale + 20, this.centerY);
        ctx.stroke();
        
        // Y axis (valence)
        ctx.beginPath();
        ctx.moveTo(this.centerX, this.centerY - this.scale - 20);
        ctx.lineTo(this.centerX, this.centerY + this.scale + 20);
        ctx.stroke();
        
        // Axis arrows
        ctx.fillStyle = this.colors.axes;
        
        // Right arrow (intense)
        ctx.beginPath();
        ctx.moveTo(this.centerX + this.scale + 20, this.centerY);
        ctx.lineTo(this.centerX + this.scale + 10, this.centerY - 5);
        ctx.lineTo(this.centerX + this.scale + 10, this.centerY + 5);
        ctx.fill();
        
        // Up arrow (positive)
        ctx.beginPath();
        ctx.moveTo(this.centerX, this.centerY - this.scale - 20);
        ctx.lineTo(this.centerX - 5, this.centerY - this.scale - 10);
        ctx.lineTo(this.centerX + 5, this.centerY - this.scale - 10);
        ctx.fill();
    }
    
    drawEnvelope() {
        if (!this.song || !this.song.envelope) return;
        
        const ctx = this.ctx;
        const env = this.song.envelope;
        
        // Draw envelope ellipse
        const cx = this.centerX + env.center.x * this.scale;
        const cy = this.centerY - env.center.y * this.scale; // Y is inverted
        const rx = env.radiusX * this.scale;
        const ry = env.radiusY * this.scale;
        
        // Fill
        ctx.fillStyle = this.colors.envelope;
        ctx.beginPath();
        ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Border
        ctx.strokeStyle = this.colors.envelopeBorder;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
    }
    
    drawTrail() {
        if (this.trail.length < 2) return;
        
        const ctx = this.ctx;
        
        // Draw trail as gradient path
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        for (let i = 1; i < this.trail.length; i++) {
            const prev = this.trail[i - 1];
            const curr = this.trail[i];
            
            // Fade based on position in trail
            const alpha = (i / this.trail.length) * 0.8;
            
            // Convert to canvas coordinates
            const x1 = this.centerX + prev.x * this.scale;
            const y1 = this.centerY - prev.y * this.scale;
            const x2 = this.centerX + curr.x * this.scale;
            const y2 = this.centerY - curr.y * this.scale;
            
            // Draw segment
            ctx.strokeStyle = `rgba(74, 158, 255, ${alpha})`;
            ctx.lineWidth = 2 + alpha * 4;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
    }
    
    drawComet() {
        const pos = this.getPositionAtTime(this.currentTime);
        if (!pos) return;
        
        const ctx = this.ctx;
        const x = this.centerX + pos.x * this.scale;
        const y = this.centerY - pos.y * this.scale;
        
        // Outer glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 30);
        gradient.addColorStop(0, this.colors.cometGlow);
        gradient.addColorStop(1, 'rgba(74, 158, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, 30, 0, Math.PI * 2);
        ctx.fill();
        
        // Inner comet
        ctx.fillStyle = this.colors.comet;
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.fill();
        
        // Bright center
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    drawLyricMarkers() {
        if (!this.song) return;
        
        const ctx = this.ctx;
        
        // Draw small dots at each lyric position
        for (const lyric of this.song.lyrics) {
            // Skip if in the future
            if (lyric.time > this.currentTime + 5) continue;
            
            const x = this.centerX + lyric.tension * this.scale;
            const y = this.centerY - lyric.valence * this.scale;
            
            // Fade based on how far in the past
            const age = this.currentTime - lyric.time;
            const alpha = age > 0 ? Math.max(0.1, 0.5 - age * 0.05) : 0.3;
            
            ctx.fillStyle = `rgba(168, 85, 247, ${alpha})`;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // UTILITIES
    // ═══════════════════════════════════════════════════════════════
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Convert semantic coordinates to canvas coordinates
    toCanvas(tension, valence) {
        return {
            x: this.centerX + tension * this.scale,
            y: this.centerY - valence * this.scale
        };
    }
    
    // Convert canvas coordinates to semantic coordinates
    toSemantic(canvasX, canvasY) {
        return {
            tension: (canvasX - this.centerX) / this.scale,
            valence: -(canvasY - this.centerY) / this.scale
        };
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    window.voicePath = new VoicePath('voicepath-canvas');
    console.log('VoicePath initialized — See what you hear');
});
