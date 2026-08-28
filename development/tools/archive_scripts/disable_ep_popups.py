import os

EP_CONFIG = """# This file stores configuration options for the Euphoria Patcher mod
# Made for version 1.9.3
# Thank you for using Euphoria Patches - SpacEagle17

[display]
	# Option for the sodium message popup logging.
	doPopUpLogging = false

	# Option that enables or disables the in-game shader messages.
	doDisplayShaderInGameMessage = false

[updates]
	doUpdateChecking = "none"

[maintenance]
	doRenameOldShaderFiles = false
	doDeleteOldShaderFiles = false

[debug]
	doDebugLogging = false

[advanced]
	alternativeShaderNames = ""
	autoMergeBlockProperties = false
"""

TARGETS = [
    r"d:\mods\config\euphoria_patcher",
    r"d:\mods\Aetheris_Modpack_Modern_26.2\config\euphoria_patcher",
    r"C:\Users\a7med\AppData\Roaming\.minecraft\config\euphoria_patcher",
    r"C:\Users\a7med\.lunarclient\profiles\26\config\euphoria_patcher",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\config\euphoria_patcher"
]

for t in TARGETS:
    os.makedirs(t, exist_ok=True)
    cfg_file = os.path.join(t, "settings.toml")
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write(EP_CONFIG)
    print(f"Updated EuphoriaPatcher config: {cfg_file}")

print("Disabled EuphoriaPatcher popup toasts successfully.")
