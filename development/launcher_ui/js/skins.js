// =============================================================================
// 10. 3D SKIN & CAPES STUDIO (100% PARITY WITH WEB PLATFORM)
// =============================================================================
const PRESET_SKINS = [
  { id: "steve", name: "Steve (Classic Vanilla)", category: "Default / OG", username: "Steve" },
  { id: "siranmed", name: "SirAhmed (Creator Edition)", category: "SIR Developer", username: "SirAhmed" },
  { id: "technoblade", name: "Technoblade (The Blade)", category: "Legendary / PvP", username: "Technoblade" },
  { id: "dream", name: "Dream (Speedrun Legend)", category: "Speedrun / Competitive", username: "Dream" },
  { id: "skeppy", name: "Skeppy (Diamond Skeppy)", category: "Content / Trolling", username: "Skeppy" },
  { id: "sparklez", name: "CaptainSparklez (Jordan)", category: "OG Veteran / Music", username: "CaptainSparklez" },
  { id: "illumina", name: "Illumina (Speedrun Master)", category: "Speedrun / Fantasy", username: "Illumina" },
  { id: "grian", name: "Grian (Master Builder)", category: "Creative / Builder", username: "Grian" },
  { id: "mumbo", name: "Mumbo Jumbo (Redstone)", category: "Redstone / Engineering", username: "Mumbo" }
];

const PRESET_CAPES = [
  { 
    id: "sir_founder", 
    name: "SIR Founder Obsidian Neon", 
    tag: "✨ Exclusive Founder", 
    gradient: "from-cyan-900 to-slate-950",
    url: "capes/sir_founder.png",
    desc: "The signature glowing obsidian cape crafted exclusively for SIR ecosystem founders with dynamic cyan circuitry."
  },
  { 
    id: "ender_dragon", 
    name: "Ender Void Dragon Wings", 
    tag: "🔮 Animated Mythic", 
    gradient: "from-purple-900 to-slate-950",
    url: "capes/ender_dragon.png",
    desc: "Mystic animated void particles with the radiant eye of the Ender Dragon glowing in the dark."
  },
  { 
    id: "optifine_banner", 
    name: "OptiFine Ultra Crimson", 
    tag: "⚡ Classic OF Edition", 
    gradient: "from-red-900 to-slate-950",
    url: "capes/optifine_banner.png",
    desc: "The legendary OptiFine white 'OF' heraldic crest on a vibrant gradient crimson canvas."
  },
  { 
    id: "lunar_astral", 
    name: "Lunar Astral Galaxy", 
    tag: "🌌 Cosmic Nebula Flow", 
    gradient: "from-indigo-900 to-slate-950",
    url: "capes/lunar_astral.png",
    desc: "Deep space cosmic dust and shooting stars shimmering across an indigo twilight sky."
  },
  { 
    id: "cherry_blossom", 
    name: "Sakura Cherry Blossom 15th", 
    tag: "🌸 15th Anniversary", 
    gradient: "from-pink-900 to-slate-950",
    url: "capes/cherry_blossom.png",
    desc: "Pastel pink sakura petals drifting over the official 15th Anniversary commemorative badge."
  },
  { 
    id: "diamond_gladiator", 
    name: "Gladiator Diamond Shards", 
    tag: "💎 Ranked Diamond", 
    gradient: "from-blue-900 to-slate-950",
    url: "capes/diamond_gladiator.png",
    desc: "Forged from pure BedWars diamond shards with reflective geometric crystal facets."
  }
];

let STUDIO_STATE = {
  username: 'Steve',
  model: 'classic',
  selectedCape: PRESET_CAPES[0],
  subTab: 'capes',
  isSpinning: true,
  isWalking: true,
  animMode: 'walk',
  hasElytra: false,
  viewer: null,
  animation: null
};

