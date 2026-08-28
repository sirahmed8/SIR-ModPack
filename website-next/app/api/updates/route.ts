import { NextRequest, NextResponse } from "next/server";
import { SECURITY_HEADERS } from "@/lib/security";

export const dynamic = "force-static";

export async function GET(req: NextRequest) {
  const versionManifest = {
    release_version: "1.0.0",
    release_date: "2026-08-23",
    status: "STABLE_RELEASE",
    download_urls: {
      dispatcher: "https://sir-modpack.web.app/share/SIR_ModPack.exe",
      installer: "https://sir-modpack.web.app/share/SIR_ModPack.exe",
      launcher: "https://sir-modpack.web.app/share/SIR_ModPack.exe",
      server_manager: "https://sir-modpack.web.app/share/SIR_ModPack.exe",
      full_bundle: "https://sir-modpack.web.app/share/SIR_Full_Offline_Bundle.zip"
    },
    checksums: {
      dispatcher_sha256: "B7CA7EFBBD5A16E7B79BF67E1388EF09ACC480B0DFAC403473DC4CAA1CFD3761",
      installer_sha256: "B7CA7EFBBD5A16E7B79BF67E1388EF09ACC480B0DFAC403473DC4CAA1CFD3761",
      launcher_sha256: "B7CA7EFBBD5A16E7B79BF67E1388EF09ACC480B0DFAC403473DC4CAA1CFD3761",
      server_manager_sha256: "B7CA7EFBBD5A16E7B79BF67E1388EF09ACC480B0DFAC403473DC4CAA1CFD3761"
    },
    changelog: [
      "22 Full Static Production Routes with Turbopack acceleration.",
      "Dedicated SIR Server Manager 3.0 with 0-Port-Forwarding Cloud Tunneling.",
      "In-Launcher 3D Skin Studio & Capes Wardrobe.",
      "SIR Shaders 2.0 Optical Engine Lab with live custom shader profile generator.",
      "240+ verified mods index in /mods catalog."
    ],
    compatibility: {
      java_minimum: 21,
      java_recommended: 21,
      os_supported: ["Windows 10 64-bit", "Windows 11 64-bit", "Linux", "macOS"]
    }
  };

  return NextResponse.json(versionManifest, {
    headers: {
      ...SECURITY_HEADERS,
      "Cache-Control": "public, max-age=60, s-maxage=300",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
