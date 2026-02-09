/* ═══════════════════════════════════════════════════════════════
   parcStation WebGL Background
   Animated Aurora + Floating Particles + Mesh Grid
   Apple HIG 2026 Liquid Glass Enhancement
   ═══════════════════════════════════════════════════════════════ */

class WebGLBackground {
    constructor() {
        this.canvas = null;
        this.gl = null;
        this.program = null;
        this.startTime = Date.now();
        this.mouse = { x: 0.5, y: 0.5 };
        this.targetMouse = { x: 0.5, y: 0.5 };
        this.particles = [];
        this.particleCanvas = null;
        this.particleCtx = null;
        
        this.init();
    }
    
    init() {
        // Create WebGL canvas for aurora
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'webgl-bg';
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        `;
        document.body.prepend(this.canvas);
        
        // Create 2D canvas for particles
        this.particleCanvas = document.createElement('canvas');
        this.particleCanvas.id = 'particle-bg';
        this.particleCanvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            opacity: 0.6;
        `;
        document.body.prepend(this.particleCanvas);
        this.particleCtx = this.particleCanvas.getContext('2d');
        
        // Initialize WebGL
        this.gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');
        if (!this.gl) {
            console.warn('WebGL not supported, falling back to CSS');
            this.fallbackCSS();
            return;
        }
        
        this.resize();
        this.initShaders();
        this.initParticles();
        this.bindEvents();
        this.animate();
    }
    
    fallbackCSS() {
        // CSS fallback for non-WebGL browsers
        const fallback = document.createElement('div');
        fallback.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(ellipse at 30% 20%, rgba(10, 132, 255, 0.15) 0%, transparent 50%),
                        radial-gradient(ellipse at 70% 80%, rgba(48, 209, 88, 0.1) 0%, transparent 50%),
                        #000;
        `;
        document.body.prepend(fallback);
    }
    
    initShaders() {
        const vertexShaderSource = `
            attribute vec2 a_position;
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
        `;
        
        // Aurora shader inspired by Apple's visionOS aesthetic
        const fragmentShaderSource = `
            precision mediump float;
            
            uniform vec2 u_resolution;
            uniform float u_time;
            uniform vec2 u_mouse;
            
            // Simplex noise function
            vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
            vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
            vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }
            
