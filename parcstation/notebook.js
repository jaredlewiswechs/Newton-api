/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PARCSTATION NOTEBOOK
 * The Spatial Container for Verified Knowledge
 * 
 * OpenDoc + Cyberdog + Hot Sauce + Newton
 * "Built on proof."
 * 
 * © 2026 Jared Lewis · Ada Computing Company · Houston, Texas
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * The Notebook IS the territory.
 * The Stacks ARE the landmarks.
 * The Cards ARE the coordinates.
 * The Trust IS the light.
 * 
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

// ═══════════════════════════════════════════════════════════════════════════════
// DATA MODEL - The OpenDoc Structure
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Trust levels for visual encoding
 */
const TrustLevel = {
    VERIFIED: 'verified',      // 100% - bright glow
    PARTIAL: 'partial',        // 50-99% - medium glow
    DRAFT: 'draft',            // <50% - dim
    UNVERIFIED: 'unverified',  // Live/external - pulsing
    DISPUTED: 'disputed'       // Conflict - red warning
};

/**
 * A Card - the atomic unit of verified knowledge
 */
class Card {
    constructor(config) {
        this.id = config.id || crypto.randomUUID();
        this.claim = config.claim || '';
        this.sources = config.sources || [];
        this.links = config.links || [];
        this.position = config.position || { x: 0, y: 0, z: 0 };
        this.verification = config.verification || {
            status: 'draft',
            confidence: 0,
            verifiedAt: null
        };
        this.metadata = config.metadata || {};
        this.mesh = null; // Three.js mesh reference
    }

    get trustLevel() {
        if (this.verification.status === 'verified') return TrustLevel.VERIFIED;
        if (this.verification.status === 'disputed') return TrustLevel.DISPUTED;
        if (this.verification.confidence >= 0.5) return TrustLevel.PARTIAL;
        if (this.sources.length === 0) return TrustLevel.UNVERIFIED;
        return TrustLevel.DRAFT;
    }
}

/**
 * A Stack - collection of Cards with shared constraints
 */
class Stack {
    constructor(config) {
        this.id = config.id || crypto.randomUUID();
        this.name = config.name || 'Untitled Stack';
        this.description = config.description || '';
        this.cards = new Map();
        this.constraints = config.constraints || [];
        this.position = config.position || { x: 0, y: 0, z: 0 };
        this.color = config.color || 0x4a9eff;
        this.mesh = null;
        this.group = null; // Three.js group for stack + cards
        
        // Add initial cards
        if (config.cards) {
            config.cards.forEach(card => this.addCard(card));
        }
    }

    addCard(cardConfig) {
        const card = cardConfig instanceof Card ? cardConfig : new Card(cardConfig);
        this.cards.set(card.id, card);
        return card;
    }

    get verificationPercent() {
        if (this.cards.size === 0) return 100;
        let verified = 0;
        this.cards.forEach(card => {
            if (card.verification.status === 'verified') verified++;
        });
        return Math.round((verified / this.cards.size) * 100);
    }

    get trustLevel() {
        const pct = this.verificationPercent;
        if (pct === 100) return TrustLevel.VERIFIED;
        if (pct >= 50) return TrustLevel.PARTIAL;
        return TrustLevel.DRAFT;
    }
}

/**
 * A Cartridge - embeddable verified component (OpenDoc Part)
 */
class Cartridge {
    constructor(config) {
        this.id = config.id || crypto.randomUUID();
        this.type = config.type; // 'visual', 'sound', 'data', 'voicepath', etc.
        this.name = config.name || 'Untitled Cartridge';
        this.contract = config.contract || { inputs: [], outputs: [], invariants: [] };
        this.position = config.position || { x: 0, y: 0, z: 0 };
        this.state = config.state || {};
        this.verified = config.verified || false;
        this.mesh = null;
    }
}

/**
 * The Notebook - the spatial container
 */
class Notebook {
    constructor() {
        this.stacks = new Map();
        this.cartridges = new Map();
        this.quickCards = []; // Drafts not yet in a stack
        this.recentQueries = [];
    }

    addStack(stackConfig) {
        const stack = stackConfig instanceof Stack ? stackConfig : new Stack(stackConfig);
        this.stacks.set(stack.id, stack);
        return stack;
    }

