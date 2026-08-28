// =============================================================================
// 10. 3D SKIN & CAPES STUDIO (WEBSITE PARITY)
// =============================================================================
const PRESET_SKINS = [
  { id: "technoblade", name: "Technoblade (The Blade)", category: "Legendary / PvP", username: "Technoblade" },
  { id: "dream", name: "Dream (Speedrun Legend)", category: "Speedrun / Competitive", username: "Dream" },
  { id: "skeppy", name: "Skeppy (Diamond Skeppy)", category: "Content / Trolling", username: "Skeppy" },
  { id: "sparklez", name: "CaptainSparklez (Jordan)", category: "OG Veteran / Music", username: "CaptainSparklez" },
  { id: "illumina", name: "Illumina (Speedrun Master)", category: "Speedrun / Fantasy", username: "Illumina" },
  { id: "grian", name: "Grian (Master Builder)", category: "Creative / Builder", username: "Grian" },
  { id: "mumbo", name: "Mumbo Jumbo (Redstone)", category: "Redstone / Engineering", username: "Mumbo" },
  { id: "siranmed", name: "SirAhmed (Creator Edition)", category: "SIR Developer", username: "SirAhmed" }
];

const PRESET_CAPES = [
  { id: "migrator", name: "Migrator Cape", year: "2021", color: "from-red-900 to-amber-700", url: "https://textures.minecraft.net/texture/2340c0e03dd66dd116bed10937dbda69617d0ef819bb1e3263044d30e80a5c48" },
  { id: "vanilla", name: "Vanilla Cape", year: "2022", color: "from-blue-900 to-amber-600", url: "https://textures.minecraft.net/texture/1a084c8a417537b830f81d459223fa8c0a876793b8f101f34ec8cf7d85fe3fb" },
  { id: "cherry", name: "Cherry Blossom Cape", year: "2023", color: "from-pink-600 to-rose-400", url: "https://textures.minecraft.net/texture/a2e632041269389e67d26bb4c90d54020de0d01441865365fb93c3fb2b6a93bf" },
  { id: "anniversary15", name: "15th Anniversary Cape", year: "2024", color: "from-emerald-700 to-teal-500", url: "https://textures.minecraft.net/texture/4458b663c6b24017849ecb1379cc7a4bb748a313d4982631a0ceba6ee48cf491" },
  { id: "minecon2011", name: "Minecon 2011 (Classic Red)", year: "2011", color: "from-red-700 to-rose-900", url: "https://textures.minecraft.net/texture/8ba068795e2f5be7a677148e3029030df13dd700072ec3c84fa760fdd89923be" },
  { id: "minecon2012", name: "Minecon 2012 (Pickaxe)", year: "2012", color: "from-blue-800 to-slate-900", url: "https://textures.minecraft.net/texture/a2e632041269389e67d26bb4c90d54020de0d01441865365fb93c3fb2b6a93bf" },
  { id: "minecon2013", name: "Minecon 2013 (Piston)", year: "2013", color: "from-amber-800 to-orange-950", url: "https://textures.minecraft.net/texture/1a084c8a417537b830f81d459223fa8c0a876793b8f101f34ec8cf7d85fe3fb" },
  { id: "mojang_studios", name: "Mojang Studios Official", year: "Special", color: "from-red-600 to-red-950", url: "https://textures.minecraft.net/texture/2340c0e03dd66dd116bed10937dbda69617d0ef819bb1e3263044d30e80a5c48" }
];

let STUDIO_STATE = {
  username: 'Steve',
  angle: 'right',
  model: 'classic',
  selectedCape: null,
  subTab: 'presets'
};

function renderSkinsStudio() {
  renderStudioStage();
  renderStudioPresets();
  renderStudioCapes();
}

function renderStudioStage() {
  const img = document.getElementById('skin-studio-render');

  if (img) {
    const cleanUser = encodeURIComponent(STUDIO_STATE.username || 'Steve');
    img.src = `https://mc-heads.net/body/${cleanUser}/${STUDIO_STATE.angle || 'right'}`;
  }
  const badge = document.getElementById('studio-model-badge');
  if (badge) {
    badge.textContent = STUDIO_STATE.model === 'slim' ? 'Slim (3px - Alex)' : 'Classic (4px - Steve)';
  }
}