function renderSkinsStudio() {
  if (STATE.activeAccountName && STATE.activeAccountName !== 'No account' && (!STUDIO_STATE.username || STUDIO_STATE.username === 'Steve')) {
    STUDIO_STATE.username = STATE.activeAccountName;
    const input = document.getElementById('skin-studio-user-input');
    if (input) input.value = STATE.activeAccountName;
  }
  initStudio3DViewer();
  renderStudioPresets();
  renderStudioCapes();
}

function setStudioAnimation(mode) {
  STUDIO_STATE.animMode = mode;
  if (!STUDIO_STATE.viewer) return;

  if (STUDIO_STATE.animation) {
    try {
      STUDIO_STATE.animation.resetAndRemove();
    } catch {}
    STUDIO_STATE.animation = null;
  }

  if (mode === 'idle') {
    if (skinview3d.IdleAnimation) {
      STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.IdleAnimation);
    }
  } else if (mode === 'walk') {
    STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.WalkingAnimation);
    STUDIO_STATE.animation.speed = 0.8;
  } else if (mode === 'run') {
    if (skinview3d.RunningAnimation) {
      STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.RunningAnimation);
      STUDIO_STATE.animation.speed = 1.0;
    } else {
      STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.WalkingAnimation);
      STUDIO_STATE.animation.speed = 1.6;
    }
  } else if (mode === 'fly') {
    if (skinview3d.FlyingAnimation) {
      STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.FlyingAnimation);
    }
  }

  ['idle', 'walk', 'run', 'fly', 'none'].forEach(m => {
    const btn = document.getElementById('anim-btn-' + m);
    if (btn) {
      if (m === mode) {
        btn.className = 'px-2 py-1 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/40 transition-all shadow-sm';
      } else {
        btn.className = 'px-2 py-1 rounded-lg text-xs font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700/50 transition-all shadow-sm';
      }
    }
  });
}

window.fetchPlayerSkinAndCape = function() {
  const input = document.getElementById('skin-studio-user-input');
  const user = input ? input.value.trim() : '';
  if (!user) {
    showToast('Please enter a player username', 'warning');
    return;
  }
  selectStudioPreset(user);
};

function initStudio3DViewer() {
  const canvas = document.getElementById('skin-studio-3d-canvas');
  if (!canvas) return;

  if (typeof skinview3d === 'undefined') {
    console.warn("skinview3d not loaded yet, retrying...");
    setTimeout(initStudio3DViewer, 200);
    return;
  }

  if (STUDIO_STATE.viewer) {
    STUDIO_STATE.viewer.dispose();
    STUDIO_STATE.viewer = null;
  }

  try {
    const cleanUser = encodeURIComponent(STUDIO_STATE.username || 'Steve');
    const skinUrl = (STUDIO_STATE.username.toLowerCase() === 'steve')
      ? 'skins/steve.png'
      : `https://mc-heads.net/skin/${cleanUser}`;

    const viewer = new skinview3d.SkinViewer({
      canvas: canvas,
      width: 280,
      height: 340,
      skin: skinUrl
    });

    viewer.camera.position.set(0, 0, 65);
    viewer.playerObject.rotation.y = Math.PI * 0.95;
    viewer.autoRotate = STUDIO_STATE.isSpinning;
    viewer.autoRotateSpeed = 1.2;

    if (STUDIO_STATE.selectedCape && STUDIO_STATE.selectedCape.url) {
      viewer.loadCape(STUDIO_STATE.selectedCape.url, {
        backEquipment: STUDIO_STATE.hasElytra ? "elytra" : "cape"
      }).catch(e => console.warn("Cape load notice:", e));
    }

    STUDIO_STATE.viewer = viewer;
    setStudioAnimation(STUDIO_STATE.animMode || 'walk');
    updateStudioBadges();
  } catch (err) {
    console.warn("3D SkinViewer init error:", err);
  }
}

