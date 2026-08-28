// =============================================================================
// 3. MULTIPLAYER SERVERS RADAR & CURATED HUB (22+ SERVERS WITH LIVE API)
// =============================================================================
const MASTER_SERVERS_LIST = [
  {
    id: "hypixel",
    name: "Hypixel Network",
    host: "mc.hypixel.net",
    type: "Official Only",
    category: "Competitive",
    desc: "The world's largest Minecraft network featuring Bedwars, Skywars, Duels, and Skyblock.",
    featured: true,
    ping: 24,
    players: "38,500",
    playersMax: "200,000",
    version: "1.8.9 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/mc.hypixel.net"
  },
  {
    id: "minemen",
    name: "Minemen Club (MMC)",
    host: "na.minemen.club",
    type: "Official Only",
    category: "Practice",
    desc: "The premier competitive 1v1 Practice PvP and Ranked GCheat server with zero lag.",
    featured: true,
    ping: 28,
    players: "2,650",
    playersMax: "5,000",
    version: "1.7.x - 1.8.9",
    iconUrl: "https://api.mcsrvstat.us/icon/na.minemen.club"
  },
  {
    id: "pika",
    name: "PikaNetwork",
    host: "play.pika-network.net",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "Ranked #1 for Bedwars, Practice PvP, and OP Factions with zero hit delay.",
    featured: true,
    ping: 35,
    players: "6,800",
    playersMax: "10,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.pika-network.net"
  },
  {
    id: "jartex",
    name: "JartexNetwork",
    host: "play.jartexnetwork.com",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Massive hub for Bedwars, SkyWars, KitPvP, and Custom Lifesteal SMP.",
    featured: true,
    ping: 36,
    players: "5,400",
    playersMax: "8,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.jartexnetwork.com"
  },
  {
    id: "blockmc",
    name: "BlockMC Network",
    host: "blockmc.com",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "Competitive Bedwars, Ranked Duels, and fast-paced bridging challenges.",
    featured: true,
    ping: 38,
    players: "4,120",
    playersMax: "6,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/blockmc.com"
  },
  {
    id: "cubecraft",
    name: "CubeCraft Games",
    host: "play.cubecraft.net",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Home of EggWars, SkyWars, BlockWars, and custom party minigames.",
    featured: false,
    ping: 36,
    players: "1,850",
    playersMax: "15,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.cubecraft.net"
  },
  {
    id: "gommehd",
    name: "GommeHD.net",
    host: "gommehd.net",
    type: "Official Only",
    category: "Competitive",
    desc: "Europe's largest multiplayer network featuring BedWars, Cores, and EnderGames.",
    featured: false,
    ping: 22,
    players: "3,400",
    playersMax: "10,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/gommehd.net"
  },
  {
    id: "wynncraft",
    name: "Wynncraft MMORPG",
    host: "play.wynncraft.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The largest MMORPG in Minecraft with full custom quests, classes, and open world.",
    featured: false,
    ping: 45,
    players: "2,200",
    playersMax: "8,000",
    version: "1.12.2 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.wynncraft.com"
  },
  {
    id: "donutsmp",
    name: "DonutSMP (Hardcore Lifesteal)",
    host: "donutsmp.net",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The largest Hardcore Lifesteal SMP server with real heart-stealing PvP economy.",
    featured: false,
    ping: 49,
    players: "2,900",
    playersMax: "10,000",
    version: "1.20.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/donutsmp.net"
  },
  {
    id: "complex",
    name: "Complex Gaming",
    host: "hub.mc-complex.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "Hub for Pixelmon, Vanilla Survival, Skyblock, and Towny realms.",
    featured: false,
    ping: 42,
    players: "1,920",
    playersMax: "5,000",
    version: "1.8.9 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/hub.mc-complex.com"
  },
  {
    id: "mushmc",
    name: "MushMC",
    host: "mush.com.br",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "South America's premier competitive Bedwars, Duels, and HG server.",
    featured: false,
    ping: 85,
    players: "3,100",
    playersMax: "6,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/mush.com.br"
  },
  {
    id: "craftrise",
    name: "CraftRise Network",
    host: "play.craftrise.tc",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Popular international network with custom PvP clients and arena battles.",
    featured: false,
    ping: 65,
    players: "4,500",
    playersMax: "12,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.craftrise.tc"
  },
  {
    id: "herobrine",
    name: "Herobrine.org",
    host: "herobrine.org",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Legendary Survival, Earth SMP, Bedwars, and Skyblock network.",
    featured: false,
    ping: 38,
    players: "1,400",
    playersMax: "4,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/herobrine.org"
  },
  {
    id: "pvpgym",
    name: "PvPGym Training",
    host: "pvpgym.net",
    type: "Official Only",
    category: "Practice",
    desc: "Specialized aiming, combo pacing, and reaction training grounds for 1.8.9 & 1.21.",
    featured: false,
    ping: 31,
    players: "450",
    playersMax: "1,000",
    version: "1.8.9 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/pvpgym.net"
  },
  {
    id: "bedwarspractice",
    name: "Bedwars Practice Club",
    host: "bedwarspractice.club",
    type: "Cracked & Official",
    category: "Practice",
    desc: "Fast-bridging, clutch saving, and bed defense training simulator.",
    featured: false,
    ping: 42,
    players: "850",
    playersMax: "2,000",
    version: "1.8.9 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/bedwarspractice.club"
  },
  {
    id: "tubnet",
    name: "TubNet",
    host: "tubnet.gg",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Tubbo's official cross-play minigame network with custom animations.",
    featured: false,
    ping: 54,
    players: "320",
    playersMax: "1,500",
    version: "1.19.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/tubnet.gg"
  },
  {
    id: "nethergames",
    name: "NetherGames Network",
    host: "play.nethergames.org",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Fast Bedwars, Duels, and Factions with high performance multi-region routing.",
    featured: false,
    ping: 48,
    players: "1,600",
    playersMax: "5,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.nethergames.org"
  },
  {
    id: "2b2t",
    name: "2b2t Anarchy",
    host: "2b2t.org",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The oldest anarchy server in Minecraft with zero rules and rich history.",
    featured: false,
    ping: 72,
    players: "1,050",
    playersMax: "2,000",
    version: "1.20.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/2b2t.org"
  },
  {
    id: "mccisland",
    name: "MCC Island (Noxcrew)",
    host: "play.mccisland.net",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Official MC Championship server featuring Hole in the Wall, TGTTOS, and Battle Box.",
    featured: false,
    ping: 39,
    players: "1,200",
    playersMax: "5,000",
    version: "1.19.4 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.mccisland.net"
  },
  {
    id: "applemc",
    name: "AppleMC",
    host: "play.applemc.fun",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Economy Survival, Lifesteal, and Skyblock with active community events.",
    featured: false,
    ping: 44,
    players: "980",
    playersMax: "3,000",
    version: "1.16.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.applemc.fun"
  },
  {
    id: "mineberry",
    name: "MineBerry",
    host: "mineberry.net",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Custom Anarchy, OP Survival, and high-FPS Bedwars for all clients.",
    featured: false,
    ping: 41,
    players: "1,150",
    playersMax: "4,000",
    version: "1.8.x - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/mineberry.net"
  },
  {
    id: "manacube",
    name: "ManaCube",
    host: "play.manacube.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "Massive network with Parkour, Islands, Olympus Prison, and Survival.",
    featured: false,
    ping: 39,
    players: "2,150",
    playersMax: "5,000",
    version: "1.8.9 - 1.21.x",
    iconUrl: "https://api.mcsrvstat.us/icon/play.manacube.com"
  }
];