            float snoise(vec2 v) {
                const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                                   -0.577350269189626, 0.024390243902439);
                vec2 i  = floor(v + dot(v, C.yy));
                vec2 x0 = v - i + dot(i, C.xx);
                vec2 i1;
                i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
                vec4 x12 = x0.xyxy + C.xxzz;
                x12.xy -= i1;
                i = mod289(i);
                vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
                    + i.x + vec3(0.0, i1.x, 1.0));
                vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
                    dot(x12.zw,x12.zw)), 0.0);
                m = m*m;
                m = m*m;
                vec3 x = 2.0 * fract(p * C.www) - 1.0;
                vec3 h = abs(x) - 0.5;
                vec3 ox = floor(x + 0.5);
                vec3 a0 = x - ox;
                m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
                vec3 g;
                g.x = a0.x * x0.x + h.x * x0.y;
                g.yz = a0.yz * x12.xz + h.yz * x12.yw;
                return 130.0 * dot(m, g);
            }
            
            void main() {
                vec2 uv = gl_FragCoord.xy / u_resolution.xy;
                vec2 p = uv * 2.0 - 1.0;
                p.x *= u_resolution.x / u_resolution.y;
                
                float t = u_time * 0.15;
                
                // Multiple noise layers for aurora effect
                float n1 = snoise(vec2(p.x * 0.8 + t * 0.5, p.y * 0.5 + t * 0.3)) * 0.5 + 0.5;
                float n2 = snoise(vec2(p.x * 1.2 - t * 0.3, p.y * 0.8 + t * 0.2)) * 0.5 + 0.5;
                float n3 = snoise(vec2(p.x * 0.5 + t * 0.2, p.y * 1.0 - t * 0.4)) * 0.5 + 0.5;
                
                // Mouse influence
                float mouseDist = length(uv - u_mouse);
                float mouseInfluence = smoothstep(0.5, 0.0, mouseDist) * 0.3;
                
                // Apple system colors (blue, green, purple)
                vec3 blue = vec3(0.04, 0.52, 1.0);    // #0A84FF
                vec3 green = vec3(0.19, 0.82, 0.35);  // #30D158
                vec3 purple = vec3(0.75, 0.35, 0.95); // #BF5AF2
                vec3 cyan = vec3(0.39, 0.82, 1.0);    // #64D2FF
                
                // Mix colors based on noise
                vec3 color = mix(blue, cyan, n1);
                color = mix(color, green, n2 * 0.5);
                color = mix(color, purple, n3 * 0.3);
                
                // Add mouse glow
                color += blue * mouseInfluence;
                
                // Gradient mask - fade towards edges and bottom
                float mask = smoothstep(0.0, 0.3, uv.y) * smoothstep(1.0, 0.7, uv.y);
                mask *= smoothstep(0.0, 0.2, uv.x) * smoothstep(1.0, 0.8, uv.x);
                
                // Apply intensity (very subtle)
                float intensity = 0.08 + mouseInfluence * 0.5;
                color *= intensity * mask;
                
                // Add subtle vignette
                float vignette = 1.0 - length(p) * 0.3;
                color *= vignette;
                
                gl_FragColor = vec4(color, 1.0);
            }
        `;
        
        // Compile shaders
        const vertexShader = this.compileShader(this.gl.VERTEX_SHADER, vertexShaderSource);
        const fragmentShader = this.compileShader(this.gl.FRAGMENT_SHADER, fragmentShaderSource);
        
        // Create program
        this.program = this.gl.createProgram();
        this.gl.attachShader(this.program, vertexShader);
        this.gl.attachShader(this.program, fragmentShader);
        this.gl.linkProgram(this.program);
        
        if (!this.gl.getProgramParameter(this.program, this.gl.LINK_STATUS)) {
            console.error('Program link error:', this.gl.getProgramInfoLog(this.program));
            return;
        }
        
        this.gl.useProgram(this.program);
        
        // Set up geometry (full-screen quad)
        const positions = new Float32Array([
            -1, -1,
             1, -1,
            -1,  1,
             1,  1
        ]);
        
        const buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, positions, this.gl.STATIC_DRAW);
        
        const positionLocation = this.gl.getAttribLocation(this.program, 'a_position');
        this.gl.enableVertexAttribArray(positionLocation);
        this.gl.vertexAttribPointer(positionLocation, 2, this.gl.FLOAT, false, 0, 0);
        
        // Get uniform locations
        this.uniforms = {
            resolution: this.gl.getUniformLocation(this.program, 'u_resolution'),
            time: this.gl.getUniformLocation(this.program, 'u_time'),
            mouse: this.gl.getUniformLocation(this.program, 'u_mouse')
        };
    }
    
    compileShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);
        
        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', this.gl.getShaderInfoLog(shader));
            this.gl.deleteShader(shader);
            return null;
        }
        
        return shader;
    }
    
    initParticles() {
        const count = 50;
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random(),
                y: Math.random(),
                size: Math.random() * 2 + 1,
                speedX: (Math.random() - 0.5) * 0.0003,
                speedY: (Math.random() - 0.5) * 0.0003,
                opacity: Math.random() * 0.5 + 0.2,
                pulse: Math.random() * Math.PI * 2
            });
        }
    }
    
    updateParticles() {
        const w = this.particleCanvas.width;
        const h = this.particleCanvas.height;
        const time = Date.now() * 0.001;
        
        this.particleCtx.clearRect(0, 0, w, h);
        
        this.particles.forEach(p => {
            // Update position
            p.x += p.speedX;
            p.y += p.speedY;
            
            // Wrap around
            if (p.x < 0) p.x = 1;
            if (p.x > 1) p.x = 0;
            if (p.y < 0) p.y = 1;
            if (p.y > 1) p.y = 0;
            
            // Pulsing opacity
            const pulseOpacity = p.opacity * (0.7 + 0.3 * Math.sin(time * 2 + p.pulse));
            
            // Draw particle
            const x = p.x * w;
            const y = p.y * h;
            
            // Glow effect
            const gradient = this.particleCtx.createRadialGradient(x, y, 0, x, y, p.size * 4);
            gradient.addColorStop(0, `rgba(10, 132, 255, ${pulseOpacity})`);
            gradient.addColorStop(0.5, `rgba(10, 132, 255, ${pulseOpacity * 0.3})`);
            gradient.addColorStop(1, 'rgba(10, 132, 255, 0)');
            
            this.particleCtx.fillStyle = gradient;
            this.particleCtx.beginPath();
            this.particleCtx.arc(x, y, p.size * 4, 0, Math.PI * 2);
            this.particleCtx.fill();
            
            // Core
            this.particleCtx.fillStyle = `rgba(255, 255, 255, ${pulseOpacity})`;
            this.particleCtx.beginPath();
            this.particleCtx.arc(x, y, p.size, 0, Math.PI * 2);
            this.particleCtx.fill();
        });
        
        // Draw connecting lines between nearby particles
        this.particleCtx.strokeStyle = 'rgba(10, 132, 255, 0.1)';
        this.particleCtx.lineWidth = 0.5;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = (this.particles[i].x - this.particles[j].x) * w;
                const dy = (this.particles[i].y - this.particles[j].y) * h;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 150) {
                    const opacity = (1 - dist / 150) * 0.15;
                    this.particleCtx.strokeStyle = `rgba(10, 132, 255, ${opacity})`;
                    this.particleCtx.beginPath();
                    this.particleCtx.moveTo(this.particles[i].x * w, this.particles[i].y * h);
                    this.particleCtx.lineTo(this.particles[j].x * w, this.particles[j].y * h);
                    this.particleCtx.stroke();
                }
            }
        }
    }
    
    resize() {
        const dpr = window.devicePixelRatio || 1;
        const w = window.innerWidth;
        const h = window.innerHeight;
        
        this.canvas.width = w * dpr;
        this.canvas.height = h * dpr;
        this.canvas.style.width = w + 'px';
        this.canvas.style.height = h + 'px';
        
        this.particleCanvas.width = w * dpr;
        this.particleCanvas.height = h * dpr;
        this.particleCanvas.style.width = w + 'px';
        this.particleCanvas.style.height = h + 'px';
        this.particleCtx.scale(dpr, dpr);
        
        if (this.gl) {
            this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        }
    }
    
    bindEvents() {
        window.addEventListener('resize', () => this.resize());
        
        document.addEventListener('mousemove', (e) => {
            this.targetMouse.x = e.clientX / window.innerWidth;
            this.targetMouse.y = 1.0 - e.clientY / window.innerHeight;
        });
    }
    
    animate() {
        if (!this.gl) return;
        
        // Smooth mouse follow
        this.mouse.x += (this.targetMouse.x - this.mouse.x) * 0.05;
        this.mouse.y += (this.targetMouse.y - this.mouse.y) * 0.05;
        
        const time = (Date.now() - this.startTime) * 0.001;
        
        // Update WebGL uniforms
        this.gl.uniform2f(this.uniforms.resolution, this.canvas.width, this.canvas.height);
        this.gl.uniform1f(this.uniforms.time, time);
        this.gl.uniform2f(this.uniforms.mouse, this.mouse.x, this.mouse.y);
        
        // Draw
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4);
        
        // Update particles
        this.updateParticles();
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize on DOM ready with error handling
function initWebGLBackground() {
    try {
        new WebGLBackground();
    } catch (e) {
        console.warn('WebGL background failed to initialize:', e);
        // Create CSS fallback
        const fallback = document.createElement('div');
        fallback.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(ellipse at 30% 20%, rgba(10, 132, 255, 0.15) 0%, transparent 50%),
                        radial-gradient(ellipse at 70% 80%, rgba(48, 209, 88, 0.1) 0%, transparent 50%),
                        #000;
        `;
        document.body.prepend(fallback);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWebGLBackground);
} else {
    initWebGLBackground();
}
