import urllib.request
import urllib.parse
import json

MODRINTH_CATEGORIES = [
    ("⛏️ Ores & Resources", "technology"),
    ("🍴 Food & Farming", "food"),
    ("⚡ Tech & Machinery", "technology"),
    ("🏰 Worldgen & Biomes", "worldgen"),
    ("🪄 Magic & Spells", "magic"),
    ("🎒 Storage & Chests", "storage"),
    ("👗 Cosmetics & Capes", "cosmetics"),
    ("🚀 Performance / FPS", "optimization"),
    ("🛡️ Armor & Tools", "equipment")
]

def query_modrinth_mods(query="", loader="fabric", version="26.2", category=None, limit=20, sort="relevance"):
    facets = []
    if loader and loader.lower() != "all":
        facets.append([f"categories:{loader.lower()}"])
    if version and version.lower() != "all":
        facets.append([f"versions:{version}"])
    if category:
        facets.append([f"categories:{category}"])
    params = {
        "query": query,
        "limit": limit,
        "index": "relevance" if sort == "relevance" else "downloads"
    }
    if facets:
        params["facets"] = json.dumps(facets)
    url = f"https://api.modrinth.com/v2/search?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = []
            for h in data.get("hits", []):
                hits.append({
                    "id": h.get("project_id"),
                    "slug": h.get("slug"),
                    "title": h.get("title"),
                    "desc": h.get("description", ""),
                    "author": h.get("author", "Unknown"),
                    "icon": h.get("icon_url", ""),
                    "downloads": f"{h.get('downloads', 0):,}",
                    "follows": f"{h.get('follows', 0):,}",
                    "source": "Modrinth",
                    "categories": h.get("categories", []),
                    "latest_version": h.get("latest_version", "")
                })
            return hits, None
    except Exception as e:
        return [], str(e)