STATE.servers = MASTER_SERVERS_LIST;
STATE.serverFilter = "All";
STATE.serverSearch = "";
STATE.serverSort = "Fastest"; // Fastest | Players | Name

function filterServers(cat) {
  STATE.serverFilter = cat;
  const pills = document.querySelectorAll('#server-filter-pills .filter-pill');
  pills.forEach(btn => {
    const text = btn.textContent.trim();
    if (cat === 'All' && text === 'All') btn.classList.add('active');
    else if (cat === 'Cracked' && text.includes('Cracked')) btn.classList.add('active');
    else if (cat === 'Saved' && text.includes('Saved')) btn.classList.add('active');
    else if (text.toLowerCase() === cat.toLowerCase()) btn.classList.add('active');
    else btn.classList.remove('active');
  });
  renderServers();
}

function searchServers(query) {
  STATE.serverSearch = query || "";
  renderServers();
}

function toggleServerSorting() {
  if (STATE.serverSort === "Fastest") {
    STATE.serverSort = "Players";
    document.getElementById('server-sort-text').textContent = "Most Players";
  } else if (STATE.serverSort === "Players") {
    STATE.serverSort = "Name";
    document.getElementById('server-sort-text').textContent = "Server Name";
  } else {
    STATE.serverSort = "Fastest";
    document.getElementById('server-sort-text').textContent = "Fastest Ping";
  }
  renderServers();
}

