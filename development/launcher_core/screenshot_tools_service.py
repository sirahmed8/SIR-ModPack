import os
import sys
import ctypes
import subprocess
import glob

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02

class ScreenshotToolsService:
    """Windows native desktop wallpaper setter and media studio orchestrator."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def set_as_wallpaper(self, image_path):
        if not os.path.exists(image_path):
            return {"success": False, "error": "Image file not found"}
            
        try:
            # Call SystemParametersInfoW
            abs_path = os.path.abspath(image_path)
            res = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
            )
            if res:
                return {
                    "success": True,
                    "message": "✓ Successfully set Minecraft screenshot as Windows desktop wallpaper!"
                }
            else:
                return {"success": False, "error": "Failed to invoke Windows SystemParametersInfo"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reveal_in_explorer(self, file_path):
        try:
            abs_path = os.path.abspath(file_path)
            subprocess.run(f'explorer /select,"{abs_path}"', shell=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
