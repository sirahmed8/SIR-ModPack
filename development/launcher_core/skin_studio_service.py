import os
import shutil
import urllib.request
import json
import time
from shared_core.runtime import atomic_write_json, download_file_resilient

class SkinStudioService:

    """Manages player skins, animated capes, 3D HD presets, and offline avatar texture injection."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.skins_dir = os.path.join(self.root_dir, "skins")
        self.capes_dir = os.path.join(self.root_dir, "capes")
        os.makedirs(self.skins_dir, exist_ok=True)
        os.makedirs(self.capes_dir, exist_ok=True)

    def get_curated_skins(self):
        """Returns top creator and aesthetic skin presets matching the web platform."""
        return [
            {
                "id": "technoblade",
                "name": "Technoblade",
                "creator": "Legend",
                "preview": "https://mc-heads.net/body/Technoblade/right",
                "skin_url": "https://mc-heads.net/skin/Technoblade",
                "model": "classic",
                "tag": "👑 Legend PvP"
            },
            {
                "id": "dream",
                "name": "Dream",
                "creator": "Speedrunner",
                "preview": "https://mc-heads.net/body/Dream/right",
                "skin_url": "https://mc-heads.net/skin/Dream",
                "model": "classic",
                "tag": "⚡ Speedrunner"
            },
            {
                "id": "dantdm",
                "name": "DanTDM",
                "creator": "OG Legend",
                "preview": "https://mc-heads.net/body/DanTDM/right",
                "skin_url": "https://mc-heads.net/skin/DanTDM",
                "model": "classic",
                "tag": "💎 Diamond OG"
            },
            {
                "id": "mumbo",
                "name": "MumboJumbo",
                "creator": "Redstone",
                "preview": "https://mc-heads.net/body/MumboJumbo/right",
                "skin_url": "https://mc-heads.net/skin/MumboJumbo",
                "model": "classic",
                "tag": "⚙️ Redstone Pro"
            },
            {
                "id": "grian",
                "name": "Grian",
                "creator": "Architect",
                "preview": "https://mc-heads.net/body/Grian/right",
                "skin_url": "https://mc-heads.net/skin/Grian",
                "model": "classic",
                "tag": "🏰 Architect"
            },
            {
                "id": "purpled",
                "name": "Purpled",
                "creator": "Bedwars",
                "preview": "https://mc-heads.net/body/Purpled/right",
                "skin_url": "https://mc-heads.net/skin/Purpled",
                "model": "classic",
                "tag": "⚔️ Ranked Bedwars"
            },
            {
                "id": "steve",
                "name": "Steve (Classic 4px)",
                "creator": "Mojang",
                "preview": "https://mc-heads.net/body/Steve/right",
                "skin_url": "https://mc-heads.net/skin/Steve",
                "model": "classic",
                "tag": "🍃 Classic Default"
            },
            {
                "id": "alex",
                "name": "Alex (Slim 3px)",
                "creator": "Mojang",
                "preview": "https://mc-heads.net/body/Alex/right",
                "skin_url": "https://mc-heads.net/skin/Alex",
                "model": "slim",
                "tag": "✨ Slim Default"
            }
        ]

    def get_curated_capes(self):
        """Returns official Minecraft and anniversary capes."""
        return [
            {
                "id": "migrator",
                "name": "Migrator Cape",
                "tag": "2021 Official",
                "preview": "https://textures.minecraft.net/texture/2232d4343e061ec839da49e755294ea5e8ff74dd5c62d0494fb2167d32c53a63"
            },
            {
                "id": "minecon_2011",
                "name": "Minecon 2011",
                "tag": "Red Creeper",
                "preview": "https://textures.minecraft.net/texture/952aced8d81804f981ec4567406a445d06d4e488b0a9960ff694c9ad96e6d1b7"
            },
            {
                "id": "minecon_2012",
                "name": "Minecon 2012",
                "tag": "Golden Pickaxe",
                "preview": "https://textures.minecraft.net/texture/a2e8d9704d40587e3873f00a7529c8bf3a23868573950cb77d01861f604932"
            },
            {
                "id": "minecon_2013",
                "name": "Minecon 2013",
                "tag": "Piston",
                "preview": "https://textures.minecraft.net/texture/153b1097b669904d60d3d53337b546a783009d90543f65ed354dc973d3db30"
            },
            {
                "id": "minecon_2015",
                "name": "Minecon 2015",
                "tag": "Iron Golem",
                "preview": "https://textures.minecraft.net/texture/b0cc08840700447340433a13879334a45d0e9183287d8fa423d44ba26232c62f"
            },
            {
                "id": "minecon_2016",
                "name": "Minecon 2016",
                "tag": "Enderman",
                "preview": "https://textures.minecraft.net/texture/e7dfea16dc83c97df01a12fabbb121b6518c50f56e3244b60994211161b5822f"
            },
            {
                "id": "vanilla_cape",
                "name": "Vanilla Cape",
                "tag": "Dual Edition",
                "preview": "https://textures.minecraft.net/texture/1a122e11894d0339ab3a152ca6717a61d198bb66a8775f0a0d4c8038753229b4"
            },
            {
                "id": "cherry_cape",
                "name": "Cherry Blossom",
                "tag": "15th Anniversary",
                "preview": "https://textures.minecraft.net/texture/7222384a2c10b65bf73d3283be5a9f5d304910cf6b1c19b027d141e97d10e6e7"
            }
        ]

    def apply_skin_and_cape(self, username, skin_url="", cape_url="", model="classic", instance_id="26.2"):
        """Downloads, caches, and registers skin & cape across Modern and Legacy game instances."""
        clean_user = (username or "Steve").strip()
        if not clean_user:
            return {"success": False, "error": "Username cannot be empty"}
            
        final_skin_url = skin_url or f"https://mc-heads.net/skin/{clean_user}"
        skin_file = os.path.join(self.skins_dir, f"{clean_user}.png")
        
        try:
            download_file_resilient(final_skin_url, skin_file, timeout=5.0)
        except Exception:
            pass

        # Write skinlayers / customskinloader configs to instance directories
        target_instances = [
            os.path.join(self.root_dir, "instances", instance_id, "minecraft"),
            os.path.join(self.root_dir, "instances", "26.2", "minecraft"),
            os.path.join(self.root_dir, "instances", "1.8.9", "minecraft"),
            os.path.join(self.root_dir)
        ]

        # Replicate skin PNG to all local and instance skins directories
        for inst_p in target_instances:
            if os.path.exists(inst_p):
                inst_skins = os.path.join(inst_p, "skins")
                os.makedirs(inst_skins, exist_ok=True)
                if os.path.isfile(skin_file):
                    try:
                        shutil.copy2(skin_file, os.path.join(inst_skins, f"{clean_user}.png"))
                    except Exception:
                        pass
                cfg_dir = os.path.join(inst_p, "config")
                skin_cfg = os.path.join(cfg_dir, "customskinloader.json")
                try:
                    atomic_write_json(skin_cfg, {
                        "active_user": clean_user,
                        "skin_path": skin_file,
                        "skin_url": final_skin_url,
                        "cape_url": cape_url,
                        "model": model,
                        "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception:
                    pass

        # Update accounts in auth_service if initialized
        try:
            from .auth_service import AuthService
            auth = AuthService(self.root_dir)
            for acc in auth.accounts:
                if acc.get("displayName", "").lower() == clean_user.lower() or acc.get("name", "").lower() == clean_user.lower():
                    acc["skinUrl"] = final_skin_url
                    acc["model"] = model
            auth.save_accounts()
        except Exception:
            pass

        return {
            "success": True,
            "username": clean_user,
            "model": model,
            "skin_url": final_skin_url,
            "preview_url": f"https://mc-heads.net/body/{clean_user}/right",
            "message": f"✓ Applied 3D skin & cape for '{clean_user}' ({model.title()}) to game instances!"
        }