function updateStudioBadges() {
  const modelBadge = document.getElementById('studio-model-badge');
  const capeBadge = document.getElementById('studio-cape-badge');

  if (modelBadge) {
    modelBadge.textContent = STUDIO_STATE.model === 'slim' ? 'Slim (3px - Alex)' : 'Classic (4px - Steve)';
  }
  if (capeBadge) {
    if (STUDIO_STATE.selectedCape) {
      capeBadge.textContent = STUDIO_STATE.selectedCape.name;
      capeBadge.classList.remove('hidden');
    } else {
      capeBadge.classList.add('hidden');
    }
  }
}

function toggleLauncherStudioSpin() {
  if (!STUDIO_STATE.viewer) return;
  STUDIO_STATE.isSpinning = !STUDIO_STATE.isSpinning;
  STUDIO_STATE.viewer.autoRotate = STUDIO_STATE.isSpinning;

  const btn = document.getElementById('studio-btn-spin');
  const text = document.getElementById('studio-spin-text');
  if (btn && text) {
    if (STUDIO_STATE.isSpinning) {
      btn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Spinning';
      const icon = btn.querySelector('i');
      if (icon) icon.classList.add('animate-spin');
    } else {
      btn.className = 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Paused';
      const icon = btn.querySelector('i');
      if (icon) icon.classList.remove('animate-spin');
    }
  }
}

function toggleLauncherStudioAnim() {
  if (!STUDIO_STATE.viewer) return;
  STUDIO_STATE.isWalking = !STUDIO_STATE.isWalking;

  if (STUDIO_STATE.isWalking) {
    if (STUDIO_STATE.animation) {
      STUDIO_STATE.animation.paused = false;
    } else {
      STUDIO_STATE.animation = STUDIO_STATE.viewer.animations.add(skinview3d.WalkingAnimation);
      STUDIO_STATE.animation.speed = 0.8;
    }
  } else {
    if (STUDIO_STATE.animation) {
      STUDIO_STATE.animation.paused = true;
    }
  }

  const btn = document.getElementById('studio-btn-anim');
  const text = document.getElementById('studio-anim-text');
  if (btn && text) {
    if (STUDIO_STATE.isWalking) {
      btn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Walking';
    } else {
      btn.className = 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Static';
    }
  }
}

function toggleLauncherStudioElytra() {
  STUDIO_STATE.hasElytra = !STUDIO_STATE.hasElytra;
  if (STUDIO_STATE.viewer) {
    STUDIO_STATE.viewer.playerObject.backEquipment = STUDIO_STATE.hasElytra ? "elytra" : "cape";
    if (STUDIO_STATE.selectedCape) {
      STUDIO_STATE.viewer.loadCape(STUDIO_STATE.selectedCape.url, {
        backEquipment: STUDIO_STATE.hasElytra ? "elytra" : "cape"
      }).catch(e => console.warn("Elytra toggle notice:", e));
    }
  }

  const btn = document.getElementById('studio-btn-elytra');
  const text = document.getElementById('studio-elytra-text');
  if (btn && text) {
    if (STUDIO_STATE.hasElytra) {
      btn.className = 'px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Elytra';
    } else {
      btn.className = 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 flex items-center gap-1 transition-all cursor-pointer';
      text.textContent = 'Cape';
    }
  }
}

function setStudioModel(model) {
  STUDIO_STATE.model = model;
  const classic = document.getElementById('model-btn-classic');
  const slim = document.getElementById('model-btn-slim');
  if (classic && slim) {
    if (model === 'classic') {
      classic.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 transition-all text-center cursor-pointer';
      slim.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-slate-800 text-slate-400 border border-transparent transition-all text-center cursor-pointer';
    } else {
      slim.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 transition-all text-center cursor-pointer';
      classic.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-slate-800 text-slate-400 border border-transparent transition-all text-center cursor-pointer';
    }
  }
  if (STUDIO_STATE.viewer) {
    const cleanUser = encodeURIComponent(STUDIO_STATE.username || 'Steve');
    const skinUrl = STUDIO_STATE.customSkinData || (STUDIO_STATE.username.toLowerCase() === 'steve' ? 'skins/steve.png' : `https://mc-heads.net/skin/${cleanUser}`);
    STUDIO_STATE.viewer.loadSkin(skinUrl, { model: model === 'slim' ? 'slim' : 'default' })
      .catch(e => {
        console.warn("Model reload fallback to default:", e);
        STUDIO_STATE.viewer.loadSkin('skins/steve.png', { model: model === 'slim' ? 'slim' : 'default' }).catch(() => {});
      });
  }
  updateStudioBadges();
}