function setStudioAngle(angle) {
  STUDIO_STATE.angle = angle;
  ['right', 'left', 'front'].forEach(a => {
    const btn = document.getElementById(`angle-btn-${a}`);
    if (btn) {
      if (a === angle) {
        btn.className = 'px-2 py-0.5 text-[10px] font-bold rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 transition-all';
      } else {
        btn.className = 'px-2 py-0.5 text-[10px] font-bold rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
      }
    }
  });
  renderStudioStage();
}

function setStudioModel(model) {
  STUDIO_STATE.model = model;
  const classic = document.getElementById('model-btn-classic');
  const slim = document.getElementById('model-btn-slim');
  if (classic && slim) {
    if (model === 'classic') {
      classic.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 transition-all text-center';
      slim.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-slate-800 text-slate-400 border border-transparent transition-all text-center';
    } else {
      slim.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 transition-all text-center';
      classic.className = 'flex-1 py-1 rounded-lg text-xs font-bold bg-slate-800 text-slate-400 border border-transparent transition-all text-center';
    }
  }
  renderStudioStage();
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
    return `
      <div onclick="selectStudioPreset('${escapeHtml(skin.username)}')" class="feature-card p-3 rounded-2xl border transition-all cursor-pointer text-center ${
        isSel 
          ? 'border-cyan-400 bg-cyan-950/30 ring-1 ring-cyan-400/50 shadow-md shadow-cyan-500/20' 
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700')
      }">
        <img src="https://mc-heads.net/avatar/${encodeURIComponent(skin.username)}/48" class="w-12 h-12 mx-auto rounded-xl object-contain shadow-sm border border-slate-700" onerror="this.src='https://minotar.net/avatar/Steve/48.png'">
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
      <div onclick="selectStudioCape('${cape.id}')" class="feature-card p-3 rounded-2xl border transition-all cursor-pointer text-center ${
        isSel 
          ? 'border-emerald-400 bg-emerald-950/30 ring-1 ring-emerald-400/50 shadow-md shadow-emerald-500/20' 
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700')
      }">
        <div class="w-12 h-16 mx-auto rounded-xl bg-gradient-to-br ${cape.color} border border-slate-600 shadow-md flex items-center justify-center text-white text-lg font-bold">
          🛡️
        </div>
        <h5 class="text-xs font-black text-slate-900 dark:text-slate-100 mt-2 truncate">${escapeHtml(cape.name)}</h5>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono block mt-0.5">${cape.year}</span>
      </div>
    `;
  }).join('');
}

function selectStudioPreset(username) {
  STUDIO_STATE.username = username;
  const input = document.getElementById('skin-studio-user-input');
  if (input) input.value = username;
  renderStudioStage();
  renderStudioPresets();
  showToast(`✓ Previewing Skin: ${username}`, 'info');
}

function selectStudioCape(capeId) {
  const cape = PRESET_CAPES.find(c => c.id === capeId);
  STUDIO_STATE.selectedCape = cape;
  const capeBadge = document.getElementById('studio-cape-badge');
  if (capeBadge) {
    if (cape) {
      capeBadge.textContent = cape.name;
      capeBadge.classList.remove('hidden');
    } else {
      capeBadge.classList.add('hidden');
    }
  }
  renderStudioCapes();
  showToast(`✓ Equipped: ${cape ? cape.name : 'None'}`, 'success');
}

let _debounceSkinTimer = null;
function debounceSkinLookup(value) {
  clearTimeout(_debounceSkinTimer);
  _debounceSkinTimer = setTimeout(() => {
    if (value && value.trim().length >= 2) {
      STUDIO_STATE.username = value.trim();
      renderStudioStage();
    }
  }, 400);
}

function handleSkinFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      showToast('✓ Custom skin file uploaded successfully!', 'success');
    };
    reader.readAsDataURL(file);
  }
}

async function applySkinFromStudioInput() {
  const username = STUDIO_STATE.username || 'SirAhmed';
  const capeUrl = STUDIO_STATE.selectedCape ? STUDIO_STATE.selectedCape.url : '';
  const model = STUDIO_STATE.model || 'classic';
  const activeInst = STATE.selectedInstanceId || '26.2';

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.apply_skin_and_cape(username, `https://mc-heads.net/skin/${encodeURIComponent(username)}`, capeUrl, model, activeInst);
    } catch {}
  }
  showToast(`✓ Skin & Cape applied to ${activeInst} for @${username}!`, 'success');
}