    addCartridge(cartridgeConfig) {
        const cartridge = cartridgeConfig instanceof Cartridge ? cartridgeConfig : new Cartridge(cartridgeConfig);
        this.cartridges.set(cartridge.id, cartridge);
        return cartridge;
    }

    addQuickCard(cardConfig) {
        const card = new Card(cardConfig);
        this.quickCards.push(card);
        return card;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// VISUAL ENGINE - Three.js Spatial Rendering
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Trust level to visual properties mapping
 */
const TrustVisuals = {
    [TrustLevel.VERIFIED]: {
        emissive: 0x00ff88,
        emissiveIntensity: 0.5,
        opacity: 1.0,
        pulseSpeed: 0
    },
    [TrustLevel.PARTIAL]: {
        emissive: 0x4a9eff,
        emissiveIntensity: 0.3,
        opacity: 0.9,
        pulseSpeed: 0
    },
    [TrustLevel.DRAFT]: {
        emissive: 0x888888,
        emissiveIntensity: 0.1,
        opacity: 0.6,
        pulseSpeed: 0
    },
    [TrustLevel.UNVERIFIED]: {
        emissive: 0xffaa00,
        emissiveIntensity: 0.3,
        opacity: 0.7,
        pulseSpeed: 2
    },
    [TrustLevel.DISPUTED]: {
        emissive: 0xff0044,
        emissiveIntensity: 0.6,
        opacity: 0.8,
        pulseSpeed: 4
    }
};

/**
 * parcStation - The 3D Spatial Notebook Renderer
 */
class ParcStation {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.notebook = new Notebook();
        
        // Three.js core
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.composer = null;
        
        // Interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedObject = null;
        this.hoveredObject = null;
        
        // Animation
        this.clock = new THREE.Clock();
        this.animationId = null;
        
        // Object registries
        this.meshToData = new Map(); // mesh -> Card/Stack/Cartridge
        this.dataToMesh = new Map(); // id -> mesh
        
        // Initialize
        this.init();
        this.setupLights();
        this.setupGrid();
        this.setupPostProcessing();
        this.bindEvents();
        this.animate();
    }

    // ═══════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════

    init() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a12);
        this.scene.fog = new THREE.FogExp2(0x0a0a12, 0.015);

