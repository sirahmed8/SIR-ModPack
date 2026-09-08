def query_curseforge_mods(query="", limit=10):
    sample_cf = [
        {"id": "cf-jei", "slug": "jei", "title": "Just Enough Items (JEI)", "desc": "Item and recipe viewing mod for Minecraft.", "author": "mezz", "downloads": "250,000,000", "source": "CurseForge"},
        {"id": "cf-appleskin", "slug": "appleskin", "title": "AppleSkin", "desc": "Food and saturation HUD information.", "author": "squeek502", "downloads": "180,000,000", "source": "CurseForge"},
        {"id": "cf-journeymap", "slug": "journeymap", "title": "JourneyMap", "desc": "Real-time mapping in-game and on web browser.", "author": "techbrew", "downloads": "210,000,000", "source": "CurseForge"}
    ]
    hits = [m for m in sample_cf if not query or query.lower() in m["title"].lower() or query.lower() in m["desc"].lower()]
    return hits, None
