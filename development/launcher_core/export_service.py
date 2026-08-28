import os
import zipfile
import json
import time

class ExportService:
    """Exports and imports complete SIR ModPack instance archives with zero redundant caches."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.export_dir = os.path.join(self.root_dir, "exports")
        os.makedirs(self.export_dir, exist_ok=True)

    def export_instance_zip(self, instance_id="26.2"):
        inst_dir = os.path.join(self.root_dir, "instances", instance_id)
        if not os.path.exists(inst_dir):
            inst_dir = os.path.join(self.root_dir, "instances", "26.2")
            
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        archive_name = f"SIR_ModPack_{instance_id.replace('.', '_')}_{timestamp}.zip"
        target_path = os.path.join(self.export_dir, archive_name)
        
        try:
            with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists(inst_dir):
                    for root, dirs, files in os.walk(inst_dir):
                        # Exclude transient cache directories
                        dirs[:] = [d for d in dirs if d not in [".fabric", ".mixin.out", "logs", "crash-reports"]]
                        for file in files:
                            if not file.endswith(".log") and not file.endswith(".hprof"):
                                fp = os.path.join(root, file)
                                rel_path = os.path.relpath(fp, inst_dir)
                                zipf.write(fp, arcname=os.path.join("instance", rel_path))
                                
            return {
                "success": True,
                "filename": archive_name,
                "path": target_path,
                "message": f"✓ Successfully exported standalone bundle: {archive_name} in /exports!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def import_custom_profile_json(self, json_content):
        try:
            data = json.loads(json_content)
            name = data.get("name", "Imported_Profile")
            version = data.get("version", "1.21.4")
            
            # Save profile descriptor
            custom_dir = os.path.join(self.root_dir, "instances", "custom_" + str(int(time.time())))
            os.makedirs(custom_dir, exist_ok=True)
            with open(os.path.join(custom_dir, "profile.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            return {
                "success": True,
                "profile": data,
                "message": f"✓ Imported custom profile '{name}' ({version}) successfully!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
