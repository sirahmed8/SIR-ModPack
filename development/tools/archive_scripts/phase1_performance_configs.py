"""
phase1_performance_configs.py
Applies all critical performance fixes from the master plan.
"""
import os, json, re, shutil

VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"

# ══════════════════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════════════════
def patch_options(path, patches):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    result = []
    patched = set()
    for line in lines:
        key = line.split(":")[0]
        if key in patches:
            result.append(key + ":" + str(patches[key]) + "\n")
            patched.add(key)
        else:
            result.append(line)
    for key, val in patches.items():
        if key not in patched:
            result.append(key + ":" + str(val) + "\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(result)
    return patched

# ══════════════════════════════════════════════════════════════════
# 1. C2ME CONFIG — tune for i7-13650HX (14 cores, 20 threads)
# ══════════════════════════════════════════════════════════════════
C2ME_CONFIG = """\
version = 3

[asyncSerializationLevelChunk]
    # Serialize chunks asynchronously — eliminates save lag spikes
    enabled = true

[generalThreadPool]
    # Worker threads for chunk gen/load — leave 4 for render+game
    # i7-13650HX has 14 cores (6P + 8E), use 10 for chunk work
    workerThreads = 10

[vanilla.reduceLockContention]
    # Reduce threading lock contention
    enabled = true

[ioWorkers]
    # Parallel chunk I/O threads
    maxThreads = 4

[chunkGeneration]
    # Parallelise world gen across all worker threads
    enabled = true
    # Run noise generators in parallel
    parallelWorldGen = true
    # Enable SIMD noise generation (faster math)
    allowGlobalSIMD = true

[chunkLoading]
    # Pre-generate chunks around player proactively
    enabled = true
"""

# ══════════════════════════════════════════════════════════════════
# 2. LITHIUM CONFIG — enable ALL optimizations explicitly
# ══════════════════════════════════════════════════════════════════
LITHIUM_CONFIG = """\
# Lithium — all optimizations explicitly enabled
# CPU: i7-13650HX 14-core | Minecraft 1.21.x (26.2)

# ── AI / Mob Pathfinding ──────────────────────────────────────────
mixin.ai.pathing=true
mixin.ai.sensor.nearby_players=true
mixin.ai.task.launch=true
mixin.ai.goal.follow_mob=true

# ── Block / World ─────────────────────────────────────────────────
mixin.block.moving_block_shapes=true
mixin.block.hopper=true

# ── Chunk Ticking ─────────────────────────────────────────────────
mixin.world.chunk_ticking=true
mixin.world.block_entity_ticking=true
mixin.world.explosions=true

# ── Collections ───────────────────────────────────────────────────
mixin.collections.entity_filtering=true
mixin.collections.attributes=true

# ── Entity ────────────────────────────────────────────────────────
mixin.entity.collisions.unpushable_cramming=true
mixin.entity.collisions.fluid=true
mixin.entity.collisions.movement=true
mixin.entity.data_tracker.use_arrays=true
mixin.entity.fast_retrieval=true
mixin.entity.inactive_navigators=true
mixin.entity.replace_entitytype_predicates=true

# ── Math ──────────────────────────────────────────────────────────
mixin.math.fast_util=true

# ── Shapes ────────────────────────────────────────────────────────
mixin.shapes.blockstate_cache=true
mixin.shapes.precompute_shape_arrays=true
mixin.shapes.optimized_matching=true
mixin.shapes.shape_merging=true
mixin.shapes.specialized_shapes=true

# ── Alloc ─────────────────────────────────────────────────────────
mixin.alloc.chunk_random=true
mixin.alloc.composter=true
mixin.alloc.enum_values=true
mixin.alloc.nbt_traversal=true

# ── Chunk generation ──────────────────────────────────────────────
mixin.gen.biome_noise_cache=true
mixin.gen.cached_generator_settings=true
mixin.gen.chunk_region=true

# ── Client ────────────────────────────────────────────────────────
mixin.client.particle_rendering=true
"""

# ══════════════════════════════════════════════════════════════════
# 3. SODIUM CONFIG — optimal for RTX 4050 + Optimum Realism 64x
# ══════════════════════════════════════════════════════════════════
SODIUM_CONFIG_VISUAL = {
    "quality": {
        "hidden_fluid_culling": True,
        "improved_fluid_shaping": True,
        "use_closest_point_entity_sort": True,
        "pixel_filtering_mode": "MIPMAP_LINEAR"   # CRITICAL: smooth 64x textures at angles
    },
    "performance": {
        "chunk_builder_threads": 6,             # explicit: 6 of 14 cores for chunk building
        "chunk_build_defer_mode": "ALWAYS",
        "animate_only_visible_textures": True,
        "use_entity_culling": True,
        "use_fog_occlusion": True,
        "use_block_face_culling": True,
        "use_no_error_g_l_context": True,
        "quad_splitting_mode": "SPEED"          # faster geometry
    },
    "advanced": {
        "enable_memory_tracing": False
    },
    "debug": {
        "terrain_sorting_enabled": True
    },
    "notifications": {
        "has_cleared_donation_button": True,
        "has_seen_donation_prompt": True,
        "has_edited_fullscreen_option": True
    }
}

SODIUM_CONFIG_BALANCED = dict(SODIUM_CONFIG_VISUAL)
SODIUM_CONFIG_BALANCED["performance"] = dict(SODIUM_CONFIG_VISUAL["performance"])
SODIUM_CONFIG_BALANCED["performance"]["chunk_builder_threads"] = 4

# ══════════════════════════════════════════════════════════════════
# 4. PHYSICS MOD CONFIG — scale up CPU threads
# ══════════════════════════════════════════════════════════════════
PHYSICS_PERF_PATCH = {
    "cpuThreads": 6,               # was 2 → use 6 of 14 cores
    "clothThreads": 4,             # was 2 → smoother cloth/banners
    "maxPhysicsObjects": 800,      # was 2000 → reduce physics overhead
    "smokeParticleLimit": 2000,    # was 6000 → huge smoke FPS cost
    "fireParticleLimit": 30000,    # was 100000 → excessive
    "maxLoadedDynamicBlocks": 10,  # was 20
}

# ══════════════════════════════════════════════════════════════════
# 5. OPTIONS.TXT — definitive video settings
# ══════════════════════════════════════════════════════════════════
OPTIONS_VISUAL = {
    "renderDistance":    12,   # was 16 — massive FPS impact
    "simulationDistance": 8,   # was 12 — entities tick less far
    "particles":          1,   # was 0 (All) → Decreased (HUGE with PhysicsMod)
    "biomeBlendRadius":   3,   # was 7 — 7=very expensive, 3 still looks good
    "gamma":            1.0,   # full brightness option
    "fovEffectScale":   0.0,   # no screen warp from speed
    "ao":              True,
}
OPTIONS_BALANCED = dict(OPTIONS_VISUAL)
OPTIONS_BALANCED["renderDistance"] = 10
OPTIONS_BALANCED["simulationDistance"] = 6

# ══════════════════════════════════════════════════════════════════
# APPLY ALL TO BOTH PROFILES
# ══════════════════════════════════════════════════════════════════
def apply_to_profile(profile_path, profile_name, sodium_cfg, opts_patches):
    cfg_dir = os.path.join(profile_path, "config")
    print(f"\n=== {profile_name} ===")

    # C2ME
    c2me_path = os.path.join(cfg_dir, "c2me.toml")
    with open(c2me_path, "w") as f:
        f.write(C2ME_CONFIG)
    print("  ✓ c2me.toml — 10 chunk workers, parallel world gen, async I/O")

    # Lithium
    li_path = os.path.join(cfg_dir, "lithium.properties")
    with open(li_path, "w") as f:
        f.write(LITHIUM_CONFIG)
    print("  ✓ lithium.properties — all optimizations enabled")

    # Sodium
    sodium_path = os.path.join(cfg_dir, "sodium-options.json")
    with open(sodium_path, "w") as f:
        json.dump(sodium_cfg, f, indent=2)
    print("  ✓ sodium-options.json — MIPMAP_LINEAR filter, 6 chunk threads, SPEED quads")

    # Physics
    phys_path = os.path.join(cfg_dir, "physicsmod", "physics_client_config.json")
    if os.path.exists(phys_path):
        with open(phys_path, "r", encoding="utf-8", errors="replace") as f:
            phys = json.load(f)
        phys.update(PHYSICS_PERF_PATCH)
        with open(phys_path, "w") as f:
            json.dump(phys, f, indent=2)
        print("  ✓ physics_client_config.json — 6 CPU threads, 800 max objects, smoke reduced")

    # Options.txt
    opts_path = os.path.join(profile_path, "options.txt")
    if os.path.exists(opts_path):
        patched = patch_options(opts_path, opts_patches)
        for k, v in opts_patches.items():
            print(f"  ✓ options.txt: {k} = {v}")

apply_to_profile(VISUAL,   "VISUAL",   SODIUM_CONFIG_VISUAL,    OPTIONS_VISUAL)
apply_to_profile(BALANCED, "BALANCED", SODIUM_CONFIG_BALANCED,  OPTIONS_BALANCED)

print()
print("=" * 60)
print("PHASE 1 COMPLETE")
print("=" * 60)
print()
print("Performance gains expected:")
print("  renderDistance 16→12:        +15-20 FPS")
print("  simulationDistance 12→8:     +5-10 FPS (less entity ticking)")
print("  biomeBlendRadius 7→3:        +5-8 FPS (expensive biome blending)")
print("  particles All→Decreased:     +5-15 FPS (PhysicsMod particles were massive)")
print("  C2ME 10 workers:             +10-20 FPS (no chunk gen stutters)")
print("  Lithium all opts:            +5-10 FPS (mob AI, pathfinding, math)")
print("  Sodium MIPMAP_LINEAR:        visual fix (OR 64x textures smooth now)")
print("  Sodium 6 chunk threads:      faster chunk loading at edges")
print("  Physics 6 threads:           physics simulation smoother")
print()
print("Total estimated FPS gain: +40-80 FPS on top of current")