function switchStudioSubTab(tab) {
  STUDIO_STATE.subTab = tab;
  const tabP = document.getElementById('studio-tab-presets');
  const tabC = document.getElementById('studio-tab-capes');
  const viewP = document.getElementById('studio-presets-container');
  const viewC = document.getElementById('studio-capes-container');

  if (tab === 'presets') {
    if (tabP) tabP.className = 'filter-pill active flex items-center gap-1.5 text-xs';
    if (tabC) tabC.className = 'filter-pill flex items-center gap-1.5 text-xs';
    if (viewP) viewP.classList.remove('hidden');
    if (viewC) viewC.classList.add('hidden');
    renderStudioPresets();
  } else {
    if (tabP) tabP.className = 'filter-pill flex items-center gap-1.5 text-xs';
    if (tabC) tabC.className = 'filter-pill active flex items-center gap-1.5 text-xs';
    if (viewP) viewP.classList.add('hidden');
    if (viewC) viewC.classList.remove('hidden');
    renderStudioCapes();
  }
  refreshLucideIcons();
}

function renderStudioPresets() {
  const container = document.getElementById('studio-skins-grid');
  if (!container) return;
  const isLight = document.documentElement.classList.contains('light');

  container.innerHTML = PRESET_SKINS.map(skin => {
    const isSel = STUDIO_STATE.username.toLowerCase() === skin.username.toLowerCase();
    const avatarSrc = (skin.username.toLowerCase() === 'steve')
      ? 'https://minotar.net/avatar/Steve/48.png'
      : `https://mc-heads.net/avatar/${encodeURIComponent(skin.username)}/48`;

    return `
      <div onclick="selectStudioPreset('${escapeHtml(skin.username)}')" class="feature-card p-3 rounded-2xl border transition-all cursor-pointer text-center ${
        isSel 
          ? 'border-cyan-400 bg-cyan-950/30 ring-1 ring-cyan-400/50 shadow-md shadow-cyan-500/20' 
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700')
      }">
        <img src="${avatarSrc}" class="w-12 h-12 mx-auto rounded-xl object-contain shadow-sm border border-slate-700" onerror="this.src='https://minotar.net/avatar/Steve/48.png'">
        <h5 class="text-xs font-black text-slate-900 dark:text-slate-100 mt-2 truncate">${escapeHtml(skin.name)}</h5>
        <span class="text-[10px] text-cyan-600 dark:text-cyan-400 font-mono block mt-0.5 truncate">${escapeHtml(skin.category)}</span>
      </div>
    `;
  }).join('');
}

