/**
 * 3D Skin & Capes WebGL Studio Module
 * Built on Three.js & SkinView3D
 * Supports:
 *  - 3D Walking, Running, Idle & Waving Animations
 *  - Dynamic Classic (4px - Steve) vs Slim (3px - Alex) Model Switching
 *  - Custom Cape & Elytra Injection with Multi-Texture Support
 *  - Interactive OrbitControls, Auto-Rotation & Real-time Canvas Rendering
 *  - Direct File Upload & Live Username Skin Fetching
 */

export class SkinViewerStudio {
  constructor(options = {}) {
    this.canvasId = options.canvasId || 'skin-studio-3d-canvas';
    this.width = options.width || 280;
    this.height = options.height || 340;
    this.username = options.username || 'Steve';
    this.model = options.model || 'classic';
    this.capeUrl = options.capeUrl || 'capes/sir_founder.png';
    this.isSpinning = options.isSpinning !== undefined ? options.isSpinning : true;
    this.isWalking = options.isWalking !== undefined ? options.isWalking : true;
    this.hasElytra = options.hasElytra !== undefined ? options.hasElytra : false;
    this.viewer = null;
    this.animation = null;
    this.currentAnimationType = 'walking';
  }

  /**
   * Initializes the WebGL canvas and loads initial skin/cape models.
   */
  init() {
    const canvas = typeof this.canvasId === 'string' 
      ? document.getElementById(this.canvasId) 
      : this.canvasId;
    if (!canvas) {
      console.warn(`[SkinViewerStudio] Canvas '${this.canvasId}' not found.`);
      return false;
    }

    if (typeof skinview3d === 'undefined') {
      console.warn('[SkinViewerStudio] skinview3d library not loaded yet.');
      return false;
    }

    if (this.viewer) {
      this.dispose();
    }

    try {
      const cleanUser = encodeURIComponent(this.username || 'Steve');
      const skinUrl = (this.username.toLowerCase() === 'steve')
        ? 'skins/steve.png'
        : `https://mc-heads.net/skin/${cleanUser}`;

      this.viewer = new skinview3d.SkinViewer({
        canvas: canvas,
        width: this.width,
        height: this.height,
        skin: skinUrl
      });

      this.viewer.camera.position.set(0, 0, 65);
      this.viewer.playerObject.rotation.y = Math.PI * 0.95;
      this.viewer.autoRotate = this.isSpinning;
      this.viewer.autoRotateSpeed = 1.2;

      // Load Cape if provided
      if (this.capeUrl) {
        this.loadCape(this.capeUrl, { hasElytra: this.hasElytra });
      }

      // Start animation
      if (this.isWalking) {
        this.setAnimation('walking');
      }

      return true;
    } catch (err) {
      console.error('[SkinViewerStudio] Initialization error:', err);
      return false;
    }
  }

  /**
   * Loads a new skin texture from URL or data URI.
   */
  async loadSkin(skinUrlOrData, options = {}) {
    if (!this.viewer) return;
    const modelType = (options.model || this.model) === 'slim' ? 'slim' : 'default';
    try {
      await this.viewer.loadSkin(skinUrlOrData, { model: modelType });
    } catch (err) {
      console.warn('[SkinViewerStudio] Skin load error, fallback to steve.png:', err);
      try {
        await this.viewer.loadSkin('skins/steve.png', { model: modelType });
      } catch (e) {}
    }
  }

  /**
   * Loads a custom cape or elytra texture.
   */
  async loadCape(capeUrl, options = {}) {
    if (!this.viewer || !capeUrl) return;
    const hasElytra = options.hasElytra !== undefined ? options.hasElytra : this.hasElytra;
    try {
      this.viewer.playerObject.backEquipment = hasElytra ? 'elytra' : 'cape';
      await this.viewer.loadCape(capeUrl, {
        backEquipment: hasElytra ? 'elytra' : 'cape'
      });
    } catch (err) {
      console.warn('[SkinViewerStudio] Cape load error:', err);
    }
  }

  /**
   * Sets the 3D animation mode ('walking', 'running', 'idle', 'flying', 'wave', 'none').
   */
  setAnimation(animType = 'walking') {
    if (!this.viewer) return;
    this.currentAnimationType = animType;

    if (this.animation) {
      this.animation.paused = true;
    }

    if (animType === 'none') {
      this.isWalking = false;
      return;
    }

    this.isWalking = true;
    try {
      if (animType === 'running' && skinview3d.RunningAnimation) {
        this.animation = this.viewer.animations.add(skinview3d.RunningAnimation);
        this.animation.speed = 1.0;
      } else if (animType === 'idle' && skinview3d.IdleAnimation) {
        this.animation = this.viewer.animations.add(skinview3d.IdleAnimation);
        this.animation.speed = 0.5;
      } else if (animType === 'flying' && skinview3d.FlyingAnimation) {
        this.animation = this.viewer.animations.add(skinview3d.FlyingAnimation);
        this.animation.speed = 0.8;
      } else if (skinview3d.WalkingAnimation) {
        this.animation = this.viewer.animations.add(skinview3d.WalkingAnimation);
        this.animation.speed = 0.8;
      }
    } catch (err) {
      console.warn('[SkinViewerStudio] Animation setting error:', err);
    }
  }

  /**
   * Switches character model between 'classic' (4px Steve) and 'slim' (3px Alex).
   */
  setModel(model = 'classic') {
    this.model = model === 'slim' ? 'slim' : 'classic';
    if (!this.viewer) return;

    const cleanUser = encodeURIComponent(this.username || 'Steve');
    const skinUrl = (this.username.toLowerCase() === 'steve')
      ? 'skins/steve.png'
      : `https://mc-heads.net/skin/${cleanUser}`;

    this.loadSkin(skinUrl, { model: this.model });
  }

  /**
   * Toggles auto-rotation (spinning).
   */
  toggleSpin(forceState) {
    if (!this.viewer) return this.isSpinning;
    this.isSpinning = forceState !== undefined ? forceState : !this.isSpinning;
    this.viewer.autoRotate = this.isSpinning;
    return this.isSpinning;
  }

  /**
   * Toggles animation playback.
   */
  toggleAnimation(forceState) {
    if (!this.viewer) return this.isWalking;
    this.isWalking = forceState !== undefined ? forceState : !this.isWalking;

    if (this.isWalking) {
      if (this.animation) {
        this.animation.paused = false;
      } else {
        this.setAnimation(this.currentAnimationType);
      }
    } else {
      if (this.animation) {
        this.animation.paused = true;
      }
    }
    return this.isWalking;
  }

  /**
   * Toggles between Cape and Elytra back equipment.
   */
  toggleElytra(forceState) {
    this.hasElytra = forceState !== undefined ? forceState : !this.hasElytra;
    if (this.viewer && this.capeUrl) {
      this.loadCape(this.capeUrl, { hasElytra: this.hasElytra });
    }
    return this.hasElytra;
  }

  /**
   * Safely disposes Three.js WebGL context and event listeners.
   */
  dispose() {
    if (this.viewer) {
      try {
        if (typeof this.viewer.dispose === 'function') {
          this.viewer.dispose();
        }
      } catch (e) {}
      this.viewer = null;
      this.animation = null;
    }
  }
}

// Expose on window for vanilla script compatibility
if (typeof window !== 'undefined') {
  window.SkinViewerStudio = SkinViewerStudio;
}

export default SkinViewerStudio;
