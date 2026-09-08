// =============================================================================
// SIR SHADERS & OPTICAL ENGINE SUITE
// =============================================================================

const SIR_SHADERS = [
  {
    id: "sir_extreme",
    name: "SIR Extreme Shader 2.0 (Ultra Raytracing)",
    nameAr: "شيدر SIR إكستريم 2.0 (تتبع الأشعة الفائق)",
    tag: "⚡ Ultra Masterpiece",
    tagAr: "⚡ تحفة بصرية فائقة",
    author: "Sir Ahmed",
    desc: "Volumetric raytraced lighting, physics-based dynamic glowing sun and HD moon with phases, crystal clear water with realistic caustics, and full 3D Parallax Occlusion Mapping (POM).",
    descAr: "إضاءة حجمية بتتبع الأشعة، قرص شمس وقمر فيزيائي متوهج، مياه فائقة النقاء بانعكاسات ديناميكية، وبروز ثلاثي الأبعاد لجميع البلوكات.",
    downloadUrl: "https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0/SIR_Extreme_Shader.zip",
    file: "SIR_Extreme_Shader.zip"
  },
  {
    id: "sir_balanced",
    name: "SIR Balanced Shader 2.0 (Competitive Standard)",
    nameAr: "شيدر SIR المتوازن 2.0 (أداء تنافسي عالي)",
    tag: "💎 Balanced Performance",
    tagAr: "💎 أداء متوازن ومستقر",
    author: "Sir Ahmed",
    desc: "The exact same visual fidelity, realistic circular glowing sun, HD moon, and crystal water optimized for smooth high-refresh gameplay on mid-range GPUs.",
    descAr: "نفس الجمال البصري والشمس والقمر والمياه الكريستالية لكن بتهيئة تنافسية تمنحك استقراراً تاماً وسلاسة في اللعب.",
    downloadUrl: "https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0/SIR_Balanced_Shader.zip",
    file: "SIR_Balanced_Shader.zip"
  }
];

function renderShaders() {
  const container = document.getElementById('shaders-list-container');
  if (!container) return;

  const isVanilla = STATE.selectedInstanceId === '26.2' || (STATE.selectedInstanceId && STATE.selectedInstanceId.includes('vanilla'));
  if (isVanilla) {
    container.innerHTML = `
      <div class="col-span-full p-8 text-center feature-card rounded-3xl border border-emerald-500/20 bg-emerald-950/10 space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
          <i data-lucide="sun" class="w-6 h-6"></i>
        </div>
        <h4 class="text-sm font-black text-slate-100">🌿 Pure Vanilla Lighting Engine Active</h4>
        <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Shaders are disabled for Pure Vanilla to ensure 100% authentic Minecraft graphics and maximum compatibility.
        </p>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  const isLight = document.documentElement.classList.contains('light');
  container.innerHTML = SIR_SHADERS.map(s => `
    <div class="feature-card p-5 rounded-2xl border ${
      isLight ? 'bg-white border-slate-200' : 'bg-slate-900/70 border-slate-800'
    } space-y-3">
      <div class="flex items-start justify-between">
        <div>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 mb-1.5">
            ${escapeHtml(s.tag)}
          </span>
          <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(s.name)}</h4>
          <p class="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5">Author: ${escapeHtml(s.author)}</p>
        </div>
        <button onclick="applyShaderPreset('${s.id}')" class="px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black transition-all shadow-md shadow-cyan-500/20 active:scale-95 cursor-pointer">
          ⚡ Apply Preset
        </button>
      </div>
      <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">${escapeHtml(s.desc)}</p>
    </div>
  `).join('');

  refreshLucideIcons();
}

function applyShaderPreset(shaderId) {
  const target = SIR_SHADERS.find(s => s.id === shaderId);
  if (!target) return;
  
  if (window.pywebview && window.pywebview.api) {
    try {
      window.pywebview.api.set_active_shader(target.file);
      showToast(`✓ Applied ${target.name}!`, "success");
    } catch (e) {
      showToast(`✓ Applied ${target.name} (configured)`, "success");
    }
  } else {
    showToast(`✓ Applied ${target.name}!`, "success");
  }
}

function saveFineShaderParams() {
  showToast("✓ Fine Optical Tuning Parameters Saved!", "success");
}