function renderStudioCapes() {
  const container = document.getElementById('studio-capes-grid');
  if (!container) return;
  const isLight = document.documentElement.classList.contains('light');

  container.innerHTML = PRESET_CAPES.map(cape => {
    const isSel = STUDIO_STATE.selectedCape && STUDIO_STATE.selectedCape.id === cape.id;
    return `
      <div onclick="selectStudioCape('${cape.id}')" class="feature-card p-3.5 rounded-2xl border transition-all cursor-pointer text-left ${
        isSel 
          ? 'border-cyan-400 bg-cyan-950/30 ring-1 ring-cyan-400/50 shadow-lg shadow-cyan-500/20' 
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700')
      }">
        <div class="flex items-center justify-between mb-2">
          <span class="badge-tag text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">${escapeHtml(cape.tag)}</span>
          <span class="w-2.5 h-2.5 rounded-full ${isSel ? 'bg-emerald-400 shadow-[0_0_8px_#38ef7d]' : 'bg-slate-700'}"></span>
        </div>
        <div class="flex items-center gap-3">
          <div class="w-10 h-14 rounded-lg bg-gradient-to-br ${cape.gradient} border border-cyan-500/30 shadow-md flex items-center justify-center text-cyan-300 text-base font-bold shrink-0">
            🛡️
          </div>
          <div class="min-w-0 flex-1">
            <h5 class="text-xs font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(cape.name)}</h5>
            <p class="text-[10px] text-slate-400 line-clamp-2 mt-0.5 leading-relaxed">${escapeHtml(cape.desc)}</p>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function selectStudioPreset(username) {
  STUDIO_STATE.username = username;
  const input = document.getElementById('skin-studio-user-input');
  if (input) input.value = username;
  
  if (STUDIO_STATE.viewer) {
    const cleanUser = encodeURIComponent(username);
    const skinUrl = (username.toLowerCase() === 'steve')
      ? 'skins/steve.png'
      : `https://mc-heads.net/skin/${cleanUser}`;
    STUDIO_STATE.viewer.loadSkin(skinUrl).catch(e => console.warn("Skin load notice:", e));
  }

  renderStudioPresets();
  updateStudioBadges();
  showToast(`✓ Previewing Skin: @${username}`, 'info');
}

function selectStudioCape(capeId) {
  const cape = PRESET_CAPES.find(c => c.id === capeId);
  STUDIO_STATE.selectedCape = cape;

  if (STUDIO_STATE.viewer && cape) {
    STUDIO_STATE.viewer.playerObject.rotation.y = Math.PI * 0.95;
    STUDIO_STATE.viewer.loadCape(cape.url, {
      backEquipment: STUDIO_STATE.hasElytra ? "elytra" : "cape"
    }).catch(e => console.warn("Cape load notice:", e));
  }

  renderStudioCapes();
  updateStudioBadges();
  showToast(`✓ Equipped: ${cape ? cape.name : 'None'}`, 'success');
}

let _debounceSkinTimer = null;
function debounceSkinLookup(value) {
  clearTimeout(_debounceSkinTimer);
  _debounceSkinTimer = setTimeout(() => {
    if (value && value.trim().length >= 2) {
      const clean = value.trim();
      STUDIO_STATE.username = clean;
      STUDIO_STATE.customSkinData = null;
      if (STUDIO_STATE.viewer) {
        const modelOpt = STUDIO_STATE.model === 'slim' ? 'slim' : 'default';
        STUDIO_STATE.viewer.loadSkin(`https://mc-heads.net/skin/${encodeURIComponent(clean)}`, { model: modelOpt })
          .catch(e => {
            console.warn("Live skin lookup notice, falling back to local steve.png:", e);
            STUDIO_STATE.viewer.loadSkin('skins/steve.png', { model: modelOpt }).catch(() => {});
          });
      }
      updateStudioBadges();
    }
  }, 400);
}

function handleSkinFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      STUDIO_STATE.customSkinData = dataUrl;
      if (STUDIO_STATE.viewer) {
        const modelOpt = STUDIO_STATE.model === 'slim' ? 'slim' : 'default';
        STUDIO_STATE.viewer.loadSkin(dataUrl, { model: modelOpt })
          .catch(err => console.warn("Custom skin upload load notice:", err));
      }
      showToast('✓ Custom skin file loaded into 3D viewer!', 'success');
    };
    reader.readAsDataURL(file);
  }
}

async function applySkinFromStudioInput() {
  const username = STUDIO_STATE.username || 'SirAhmed';
  const capeUrl = STUDIO_STATE.selectedCape ? STUDIO_STATE.selectedCape.url : '';
  const model = STUDIO_STATE.model || 'classic';
  const activeInst = STATE.selectedInstanceId || '26.2';
  const skinUrl = STUDIO_STATE.customSkinData || `https://mc-heads.net/skin/${encodeURIComponent(username)}`;

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.apply_skin_and_cape(username, skinUrl, capeUrl, model, activeInst);
    } catch {}
  }
  showToast(`✓ Skin & Cape applied to ${activeInst} for @${username}!`, 'success');
}