        // Camera
        this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
        this.camera.position.set(0, 30, 50);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // Controls - fly through!
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 5;
        this.controls.maxDistance = 200;
        this.controls.maxPolarAngle = Math.PI * 0.85;
    }

    setupLights() {
        // Ambient
        const ambient = new THREE.AmbientLight(0x404060, 0.4);
        this.scene.add(ambient);

        // Main directional
        const main = new THREE.DirectionalLight(0xffffff, 0.8);
        main.position.set(20, 40, 20);
        main.castShadow = true;
        main.shadow.mapSize.width = 2048;
        main.shadow.mapSize.height = 2048;
        this.scene.add(main);

        // Accent lights
        const accent1 = new THREE.PointLight(0x4a9eff, 0.5, 100);
        accent1.position.set(-20, 20, -20);
        this.scene.add(accent1);

        const accent2 = new THREE.PointLight(0xa855f7, 0.5, 100);
        accent2.position.set(20, 20, 20);
        this.scene.add(accent2);
    }

    setupGrid() {
        // Ground plane
        const groundGeo = new THREE.PlaneGeometry(200, 200);
        const groundMat = new THREE.MeshStandardMaterial({
            color: 0x111118,
            roughness: 0.9,
            metalness: 0.1
        });
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        // Grid helper
        const grid = new THREE.GridHelper(200, 40, 0x222233, 0x181822);
        grid.position.y = 0.01;
        this.scene.add(grid);

        // Axes indicator (subtle)
        const axesHelper = new THREE.AxesHelper(5);
        axesHelper.position.set(-95, 0.1, -95);
        this.scene.add(axesHelper);
    }

    setupPostProcessing() {
        this.composer = new EffectComposer(this.renderer);
        
        const renderPass = new RenderPass(this.scene, this.camera);
        this.composer.addPass(renderPass);

        // Bloom for trust glow
        const bloomPass = new UnrealBloomPass(
            new THREE.Vector2(this.container.clientWidth, this.container.clientHeight),
            0.5,  // strength
            0.4,  // radius
            0.85  // threshold
        );
        this.composer.addPass(bloomPass);
    }

    // ═══════════════════════════════════════════════════════════════
    // OBJECT CREATION
    // ═══════════════════════════════════════════════════════════════

    createStackMesh(stack) {
        const group = new THREE.Group();
        group.position.set(stack.position.x, stack.position.y, stack.position.z);
        
        const visuals = TrustVisuals[stack.trustLevel];

        // Stack base - rounded box
        const baseGeo = new THREE.BoxGeometry(8, 2, 8, 4, 4, 4);
        const baseMat = new THREE.MeshStandardMaterial({
            color: stack.color,
            roughness: 0.3,
            metalness: 0.7,
            emissive: visuals.emissive,
            emissiveIntensity: visuals.emissiveIntensity,
            transparent: true,
            opacity: visuals.opacity
        });
        const base = new THREE.Mesh(baseGeo, baseMat);
        base.castShadow = true;
        base.receiveShadow = true;
        group.add(base);

        // Stack label (floating text would go here - simplified as sprite)
        const labelCanvas = this.createLabelCanvas(stack.name, stack.verificationPercent);
        const labelTexture = new THREE.CanvasTexture(labelCanvas);
        const labelMat = new THREE.SpriteMaterial({ map: labelTexture, transparent: true });
        const label = new THREE.Sprite(labelMat);
        label.scale.set(8, 2, 1);
        label.position.y = 3;
        group.add(label);

        // Verification indicator ring
        const ringGeo = new THREE.TorusGeometry(5, 0.1, 8, 64);
        const ringMat = new THREE.MeshBasicMaterial({
            color: visuals.emissive,
            transparent: true,
            opacity: 0.6
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = 0.1;
        group.add(ring);

        // Add cards as floating nodes above the stack
        let cardIndex = 0;
        const cardCount = stack.cards.size;
        stack.cards.forEach(card => {
            const cardMesh = this.createCardMesh(card, cardIndex, cardCount);
            cardMesh.position.y = 4 + Math.random() * 2;
            group.add(cardMesh);
            card.mesh = cardMesh;
            this.meshToData.set(cardMesh, card);
            cardIndex++;
        });

        stack.mesh = base;
        stack.group = group;
        this.meshToData.set(base, stack);
        this.dataToMesh.set(stack.id, group);
        
        this.scene.add(group);
        return group;
    }

    createCardMesh(card, index = 0, total = 1) {
        const visuals = TrustVisuals[card.trustLevel];

        // Cards are smaller spheres orbiting the stack
        const angle = (index / total) * Math.PI * 2;
        const radius = 3;
        
        const geo = new THREE.SphereGeometry(0.4, 16, 16);
        const mat = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            roughness: 0.2,
            metalness: 0.8,
            emissive: visuals.emissive,
            emissiveIntensity: visuals.emissiveIntensity * 1.5,
            transparent: true,
            opacity: visuals.opacity
        });
        
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.x = Math.cos(angle) * radius;
        mesh.position.z = Math.sin(angle) * radius;
        mesh.castShadow = true;

        // Store pulse data for unverified cards
        mesh.userData.pulseSpeed = visuals.pulseSpeed;
        mesh.userData.pulsePhase = Math.random() * Math.PI * 2;

        return mesh;
    }

    createCartridgeMesh(cartridge) {
        const visuals = TrustVisuals[cartridge.verified ? TrustLevel.VERIFIED : TrustLevel.UNVERIFIED];

        // Cartridges are distinctive hexagonal prisms
        const geo = new THREE.CylinderGeometry(2, 2, 3, 6);
        const mat = new THREE.MeshStandardMaterial({
            color: this.getCartridgeColor(cartridge.type),
            roughness: 0.2,
            metalness: 0.9,
            emissive: visuals.emissive,
            emissiveIntensity: visuals.emissiveIntensity,
            transparent: true,
            opacity: visuals.opacity
        });

        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(cartridge.position.x, cartridge.position.y + 1.5, cartridge.position.z);
        mesh.castShadow = true;

        // Type icon as floating sprite
        const iconCanvas = this.createCartridgeIcon(cartridge.type);
        const iconTexture = new THREE.CanvasTexture(iconCanvas);
        const iconMat = new THREE.SpriteMaterial({ map: iconTexture, transparent: true });
        const icon = new THREE.Sprite(iconMat);
        icon.scale.set(2, 2, 1);
        icon.position.y = 2.5;
        mesh.add(icon);

        cartridge.mesh = mesh;
        this.meshToData.set(mesh, cartridge);
        this.dataToMesh.set(cartridge.id, mesh);
        
        this.scene.add(mesh);
        return mesh;
    }

    createQuickCardMesh(card) {
        // Quick cards float in the "intake" area
        const visuals = TrustVisuals[TrustLevel.DRAFT];

        const geo = new THREE.BoxGeometry(2, 0.2, 3);
        const mat = new THREE.MeshStandardMaterial({
            color: 0xffffee,
            roughness: 0.5,
            metalness: 0.1,
            emissive: visuals.emissive,
            emissiveIntensity: 0.2,
            transparent: true,
            opacity: 0.8
        });

        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(card.position.x, card.position.y + 0.5, card.position.z);
        mesh.castShadow = true;

        // Needs verification indicator
        const warningGeo = new THREE.ConeGeometry(0.3, 0.6, 3);
        const warningMat = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
        const warning = new THREE.Mesh(warningGeo, warningMat);
        warning.position.y = 0.6;
        warning.rotation.z = Math.PI;
        mesh.add(warning);

        card.mesh = mesh;
        this.meshToData.set(mesh, card);
        
        this.scene.add(mesh);
        return mesh;
    }

    // ═══════════════════════════════════════════════════════════════
    // HELPERS
    // ═══════════════════════════════════════════════════════════════

    createLabelCanvas(text, percent) {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');

        // Background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.roundRect(0, 0, 512, 128, 16);
        ctx.fill();

        // Text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 36px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(text, 256, 50);

        // Verification badge
        const badgeColor = percent === 100 ? '#00ff88' : percent >= 50 ? '#4a9eff' : '#888888';
        ctx.fillStyle = badgeColor;
        ctx.font = '24px system-ui, sans-serif';
        ctx.fillText(`✓ ${percent}%`, 256, 90);

        return canvas;
    }

    createCartridgeIcon(type) {
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');

        const icons = {
            visual: '🎨',
            sound: '🔊',
            data: '📊',
            voicepath: '🎵',
            sequence: '🎬',
            rosetta: '💻',
            document: '📄'
        };

        ctx.font = '64px system-ui';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(icons[type] || '📦', 64, 64);

        return canvas;
    }

    getCartridgeColor(type) {
        const colors = {
            visual: 0xff6b6b,
            sound: 0x4ecdc4,
            data: 0x45b7d1,
            voicepath: 0xa855f7,
            sequence: 0xf7dc6f,
            rosetta: 0x82e0aa,
            document: 0xf8b500
        };
        return colors[type] || 0x888888;
    }

    // ═══════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════

    bindEvents() {
        window.addEventListener('resize', () => this.onResize());
        this.renderer.domElement.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.renderer.domElement.addEventListener('click', (e) => this.onClick(e));
        this.renderer.domElement.addEventListener('dblclick', (e) => this.onDoubleClick(e));
        
        // Drag and drop for adding items
        this.renderer.domElement.addEventListener('dragover', (e) => e.preventDefault());
        this.renderer.domElement.addEventListener('drop', (e) => this.onDrop(e));
    }

    onResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
        this.composer.setSize(width, height);
    }

    onMouseMove(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        // Raycast for hover
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);

        // Reset previous hover
        if (this.hoveredObject && this.hoveredObject.material) {
            this.hoveredObject.material.emissiveIntensity = 
                this.hoveredObject.userData.baseEmissive || 0.3;
        }

        if (intersects.length > 0) {
            const obj = intersects[0].object;
            if (this.meshToData.has(obj)) {
                this.hoveredObject = obj;
                obj.userData.baseEmissive = obj.material.emissiveIntensity;
                obj.material.emissiveIntensity = 0.8;
                this.renderer.domElement.style.cursor = 'pointer';
            }
        } else {
            this.hoveredObject = null;
            this.renderer.domElement.style.cursor = 'default';
        }
    }

    onClick(event) {
        if (this.hoveredObject) {
            const data = this.meshToData.get(this.hoveredObject);
            this.selectObject(data);
            this.dispatchEvent('select', data);
        }
    }

    onDoubleClick(event) {
        if (this.hoveredObject) {
            const data = this.meshToData.get(this.hoveredObject);
            if (data instanceof Stack) {
                this.flyToStack(data);
            }
            this.dispatchEvent('open', data);
        }
    }

    onDrop(event) {
        event.preventDefault();
        const data = event.dataTransfer.getData('application/json');
        if (data) {
            try {
                const item = JSON.parse(data);
                const worldPos = this.screenToWorld(event.clientX, event.clientY);
                item.position = { x: worldPos.x, y: 0, z: worldPos.z };
                
                if (item.type === 'stack') {
                    const stack = this.notebook.addStack(item);
                    this.createStackMesh(stack);
                } else if (item.type === 'cartridge') {
                    const cartridge = this.notebook.addCartridge(item);
                    this.createCartridgeMesh(cartridge);
                } else {
                    const card = this.notebook.addQuickCard(item);
                    this.createQuickCardMesh(card);
                }
                
                this.dispatchEvent('drop', item);
            } catch (e) {
                console.error('Drop parse error:', e);
            }
        }
    }

    screenToWorld(screenX, screenY) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        const x = ((screenX - rect.left) / rect.width) * 2 - 1;
        const y = -((screenY - rect.top) / rect.height) * 2 + 1;
        
        const vector = new THREE.Vector3(x, y, 0.5);
        vector.unproject(this.camera);
        const dir = vector.sub(this.camera.position).normalize();
        const distance = -this.camera.position.y / dir.y;
        const pos = this.camera.position.clone().add(dir.multiplyScalar(distance));
        
        return pos;
    }

    // ═══════════════════════════════════════════════════════════════
    // NAVIGATION
    // ═══════════════════════════════════════════════════════════════

    flyToStack(stack) {
        const target = stack.group.position.clone();
        target.y = 15;
        target.z += 20;

        // Animate camera
        const start = this.camera.position.clone();
        const duration = 1000;
        const startTime = Date.now();

        const animateFly = () => {
            const elapsed = Date.now() - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3); // ease out cubic

            this.camera.position.lerpVectors(start, target, eased);
            this.controls.target.lerp(stack.group.position, eased);
            this.controls.update();

            if (t < 1) {
                requestAnimationFrame(animateFly);
            }
        };

        animateFly();
    }

    flyHome() {
        const target = new THREE.Vector3(0, 30, 50);
        const lookAt = new THREE.Vector3(0, 0, 0);

        const start = this.camera.position.clone();
        const startLook = this.controls.target.clone();
        const duration = 1000;
        const startTime = Date.now();

        const animateFly = () => {
            const elapsed = Date.now() - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);

            this.camera.position.lerpVectors(start, target, eased);
            this.controls.target.lerpVectors(startLook, lookAt, eased);
            this.controls.update();

            if (t < 1) {
                requestAnimationFrame(animateFly);
            }
        };

        animateFly();
    }

    // ═══════════════════════════════════════════════════════════════
    // ANIMATION
    // ═══════════════════════════════════════════════════════════════

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        const time = this.clock.getElapsedTime();
        const delta = this.clock.getDelta();

        // Update controls
        this.controls.update();

        // Animate cards (orbit and pulse)
        this.notebook.stacks.forEach(stack => {
            if (stack.group) {
                let cardIndex = 0;
                stack.cards.forEach(card => {
                    if (card.mesh) {
                        // Gentle orbit
                        const angle = time * 0.2 + (cardIndex / stack.cards.size) * Math.PI * 2;
                        const radius = 3;
                        card.mesh.position.x = Math.cos(angle) * radius;
                        card.mesh.position.z = Math.sin(angle) * radius;
                        
                        // Pulse for unverified
                        if (card.mesh.userData.pulseSpeed > 0) {
                            const pulse = Math.sin(time * card.mesh.userData.pulseSpeed + card.mesh.userData.pulsePhase);
                            card.mesh.material.emissiveIntensity = 0.3 + pulse * 0.3;
                        }
                    }
                    cardIndex++;
                });

                // Gentle stack hover
                stack.group.position.y = Math.sin(time * 0.5) * 0.2;
            }
        });

        // Animate cartridges (slow rotation)
        this.notebook.cartridges.forEach(cartridge => {
            if (cartridge.mesh) {
                cartridge.mesh.rotation.y = time * 0.3;
            }
        });

        // Render with bloom
        this.composer.render();
    }

    // ═══════════════════════════════════════════════════════════════
    // SELECTION & EVENTS
    // ═══════════════════════════════════════════════════════════════

    selectObject(data) {
        this.selectedObject = data;
        // Could add selection outline here
    }

    dispatchEvent(eventName, data) {
        const event = new CustomEvent(`parcstation:${eventName}`, { detail: data });
        this.container.dispatchEvent(event);
    }

    // ═══════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════

    /**
     * Load a notebook state
     */
    loadNotebook(notebookData) {
        // Clear existing
        this.notebook.stacks.forEach(stack => {
            if (stack.group) this.scene.remove(stack.group);
        });
        this.notebook.cartridges.forEach(cartridge => {
            if (cartridge.mesh) this.scene.remove(cartridge.mesh);
        });

        this.notebook = new Notebook();
        this.meshToData.clear();
        this.dataToMesh.clear();

        // Load stacks
        if (notebookData.stacks) {
            notebookData.stacks.forEach(stackData => {
                const stack = this.notebook.addStack(stackData);
                this.createStackMesh(stack);
            });
        }

        // Load cartridges
        if (notebookData.cartridges) {
            notebookData.cartridges.forEach(cartridgeData => {
                const cartridge = this.notebook.addCartridge(cartridgeData);
                this.createCartridgeMesh(cartridge);
            });
        }

        // Load quick cards
        if (notebookData.quickCards) {
            notebookData.quickCards.forEach(cardData => {
                const card = this.notebook.addQuickCard(cardData);
                this.createQuickCardMesh(card);
            });
        }
    }

    /**
     * Export notebook state
     */
    exportNotebook() {
        return {
            stacks: Array.from(this.notebook.stacks.values()).map(s => ({
                id: s.id,
                name: s.name,
                description: s.description,
                position: s.position,
                color: s.color,
                constraints: s.constraints,
                cards: Array.from(s.cards.values()).map(c => ({
                    id: c.id,
                    claim: c.claim,
                    sources: c.sources,
                    links: c.links,
                    verification: c.verification
                }))
            })),
            cartridges: Array.from(this.notebook.cartridges.values()).map(c => ({
                id: c.id,
                type: c.type,
                name: c.name,
                position: c.position,
                contract: c.contract,
                verified: c.verified
            })),
            quickCards: this.notebook.quickCards.map(c => ({
                id: c.id,
                claim: c.claim,
                position: c.position
            }))
        };
    }

    /**
     * Add a stack programmatically
     */
    addStack(config) {
        const stack = this.notebook.addStack(config);
        this.createStackMesh(stack);
        return stack;
    }

    /**
     * Add a cartridge programmatically
     */
    addCartridge(config) {
        const cartridge = this.notebook.addCartridge(config);
        this.createCartridgeMesh(cartridge);
        return cartridge;
    }

    /**
     * Update verification status (triggers visual update)
     */
    updateVerification(id, verification) {
        const mesh = this.dataToMesh.get(id);
        if (mesh) {
            const data = this.meshToData.get(mesh);
            if (data) {
                data.verification = verification;
                // Update visuals
                const visuals = TrustVisuals[data.trustLevel];
                if (mesh.material) {
                    mesh.material.emissive.setHex(visuals.emissive);
                    mesh.material.emissiveIntensity = visuals.emissiveIntensity;
                    mesh.material.opacity = visuals.opacity;
                }
            }
        }
    }

    /**
     * Cleanup
     */
    dispose() {
        cancelAnimationFrame(this.animationId);
        this.renderer.dispose();
        this.controls.dispose();
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
    ParcStation,
    Notebook,
    Stack,
    Card,
    Cartridge,
    TrustLevel
};
