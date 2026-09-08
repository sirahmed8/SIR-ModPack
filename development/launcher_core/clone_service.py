import os
import shutil
import time

class CloneService:
    """Clones and creates isolated lightweight instances for testing, speedrunning, or custom modpacks."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def clone_instance(self, source_id="26.2", new_name="SIR_Cloned_Instance"):
        source_dir = os.path.join(self.root_dir, "instances", source_id)
        if not os.path.exists(source_dir):
            source_dir = os.path.join(self.root_dir, "instances", "26.2")
            
        clean_name = new_name.strip().replace(" ", "_")
        target_dir = os.path.join(self.root_dir, "instances", clean_name)
        
        if os.path.exists(target_dir):
            clean_name = f"{clean_name}_{int(time.time())}"
            target_dir = os.path.join(self.root_dir, "instances", clean_name)
            
        try:
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy essential directories and files
            if os.path.exists(source_dir):
                for item in os.listdir(source_dir):
                    s_item = os.path.join(source_dir, item)
                    d_item = os.path.join(target_dir, item)
                    
                    if os.path.isdir(s_item):
                        if item in [".fabric", "logs", "crash-reports"]:
                            continue
                        shutil.copytree(s_item, d_item, ignore=shutil.ignore_patterns("*.log", "*.hprof"))
                    else:
                        shutil.copy2(s_item, d_item)
                        
            return {
                "success": True,
                "cloned_id": clean_name,
                "path": target_dir,
                "message": f"✓ Successfully cloned instance '{source_id}' into new profile '{clean_name}'!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
