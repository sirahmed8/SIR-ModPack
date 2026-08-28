/**
 * Cloudinary CDN Client & Asset Optimizer for the SIR Ecosystem
 * Cloud Name: dfvh4jcsh
 */

const CLOUD_NAME = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME || "dfvh4jcsh";
const BASE_URL = `https://res.cloudinary.com/${CLOUD_NAME}/image/upload`;

export interface CloudinaryTransformOptions {
  width?: number;
  height?: number;
  quality?: "auto" | "auto:best" | "auto:good" | "auto:eco" | number;
  format?: "auto" | "webp" | "avif" | "png" | "jpg";
  crop?: "fill" | "fit" | "scale" | "thumb" | "pad";
  gravity?: "auto" | "center" | "face";
  blur?: number;
  effect?: string;
  dpr?: number | "auto";
}

/**
 * Build an optimized Cloudinary delivery URL
 */
export function getCloudinaryUrl(publicId: string, options: CloudinaryTransformOptions = {}): string {
  if (!publicId) return "";
  
  // If it is already a full remote URL, use Cloudinary fetch
  if (publicId.startsWith("http://") || publicId.startsWith("https://")) {
    const transforms: string[] = ["f_auto", "q_auto"];
    if (options.width) transforms.push(`w_${options.width}`);
    if (options.height) transforms.push(`h_${options.height}`);
    if (options.crop) transforms.push(`c_${options.crop}`);
    return `https://res.cloudinary.com/${CLOUD_NAME}/image/fetch/${transforms.join(",")}/${encodeURIComponent(publicId)}`;
  }

  const transformations: string[] = [];

  // Default smart optimizations
  transformations.push(`f_${options.format || "auto"}`);
  transformations.push(`q_${options.quality || "auto"}`);

  if (options.width) transformations.push(`w_${options.width}`);
  if (options.height) transformations.push(`h_${options.height}`);
  if (options.crop) transformations.push(`c_${options.crop || "fill"}`);
  if (options.gravity) transformations.push(`g_${options.gravity}`);
  if (options.dpr) transformations.push(`dpr_${options.dpr}`);
  if (options.blur) transformations.push(`e_blur:${options.blur}`);
  if (options.effect) transformations.push(`e_${options.effect}`);

  const transformString = transformations.join(",");
  const cleanId = publicId.replace(/^\//, "");

  return `${BASE_URL}/${transformString}/${cleanId}`;
}

/**
 * Get 3D Isometric or 2D Minecraft Head / Body Avatar
 */
export function getMinecraftAvatarUrl(usernameOrUuid: string, size = 128, type: "head" | "body" | "isometric" = "isometric"): string {
  if (!usernameOrUuid || usernameOrUuid.trim() === "") {
    return `https://crafatar.com/renders/head/8667ba71-b85a-4004-af54-457a9734eed7?size=${size}&overlay=true`;
  }

  const target = encodeURIComponent(usernameOrUuid.trim());
  
  if (type === "head") {
    return `https://crafatar.com/avatars/${target}?size=${size}&overlay=true`;
  }
  if (type === "body") {
    return `https://crafatar.com/renders/body/${target}?size=${size}&overlay=true`;
  }
  
  // Default isometric 3D head render
  return `https://crafatar.com/renders/head/${target}?size=${size}&overlay=true`;
}

/**
 * Asset preset helpers
 */
export const SirAssets = {
  logo: getCloudinaryUrl("sir-ecosystem/brand/sir_logo_neon.png", { width: 512, format: "webp" }),
  bannerHero: getCloudinaryUrl("sir-ecosystem/banners/hero_shader_bg.jpg", { width: 1920, quality: "auto:good" }),
  extremeShaderPreview: getCloudinaryUrl("sir-ecosystem/shaders/sir_extreme_raytracing.jpg", { width: 800, quality: "auto" }),
  balancedShaderPreview: getCloudinaryUrl("sir-ecosystem/shaders/sir_balanced_144fps.jpg", { width: 800, quality: "auto" }),
  havocBadge: getCloudinaryUrl("sir-ecosystem/havoc/havoc_injector_banner.png", { width: 600, quality: "auto" }),
  installerMockup: getCloudinaryUrl("sir-ecosystem/launcher/sir_installer_v100_mock.png", { width: 900, quality: "auto" })
};