async function loadServersLive() {
  renderServers();
  // Fetch real live status in parallel for all servers
  const promises = STATE.servers.map(async srv => {
    try {
      const res = await fetch(`https://api.mcstatus.io/v2/status/java/${srv.host}`, { 
        signal: AbortSignal.timeout(3500) 
      });
      if (res.ok) {
        const data = await res.json();
        if (data && data.online) {
          srv.ping = Math.round(data.roundTripLatency || srv.ping);
          srv.players = (data.players?.online || 0).toLocaleString();
          srv.playersMax = (data.players?.max || 0).toLocaleString();
          srv.version = data.version?.name_clean || srv.version;
          if (data.icon) srv.iconUrl = data.icon;
          if (data.motd?.clean) srv.desc = data.motd.clean.trim().replace(/\n/g, ' ');
          renderServers();
        }
      }
    } catch {
      // Graceful fallback to cached seed data
    }
  });
  await Promise.allSettled(promises);
}

function renderServers() {
  const container = document.getElementById('servers-grid');
  if (!container) return;

  const isLight = document.documentElement.classList.contains('light');

  let list = STATE.servers.filter(s => {
    // Category match
    let matchCat = true;
    if (STATE.serverFilter === 'Cracked') {
      matchCat = s.type.includes('Cracked');
    } else if (STATE.serverFilter === 'Saved') {
      matchCat = s.name.includes('SIR') || s.saved;
    } else if (STATE.serverFilter !== 'All') {
      matchCat = s.category && s.category.toLowerCase() === STATE.serverFilter.toLowerCase();
    }

    // Search query match
    let matchQuery = true;
    if (STATE.serverSearch && STATE.serverSearch.trim()) {
      const q = STATE.serverSearch.trim().toLowerCase();
      matchQuery = s.name.toLowerCase().includes(q) || 
                   s.host.toLowerCase().includes(q) || 
                   (s.desc && s.desc.toLowerCase().includes(q)) ||
                   (s.category && s.category.toLowerCase().includes(q));
    }
    return matchCat && matchQuery;
  });

  // Sorting
  if (STATE.serverSort === 'Fastest') {
    list.sort((a, b) => (a.ping || 999) - (b.ping || 999));
  } else if (STATE.serverSort === 'Players') {
    const parseCount = (v) => parseInt(String(v).replace(/,/g, ''), 10) || 0;
    list.sort((a, b) => parseCount(b.players) - parseCount(a.players));
  } else if (STATE.serverSort === 'Name') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  }

  if (list.length === 0) {
    container.innerHTML = `
      <div class="col-span-full feature-card p-10 text-center border-slate-800 bg-white dark:bg-[#0b101b]">
        <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-3 text-2xl">
          🔍
        </div>
        <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200">No Servers Found</h4>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Try resetting your search query or selecting "All" category.</p>
        <button onclick="filterServers('All'); document.getElementById('server-search-input').value=''; searchServers('')" class="mt-4 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black transition-all">Show All 22+ Servers</button>
      </div>
    `;
    return;
  }

  const isSearchingOrFiltered = STATE.serverSearch || STATE.serverFilter !== 'All';
  const showAll = STATE.showAllServers || isSearchingOrFiltered;
  const displayedList = showAll ? list : list.slice(0, 6);

  const showMoreContainer = document.getElementById('servers-show-more-container');
  const showMoreBtn = document.getElementById('servers-show-more-btn');
  const showMoreText = document.getElementById('servers-show-more-text');
  const showMoreIcon = document.getElementById('servers-show-more-icon');

  if (showMoreContainer) {
    if (isSearchingOrFiltered || list.length <= 6) {
      showMoreContainer.classList.add('hidden');
    } else {
      showMoreContainer.classList.remove('hidden');
      if (showMoreText) showMoreText.textContent = STATE.showAllServers ? 'Show Less Servers' : `Show More Servers (${list.length}+)`;
      if (showMoreIcon) showMoreIcon.style.transform = STATE.showAllServers ? 'rotate(180deg)' : 'rotate(0deg)';
    }
  }

  container.innerHTML = displayedList.map(srv => {
    const isCracked = srv.type.includes('Cracked');
    const pingColor = srv.ping < 45 ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/15 border-emerald-500/30' : (srv.ping < 90 ? 'text-amber-600 dark:text-amber-400 bg-amber-500/15 border-amber-500/30' : 'text-cyan-600 dark:text-cyan-400 bg-cyan-500/15 border-cyan-500/30');

    return `
      <div class="feature-card p-5 rounded-2xl border transition-all ${
        isLight ? 'bg-white border-slate-200 hover:border-slate-300 shadow-sm' : 'bg-[#0c121e] border-slate-800 hover:border-slate-700 shadow-md'
      } flex flex-col justify-between gap-4 group">
        <div>
          <!-- Header with Real Server Icon -->
          <div class="flex items-start gap-3.5">
            <img 
              src="${srv.iconUrl || ('https://api.mcsrvstat.us/icon/' + srv.host)}" 
              alt="${escapeHtml(srv.name)}" 
              onerror="this.src='https://eu.mc-api.net/v3/server/favicon/${srv.host}'" 
              class="w-13 h-13 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50 dark:bg-slate-900 object-contain p-1 shadow-sm shrink-0"
            />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <h4 class="text-sm font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(srv.name)}</h4>
                <span class="badge-tag ${pingColor} border text-[10px] font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                  <span>${srv.ping}ms</span>
                </span>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <code class="text-xs text-cyan-600 dark:text-cyan-400 font-mono font-bold truncate select-all">${srv.host}</code>
              </div>
            </div>
          </div>

          <!-- Feature Tags Row -->
          <div class="flex items-center gap-1.5 mt-3 flex-wrap">
            <span class="badge-tag ${
              isCracked 
                ? (isLight ? 'bg-cyan-100 text-cyan-800 border-cyan-300' : 'bg-cyan-950/80 text-cyan-400 border-cyan-800/50') 
                : (isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-emerald-950/80 text-emerald-400 border-emerald-800/50')
            } border text-[10px] font-mono px-2 py-0.5 rounded-full">
              ${srv.type}
            </span>
            <span class="badge-tag bg-slate-100 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/60 text-[10px] text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-full">
              ${srv.category}
            </span>
            <span class="badge-tag bg-slate-100 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/60 text-[10px] text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-full font-mono">
              👥 ${srv.players} / ${srv.playersMax}
            </span>
          </div>

          <!-- Description -->
          <p class="text-xs text-slate-600 dark:text-slate-400 mt-2.5 leading-relaxed line-clamp-2">${escapeHtml(srv.desc)}</p>
        </div>

        <!-- Action Row -->
        <div class="flex items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800/80">
          <div class="flex items-center gap-2">
            <button onclick="quickJoinServer('${srv.host}', ${srv.port || 25565})" class="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-slate-950 text-xs font-black shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 active:scale-95 cursor-pointer">
              <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
              <span>Join Game</span>
            </button>
            <button onclick="toggleSaveServer('${srv.id}')" class="p-2 rounded-xl ${srv.saved ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : (isLight ? 'bg-slate-100 text-slate-400 border border-slate-300 hover:text-amber-500' : 'bg-slate-800 text-slate-400 border border-slate-700 hover:text-amber-400')} text-xs transition-all flex items-center justify-center cursor-pointer" title="Bookmark Server">
              <i data-lucide="star" class="w-4 h-4 ${srv.saved ? 'fill-current' : ''}"></i>
            </button>
          </div>
          <button onclick="copyIp('${srv.host}')" class="px-3.5 py-2.5 rounded-xl ${
            isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700'
          } text-xs font-bold transition-all flex items-center gap-1.5 active:scale-95 cursor-pointer">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            <span>Copy IP</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
  refreshLucideIcons();
}

function toggleShowMoreServers() {
  STATE.showAllServers = !STATE.showAllServers;
  renderServers();
}

async function scanCustomServer() {
  const input = document.getElementById('custom-server-ip-input');
  const resultDiv = document.getElementById('custom-server-result');
  const scanBtn = document.getElementById('custom-server-scan-btn');
  if (!input || !resultDiv) return;

  const ip = input.value.trim();
  if (!ip) {
    showToast('Please enter a server IP or hostname', 'warning');
    return;
  }

  if (scanBtn) {
    scanBtn.disabled = true;
    scanBtn.innerHTML = `<i data-lucide="refresh-cw" class="w-4 h-4 animate-spin"></i><span>Scanning...</span>`;
    refreshLucideIcons();
  }

  resultDiv.classList.remove('hidden');
  resultDiv.innerHTML = `
    <div class="p-4 rounded-xl bg-slate-50 dark:bg-[#080d16] border border-slate-200 dark:border-slate-800 text-center">
      <p class="text-xs text-cyan-600 dark:text-cyan-400 font-mono animate-pulse">Pinging Minecraft API for ${escapeHtml(ip)}...</p>
    </div>
  `;

  try {
    const res = await fetch(`https://api.mcstatus.io/v2/status/java/${ip}`, {
      signal: AbortSignal.timeout(5000)
    });
    const isLight = document.documentElement.classList.contains('light');

    if (res.ok) {
      const data = await res.json();
      const isOnline = data && data.online;
      const playersOnline = (data.players?.online || 0).toLocaleString();
      const playersMax = (data.players?.max || 0).toLocaleString();
      const version = data.version?.name_clean || 'Minecraft Java';
      const motd = data.motd?.clean ? data.motd.clean.trim().replace(/\n/g, ' ') : 'Live server response received.';
      const iconUrl = data.icon || `https://api.mcsrvstat.us/icon/${ip}`;
      const latency = Math.round(data.roundTripLatency || 32);

      resultDiv.innerHTML = `
        <div class="p-4 rounded-xl ${
          isLight ? 'bg-slate-50 border-cyan-300' : 'bg-[#080d16] border-cyan-500/50'
        } border flex flex-col sm:flex-row items-center justify-between gap-4 animate-pop shadow-sm">
          <div class="flex items-center gap-3.5 flex-1 min-w-0">
            <img 
              src="${iconUrl}" 
              alt="Server Favicon" 
              onerror="this.src='https://eu.mc-api.net/v3/server/favicon/${ip}'" 
              class="w-12 h-12 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 object-contain p-1 shadow-sm shrink-0"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="text-sm font-black text-slate-900 dark:text-slate-100 font-mono truncate">${escapeHtml(ip)}</h4>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                  isOnline 
                    ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800' 
                    : 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-400 border-rose-300 dark:border-rose-800'
                }">
                  ${isOnline ? '● LIVE ONLINE' : '○ OFFLINE'}
                </span>
                <span class="text-[10px] font-mono text-cyan-600 dark:text-cyan-400">${latency}ms</span>
              </div>
              <p class="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-1">${escapeHtml(motd)}</p>
              <div class="flex items-center gap-3 text-[10px] font-mono text-slate-500 dark:text-slate-400 mt-1">
                <span>👥 ${playersOnline} / ${playersMax} Players</span>
                <span>•</span>
                <span>🏷️ ${escapeHtml(version)}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button onclick="joinServer('${escapeHtml(ip)}')" class="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all shadow-sm cursor-pointer">
              Connect ▶
            </button>
            <button onclick="copyIp('${escapeHtml(ip)}')" class="px-3 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold transition-all cursor-pointer">
              Copy
            </button>
          </div>
        </div>
      `;
    } else {
      throw new Error('Server unreachable');
    }
  } catch (err) {
    resultDiv.innerHTML = `
      <div class="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 text-xs text-rose-700 dark:text-rose-400 font-mono">
        ✕ Server "${escapeHtml(ip)}" is offline or could not be reached by the live status API.
      </div>
    `;
  } finally {
    if (scanBtn) {
      scanBtn.disabled = false;
      scanBtn.innerHTML = `<i data-lucide="radar" class="w-4 h-4"></i><span>Scan Live</span>`;
      refreshLucideIcons();
    }
  }
}

function refreshServersLive() {
  loadServersLive();
  showToast("✓ Refreshed live server pings and player counts!", "success");
}

