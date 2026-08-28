"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState, useMemo, useEffect, useRef } from "react";
import Link from "next/link";
import { 
  Cpu, 
  Gauge, 
  Sparkles, 
  Swords, 
  Zap, 
  ArrowLeft, 
  ArrowRight, 
  Activity, 
  CheckCircle2, 
  Sliders, 
  Search, 
  Flame, 
  Monitor, 
  HardDrive, 
  ShieldCheck,
  RotateCcw,
  Clock,
  TrendingDown,
  Layers,
  Award
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { CyberSelect } from "@/components/CyberSelect";

interface GpuSpec {
  id: string;
  name: string;
  brand: "NVIDIA" | "AMD" | "Intel" | "Apple" | "APU";
  tier: string;
  rank: number; // 1 (Best) to 120 (Lowest)
  baseFps: number; // Base modern shader 1080p FPS
  vram: string;
}

interface CpuSpec {
  id: string;
  name: string;
  brand: "Intel" | "AMD" | "Apple" | "APU";
  tier: string;
  rank: number; // 1 (Best) to 70 (Lowest)
  multiplier: number;
  cores: string;
}

// Master Global GPU Catalog (120+ GPUs sorted logically from Highest Performance Tier to Budget)
// Master Global GPU Catalog (100+ GPUs sorted logically from Highest Performance Tier to Budget)
const ALL_GPUS: GpuSpec[] = [
  // --- TIER 0: GOD TIER & 8K CINEMATIC (Score 300+) ---
  { id: "rtx5090", name: "NVIDIA GeForce RTX 5090 (32GB)", brand: "NVIDIA", tier: "⚡ S+ Ultra Enthusiast 8K", rank: 1, baseFps: 350, vram: "32GB GDDR7" },
  { id: "rtx5080", name: "NVIDIA GeForce RTX 5080 (16GB)", brand: "NVIDIA", tier: "⚡ S+ Flagship 4K Extreme", rank: 2, baseFps: 295, vram: "16GB GDDR7" },
  { id: "rtx4090", name: "NVIDIA GeForce RTX 4090 (24GB)", brand: "NVIDIA", tier: "⚡ S+ Flagship 4K Master", rank: 3, baseFps: 280, vram: "24GB GDDR6X" },
  { id: "rx7900xtx", name: "AMD Radeon RX 7900 XTX (24GB)", brand: "AMD", tier: "⚡ S+ Flagship 4K AMD", rank: 4, baseFps: 270, vram: "24GB GDDR6" },
  { id: "rtx4080s", name: "NVIDIA GeForce RTX 4080 Super (16GB)", brand: "NVIDIA", tier: "⚡ S+ Flagship 4K", rank: 5, baseFps: 250, vram: "16GB GDDR6X" },
  { id: "rtx5070ti", name: "NVIDIA GeForce RTX 5070 Ti (16GB)", brand: "NVIDIA", tier: "⚡ S+ High-End 4K", rank: 6, baseFps: 245, vram: "16GB GDDR7" },
  { id: "m4_max", name: "Apple M4 Max (40-Core GPU)", brand: "Apple", tier: "⚡ S+ Apple Silicon King", rank: 7, baseFps: 240, vram: "128GB Unified" },
  { id: "rtx4080", name: "NVIDIA GeForce RTX 4080 (16GB)", brand: "NVIDIA", tier: "⚡ S+ Flagship 4K", rank: 8, baseFps: 235, vram: "16GB GDDR6X" },
  { id: "rx7900xt", name: "AMD Radeon RX 7900 XT (20GB)", brand: "AMD", tier: "⚡ S+ High-End 4K AMD", rank: 9, baseFps: 235, vram: "20GB GDDR6" },

  // --- TIER 1: ENTHUSIAST & HIGH-END 1440p / 4K (Score 200 - 230) ---
  { id: "rtx3090ti", name: "NVIDIA GeForce RTX 3090 Ti (24GB)", brand: "NVIDIA", tier: "💎 S High-End Enthusiast", rank: 10, baseFps: 225, vram: "24GB GDDR6X" },
  { id: "rtx5070", name: "NVIDIA GeForce RTX 5070 (12GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 11, baseFps: 220, vram: "12GB GDDR7" },
  { id: "rtx5070m", name: "NVIDIA GeForce RTX 5070 Laptop (12GB)", brand: "NVIDIA", tier: "💎 S High-End Laptop", rank: 12, baseFps: 220, vram: "12GB GDDR7" },
  { id: "rx6950xt", name: "AMD Radeon RX 6950 XT (16GB)", brand: "AMD", tier: "💎 S Flagship RDNA2", rank: 13, baseFps: 220, vram: "16GB GDDR6" },
  { id: "rtx3090", name: "NVIDIA GeForce RTX 3090 (24GB)", brand: "NVIDIA", tier: "💎 S High-End Enthusiast", rank: 14, baseFps: 215, vram: "24GB GDDR6X" },
  { id: "rtx4070tis", name: "NVIDIA GeForce RTX 4070 Ti Super (16GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 15, baseFps: 215, vram: "16GB GDDR6X" },
  { id: "m3_max", name: "Apple M3 Max (40-Core GPU)", brand: "Apple", tier: "💎 S Apple Flagship", rank: 16, baseFps: 210, vram: "128GB Unified" },
  { id: "rx7900gre", name: "AMD Radeon RX 7900 GRE (16GB)", brand: "AMD", tier: "💎 S High-End 1440p", rank: 17, baseFps: 210, vram: "16GB GDDR6" },
  { id: "rtx4090m", name: "NVIDIA GeForce RTX 4090 Laptop (16GB)", brand: "NVIDIA", tier: "💎 S Laptop Flagship", rank: 18, baseFps: 205, vram: "16GB GDDR6" },
  { id: "rtx3080ti", name: "NVIDIA GeForce RTX 3080 Ti (12GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 19, baseFps: 200, vram: "12GB GDDR6X" },
  { id: "rtx4070ti", name: "NVIDIA GeForce RTX 4070 Ti (12GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 20, baseFps: 195, vram: "12GB GDDR6X" },
  { id: "rx7800xt", name: "AMD Radeon RX 7800 XT (16GB)", brand: "AMD", tier: "💎 S High-End 1440p AMD", rank: 21, baseFps: 190, vram: "16GB GDDR6" },
  { id: "rtx4070s", name: "NVIDIA GeForce RTX 4070 Super (12GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 22, baseFps: 185, vram: "12GB GDDR6X" },
  { id: "rtx3080", name: "NVIDIA GeForce RTX 3080 (10GB / 12GB)", brand: "NVIDIA", tier: "💎 S High-End 1440p", rank: 23, baseFps: 185, vram: "10GB GDDR6X" },
  { id: "rx6800xt", name: "AMD Radeon RX 6800 XT (16GB)", brand: "AMD", tier: "💎 S High-End RDNA2", rank: 24, baseFps: 185, vram: "16GB GDDR6" },
  { id: "m4_pro", name: "Apple M4 Pro (20-Core GPU)", brand: "Apple", tier: "💎 S Apple Pro Silicon", rank: 25, baseFps: 180, vram: "48GB Unified" },

  // --- TIER 2: PERFORMANCE SWEETSPOT & 1440p GAMING (Score 150 - 179) ---
  { id: "rtx4070", name: "NVIDIA GeForce RTX 4070 (12GB)", brand: "NVIDIA", tier: "🔥 A+ High-End 1440p", rank: 26, baseFps: 170, vram: "12GB GDDR6X" },
  { id: "rtx4080m", name: "NVIDIA GeForce RTX 4080 Laptop (12GB)", brand: "NVIDIA", tier: "🔥 A+ High-End Laptop", rank: 27, baseFps: 170, vram: "12GB GDDR6" },
  { id: "rx7700xt", name: "AMD Radeon RX 7700 XT (12GB)", brand: "AMD", tier: "🔥 A+ Performance 1440p", rank: 28, baseFps: 165, vram: "12GB GDDR6" },
  { id: "rtx3070ti", name: "NVIDIA GeForce RTX 3070 Ti (8GB)", brand: "NVIDIA", tier: "🔥 A+ Performance 1440p", rank: 29, baseFps: 165, vram: "8GB GDDR6X" },
  { id: "m3_pro", name: "Apple M3 Pro / M2 Max (18-30 Cores)", brand: "Apple", tier: "🔥 A+ Apple Pro Silicon", rank: 30, baseFps: 160, vram: "36GB Unified" },
  { id: "rtx2080ti", name: "NVIDIA GeForce RTX 2080 Ti (11GB)", brand: "NVIDIA", tier: "🔥 A+ Legendary Flagship", rank: 31, baseFps: 160, vram: "11GB GDDR6" },
  { id: "rx6800", name: "AMD Radeon RX 6800 (16GB)", brand: "AMD", tier: "🔥 A+ High-End 1440p", rank: 32, baseFps: 160, vram: "16GB GDDR6" },
  { id: "rtx3070", name: "NVIDIA GeForce RTX 3070 (8GB)", brand: "NVIDIA", tier: "🔥 A+ Performance 1440p", rank: 33, baseFps: 155, vram: "8GB GDDR6" },
  { id: "rx6750xt", name: "AMD Radeon RX 6750 XT (12GB)", brand: "AMD", tier: "🔥 A+ Performance 1440p", rank: 34, baseFps: 155, vram: "12GB GDDR6" },
  { id: "rx6700xt", name: "AMD Radeon RX 6700 XT (12GB)", brand: "AMD", tier: "🔥 A+ Performance 1440p", rank: 35, baseFps: 150, vram: "12GB GDDR6" },

  // --- TIER 3: MAINSTREAM 1080p / 144FPS SWEETSPOT (Score 120 - 149) ---
  { id: "rtx4060ti", name: "NVIDIA GeForce RTX 4060 Ti (8GB / 16GB)", brand: "NVIDIA", tier: "🎮 A Mainstream Sweetspot", rank: 36, baseFps: 145, vram: "8GB / 16GB" },
  { id: "rtx2080s", name: "NVIDIA GeForce RTX 2080 Super (8GB)", brand: "NVIDIA", tier: "🎮 A Performance Turing", rank: 37, baseFps: 145, vram: "8GB GDDR6" },
  { id: "rtx4070m", name: "NVIDIA GeForce RTX 4070 Laptop (8GB)", brand: "NVIDIA", tier: "🎮 A High-End Laptop", rank: 38, baseFps: 142, vram: "8GB GDDR6" },
  { id: "rtx3060ti", name: "NVIDIA GeForce RTX 3060 Ti (8GB)", brand: "NVIDIA", tier: "🎮 A Mainstream Sweetspot", rank: 39, baseFps: 140, vram: "8GB GDDR6" },
  { id: "arc_b580", name: "Intel Arc Battlemage B580 (12GB)", brand: "Intel", tier: "🎮 A Battlemage King", rank: 40, baseFps: 140, vram: "12GB GDDR6" },
  { id: "arc_b570", name: "Intel Arc Battlemage B570 (10GB)", brand: "Intel", tier: "🎮 A Battlemage Value", rank: 41, baseFps: 138, vram: "10GB GDDR6" },
  { id: "rtx2080", name: "NVIDIA GeForce RTX 2080 (8GB)", brand: "NVIDIA", tier: "🎮 A Performance Turing", rank: 42, baseFps: 138, vram: "8GB GDDR6" },
  { id: "rx7600xt", name: "AMD Radeon RX 7600 XT (16GB)", brand: "AMD", tier: "🎮 A Modern 1080p AMD", rank: 43, baseFps: 135, vram: "16GB GDDR6" },
  { id: "rtx2070s", name: "NVIDIA GeForce RTX 2070 Super (8GB)", brand: "NVIDIA", tier: "🎮 A Mainstream Turing", rank: 44, baseFps: 135, vram: "8GB GDDR6" },
  { id: "arc_a770", name: "Intel Arc A770 (16GB)", brand: "Intel", tier: "🎮 A Alchemist Flagship", rank: 45, baseFps: 135, vram: "16GB GDDR6" },
  { id: "rtx4060", name: "NVIDIA GeForce RTX 4060 (8GB)", brand: "NVIDIA", tier: "🎮 A Modern 1080p Standard", rank: 46, baseFps: 130, vram: "8GB GDDR6" },
  { id: "gtx1080ti", name: "NVIDIA GeForce GTX 1080 Ti (11GB)", brand: "NVIDIA", tier: "🎮 A Pascal Legend", rank: 47, baseFps: 130, vram: "11GB GDDR5X" },
  { id: "rtx3070m", name: "NVIDIA GeForce RTX 3070 Laptop (8GB)", brand: "NVIDIA", tier: "🎮 A Gaming Laptop", rank: 48, baseFps: 128, vram: "8GB GDDR6" },
  { id: "rx7600", name: "AMD Radeon RX 7600 (8GB)", brand: "AMD", tier: "🎮 A Modern 1080p AMD", rank: 49, baseFps: 125, vram: "8GB GDDR6" },
  { id: "rx6650xt", name: "AMD Radeon RX 6650 XT (8GB)", brand: "AMD", tier: "🎮 A Value 1080p Sweetspot", rank: 50, baseFps: 125, vram: "8GB GDDR6" },
  { id: "rx6600xt", name: "AMD Radeon RX 6600 XT (8GB)", brand: "AMD", tier: "🎮 A Mainstream 1080p", rank: 51, baseFps: 122, vram: "8GB GDDR6" },
  { id: "rtx2060s", name: "NVIDIA GeForce RTX 2060 Super (8GB)", brand: "NVIDIA", tier: "🎮 A Mainstream 1080p", rank: 52, baseFps: 120, vram: "8GB GDDR6" },
  { id: "arc_a750", name: "Intel Arc A750 (8GB)", brand: "Intel", tier: "🎮 A Value Dedicated", rank: 53, baseFps: 120, vram: "8GB GDDR6" },

  // --- TIER 4: SOLID 1080p & MID-RANGE (Score 100 - 119) ---
  { id: "rtx3060", name: "NVIDIA GeForce RTX 3060 (12GB)", brand: "NVIDIA", tier: "📦 B Popular 1080p Choice", rank: 54, baseFps: 115, vram: "12GB GDDR6" },
  { id: "rx5700xt", name: "AMD Radeon RX 5700 XT (8GB)", brand: "AMD", tier: "📦 B Classic RDNA 1440p", rank: 55, baseFps: 115, vram: "8GB GDDR6" },
  { id: "rtx4060m", name: "NVIDIA GeForce RTX 4060 Laptop (8GB)", brand: "NVIDIA", tier: "📦 B Mainstream Laptop", rank: 56, baseFps: 115, vram: "8GB GDDR6" },
  { id: "rx6600", name: "AMD Radeon RX 6600 (8GB)", brand: "AMD", tier: "📦 B Budget 1080p King", rank: 57, baseFps: 110, vram: "8GB GDDR6" },
  { id: "gtx1080", name: "NVIDIA GeForce GTX 1080 (8GB)", brand: "NVIDIA", tier: "📦 B Pascal High-End", rank: 58, baseFps: 110, vram: "8GB GDDR5X" },
  { id: "rtx4050m", name: "NVIDIA GeForce RTX 4050 Laptop (6GB)", brand: "NVIDIA", tier: "📦 B Modern Entry Laptop", rank: 59, baseFps: 108, vram: "6GB GDDR6" },
  { id: "rtx2060", name: "NVIDIA GeForce RTX 2060 (6GB / 12GB)", brand: "NVIDIA", tier: "📦 B Raytracing Starter", rank: 60, baseFps: 105, vram: "6GB GDDR6" },
  { id: "rtx3060m", name: "NVIDIA GeForce RTX 3060 Laptop (6GB)", brand: "NVIDIA", tier: "📦 B Popular Laptop GPU", rank: 61, baseFps: 102, vram: "6GB GDDR6" },
  { id: "arc_a580", name: "Intel Arc A580 (8GB)", brand: "Intel", tier: "📦 B Budget 1080p", rank: 62, baseFps: 100, vram: "8GB GDDR6" },

  // --- TIER 5: ENTRY DEDICATED & BUDGET ESPORTS (Score 70 - 99) ---
  { id: "gtx1070ti", name: "NVIDIA GeForce GTX 1070 Ti (8GB)", brand: "NVIDIA", tier: "📦 B Pascal Classic", rank: 63, baseFps: 98, vram: "8GB GDDR5" },
  { id: "gtx1660s", name: "NVIDIA GeForce GTX 1660 Super (6GB)", brand: "NVIDIA", tier: "📦 B Budget 1080p Legend", rank: 64, baseFps: 95, vram: "6GB GDDR6" },
  { id: "gtx1660ti", name: "NVIDIA GeForce GTX 1660 Ti (6GB)", brand: "NVIDIA", tier: "📦 B Budget 1080p", rank: 65, baseFps: 95, vram: "6GB GDDR6" },
  { id: "gtx1070", name: "NVIDIA GeForce GTX 1070 (8GB)", brand: "NVIDIA", tier: "📦 B Pascal Classic", rank: 66, baseFps: 92, vram: "8GB GDDR5" },
  { id: "rtx3050", name: "NVIDIA GeForce RTX 3050 (8GB)", brand: "NVIDIA", tier: "📦 B Budget RTX", rank: 67, baseFps: 90, vram: "8GB GDDR6" },
  { id: "m2_m1", name: "Apple M2 / M1 Silicon (8-10 Cores)", brand: "Apple", tier: "📦 B Apple Efficient", rank: 68, baseFps: 88, vram: "16GB Unified" },
  { id: "gtx1660", name: "NVIDIA GeForce GTX 1660 (6GB)", brand: "NVIDIA", tier: "📦 B Budget Turing", rank: 69, baseFps: 85, vram: "6GB GDDR5" },
  { id: "rtx3050m", name: "NVIDIA GeForce RTX 3050 Laptop (4GB / 6GB)", brand: "NVIDIA", tier: "📦 B Entry Laptop GPU", rank: 70, baseFps: 82, vram: "4GB / 6GB" },
  { id: "gtx1060_6g", name: "NVIDIA GeForce GTX 1060 (6GB)", brand: "NVIDIA", tier: "📦 B Most Popular Classic", rank: 71, baseFps: 80, vram: "6GB GDDR5" },
  { id: "rog_ally", name: "ASUS ROG Ally / Legion Go (Z1 Extreme)", brand: "APU", tier: "🔋 C Handheld Gaming APU", rank: 72, baseFps: 80, vram: "Shared LPDDR5" },
  { id: "steam_deck_oled", name: "Valve Steam Deck OLED (6nm Sephiroth APU)", brand: "APU", tier: "🔋 C Handheld APU", rank: 73, baseFps: 79, vram: "Shared LPDDR5" },
  { id: "gtx1650s", name: "NVIDIA GeForce GTX 1650 Super (4GB)", brand: "NVIDIA", tier: "📦 B Budget 1080p", rank: 74, baseFps: 78, vram: "4GB GDDR6" },
  { id: "rx590", name: "AMD Radeon RX 590 (8GB)", brand: "AMD", tier: "📦 B Polaris Refresh", rank: 75, baseFps: 78, vram: "8GB GDDR5" },
  { id: "rx580", name: "AMD Radeon RX 580 (8GB / 4GB)", brand: "AMD", tier: "📦 B Budget Legend", rank: 76, baseFps: 75, vram: "8GB GDDR5" },
  { id: "gtx980", name: "NVIDIA GeForce GTX 980 / 980 Ti (4-6GB)", brand: "NVIDIA", tier: "📦 B Maxwell Classic", rank: 77, baseFps: 74, vram: "4GB GDDR5" },
  { id: "rx5500xt", name: "AMD Radeon RX 5500 XT (8GB)", brand: "AMD", tier: "📦 B Entry Dedicated", rank: 78, baseFps: 72, vram: "8GB GDDR6" },
  { id: "gtx970", name: "NVIDIA GeForce GTX 970 (4GB)", brand: "NVIDIA", tier: "📦 B Maxwell Legend", rank: 79, baseFps: 70, vram: "4GB GDDR5" },
  { id: "gtx1060_3g", name: "NVIDIA GeForce GTX 1060 (3GB)", brand: "NVIDIA", tier: "📦 B Budget Pascal", rank: 80, baseFps: 68, vram: "3GB GDDR5" },
  { id: "rx570", name: "AMD Radeon RX 570 / 470 (4GB)", brand: "AMD", tier: "📦 B Polaris Classic", rank: 81, baseFps: 66, vram: "4GB GDDR5" },
  { id: "steam_deck", name: "Valve Steam Deck LCD (Aerith APU)", brand: "APU", tier: "🔋 C Handheld APU", rank: 82, baseFps: 65, vram: "Shared LPDDR5" },
  { id: "gtx1650", name: "NVIDIA GeForce GTX 1650 (4GB)", brand: "NVIDIA", tier: "📦 B Budget Dedicated", rank: 83, baseFps: 64, vram: "4GB GDDR5/6" },

  // --- TIER 6: LEGACY & INTEGRATED GRAPHICS (Score < 60) ---
  { id: "gtx1050ti", name: "NVIDIA GeForce GTX 1050 Ti (4GB)", brand: "NVIDIA", tier: "🏛️ D Entry Level Dedicated", rank: 84, baseFps: 60, vram: "4GB GDDR5" },
  { id: "gtx960", name: "NVIDIA GeForce GTX 960 (2GB / 4GB)", brand: "NVIDIA", tier: "🏛️ D Legacy Maxwell", rank: 85, baseFps: 52, vram: "2GB GDDR5" },
  { id: "radeon_780m", name: "AMD Radeon 780M (RDNA3 APU)", brand: "AMD", tier: "🔋 C Top APU Graphics", rank: 86, baseFps: 50, vram: "System RAM" },
  { id: "iris_xe", name: "Intel Iris Xe Graphics (96EU / G7)", brand: "Intel", tier: "🔋 C Modern Integrated", rank: 87, baseFps: 48, vram: "System RAM" },
  { id: "radeon_680m", name: "AMD Radeon 680M (RDNA2 APU)", brand: "AMD", tier: "🔋 C High-End APU", rank: 88, baseFps: 47, vram: "System RAM" },
  { id: "gtx1050", name: "NVIDIA GeForce GTX 1050 (2GB)", brand: "NVIDIA", tier: "🏛️ D Legacy Entry", rank: 89, baseFps: 46, vram: "2GB GDDR5" },
  { id: "gtx750ti", name: "NVIDIA GeForce GTX 750 Ti (2GB)", brand: "NVIDIA", tier: "🏛️ D Legendary Budget", rank: 90, baseFps: 42, vram: "2GB GDDR5" },
  { id: "gtx750", name: "NVIDIA GeForce GTX 750 (1GB / 2GB)", brand: "NVIDIA", tier: "🏛️ D Classic Maxwell", rank: 91, baseFps: 40, vram: "1GB / 2GB" },
  { id: "intel_arc_140v", name: "Intel Arc 140V (Lunar Lake iGPU)", brand: "Intel", tier: "🔋 C Next-Gen Intel iGPU", rank: 92, baseFps: 40, vram: "System RAM" },
  { id: "intel_uhd770", name: "Intel UHD Graphics 770 (12th-14th Gen)", brand: "Intel", tier: "🔋 C Desktop Integrated", rank: 93, baseFps: 38, vram: "System RAM" },
  { id: "vega_8", name: "AMD Radeon Vega 8 (Ryzen 5000/4000 APU)", brand: "AMD", tier: "🔋 C Popular APU", rank: 94, baseFps: 36, vram: "System RAM" },
  { id: "gt1030", name: "NVIDIA GeForce GT 1030 (2GB GDDR5)", brand: "NVIDIA", tier: "🏛️ D Basic Dedicated", rank: 95, baseFps: 35, vram: "2GB GDDR5" },
  { id: "gtx1630", name: "NVIDIA GeForce GTX 1630 (4GB)", brand: "NVIDIA", tier: "🏛️ D Entry Turing", rank: 96, baseFps: 35, vram: "4GB GDDR6" },
  { id: "vega_7", name: "AMD Radeon Vega 7 (Ryzen Mobile APU)", brand: "AMD", tier: "🔋 C Mobile APU", rank: 97, baseFps: 33, vram: "System RAM" },
  { id: "intel_uhd730", name: "Intel UHD Graphics 730 (Core i5/i3)", brand: "Intel", tier: "🔋 C Desktop iGPU", rank: 98, baseFps: 30, vram: "System RAM" },
  { id: "intel_uhd630", name: "Intel UHD Graphics 630 / HD 4600", brand: "Intel", tier: "🔋 C Legacy Integrated", rank: 99, baseFps: 26, vram: "System RAM" },
  { id: "gt730", name: "NVIDIA GeForce GT 730 (2GB)", brand: "NVIDIA", tier: "🏛️ D Vintage Discrete", rank: 100, baseFps: 22, vram: "2GB DDR3/GDDR5" },
  { id: "intel_hd4000", name: "Intel HD Graphics 4000 / 3000", brand: "Intel", tier: "🏛️ D Vintage Integrated", rank: 101, baseFps: 18, vram: "System RAM" }
];


// Master Global CPU Catalog (60+ Processors sorted logically by Gaming IPC & Multiplier)
// Master Global CPU Catalog (65+ Processors sorted logically by Gaming IPC & Multiplier)
const ALL_CPUS: CpuSpec[] = [
  // --- TIER 0: 3D V-CACHE GAMING KINGS & FLAGSHIPS (Multiplier 1.35 - 1.48) ---
  { id: "r7_9800x3d", name: "AMD Ryzen 7 9800X3D (Zen 5 3D V-Cache King)", brand: "AMD", tier: "⚡ S+ Undisputed Gaming King", rank: 1, multiplier: 1.48, cores: "8C / 16T" },
  { id: "r9_9950x3d", name: "AMD Ryzen 9 9950X3D / 9900X3D (16 Cores)", brand: "AMD", tier: "⚡ S+ Ultra Gaming & Heavy Work", rank: 2, multiplier: 1.45, cores: "16C / 32T" },
  { id: "r7_7800x3d", name: "AMD Ryzen 7 7800X3D (Zen 4 3D V-Cache King)", brand: "AMD", tier: "⚡ S+ Legendary Gaming King", rank: 3, multiplier: 1.42, cores: "8C / 16T" },
  { id: "r9_7950x3d", name: "AMD Ryzen 9 7950X3D / 7900X3D", brand: "AMD", tier: "⚡ S+ Ultra Enthusiast", rank: 4, multiplier: 1.40, cores: "16C / 32T" },
  { id: "i9_14900k", name: "Intel Core i9-14900KS / 14900K (6.2 GHz)", brand: "Intel", tier: "⚡ S+ Intel Flagship (24 Cores)", rank: 5, multiplier: 1.36, cores: "24C / 32T" },
  { id: "core_ultra9_285k", name: "Intel Core Ultra 9 285K (Arrow Lake)", brand: "Intel", tier: "⚡ S+ New Architecture Flagship", rank: 6, multiplier: 1.35, cores: "24C / 24T" },
  { id: "r9_9950x", name: "AMD Ryzen 9 9950X (Zen 5 16 Cores)", brand: "AMD", tier: "⚡ S+ Zen 5 Flagship", rank: 7, multiplier: 1.35, cores: "16C / 32T" },
  { id: "i9_13900k", name: "Intel Core i9-13900K / 13900KS (24 Cores)", brand: "Intel", tier: "⚡ S+ Raptor Lake Flagship", rank: 8, multiplier: 1.32, cores: "24C / 32T" },
  { id: "apple_m4_max", name: "Apple M4 Max / M4 Pro (14-16 Cores)", brand: "Apple", tier: "⚡ S+ Apple High Silicon", rank: 9, multiplier: 1.32, cores: "16C / 16T" },

  // --- TIER 1: HIGH-END ENTHUSIAST & X3D (Multiplier 1.22 - 1.30) ---
  { id: "r7_9700x", name: "AMD Ryzen 7 9700X (Zen 5 8 Cores)", brand: "AMD", tier: "💎 S High-End Zen 5", rank: 10, multiplier: 1.30, cores: "8C / 16T" },
  { id: "r9_7950x", name: "AMD Ryzen 9 7950X / 7900X (12-16 Cores)", brand: "AMD", tier: "💎 S High-End AM5", rank: 11, multiplier: 1.30, cores: "16C / 32T" },
  { id: "i7_14700k", name: "Intel Core i7-14700K / 14700KF (20 Cores)", brand: "Intel", tier: "💎 S High-End Gaming", rank: 12, multiplier: 1.29, cores: "20C / 28T" },
  { id: "core_ultra7_265k", name: "Intel Core Ultra 7 265K (Arrow Lake)", brand: "Intel", tier: "💎 S High-End Arrow Lake", rank: 13, multiplier: 1.28, cores: "20C / 20T" },
  { id: "r7_5800x3d", name: "AMD Ryzen 7 5800X3D (AM4 3D King)", brand: "AMD", tier: "💎 S AM4 Gaming Champion", rank: 14, multiplier: 1.27, cores: "8C / 16T" },
  { id: "i7_13700k", name: "Intel Core i7-13700K / 13700KF (16 Cores)", brand: "Intel", tier: "💎 S High-End Raptor Lake", rank: 15, multiplier: 1.26, cores: "16C / 24T" },
  { id: "r7_5700x3d", name: "AMD Ryzen 7 5700X3D (AM4 3D Value)", brand: "AMD", tier: "💎 S AM4 Value 3D King", rank: 16, multiplier: 1.25, cores: "8C / 16T" },
  { id: "i7_13650hx", name: "Intel Core i7-13650HX (14 Cores / 20 Threads)", brand: "Intel", tier: "💎 S High-End Gaming Laptop", rank: 17, multiplier: 1.25, cores: "14C / 20T" },
  { id: "i9_14900hx", name: "Intel Core i9-14900HX (24 Cores Laptop)", brand: "Intel", tier: "💎 S Laptop Flagship CPU", rank: 18, multiplier: 1.26, cores: "24C / 32T" },
  { id: "r5_9600x", name: "AMD Ryzen 5 9600X (Zen 5 6 Cores)", brand: "AMD", tier: "💎 S Modern High IPC", rank: 19, multiplier: 1.25, cores: "6C / 12T" },
  { id: "r7_7700x", name: "AMD Ryzen 7 7700X / 7700 (8 Cores AM5)", brand: "AMD", tier: "💎 S High-End AM5", rank: 20, multiplier: 1.24, cores: "8C / 16T" },
  { id: "i9_12900k", name: "Intel Core i9-12900K / 12900KS (16 Cores)", brand: "Intel", tier: "💎 S Alder Lake Flagship", rank: 21, multiplier: 1.23, cores: "16C / 24T" },
  { id: "i5_14600k", name: "Intel Core i5-14600K / 14600KF (14 Cores)", brand: "Intel", tier: "💎 S Gaming Sweetspot", rank: 22, multiplier: 1.22, cores: "14C / 20T" },
  { id: "core_ultra5_245k", name: "Intel Core Ultra 5 245K (Arrow Lake)", brand: "Intel", tier: "💎 S Gaming Sweetspot", rank: 23, multiplier: 1.21, cores: "14C / 14T" },

  // --- TIER 2: GAMING SWEETSPOT & MID-RANGE (Multiplier 1.12 - 1.20) ---
  { id: "i5_13600k", name: "Intel Core i5-13600K / 13600KF (14 Cores)", brand: "Intel", tier: "🔥 A+ Gaming Sweetspot", rank: 24, multiplier: 1.20, cores: "14C / 20T" },
  { id: "i7_12700k", name: "Intel Core i7-12700K / 12700F (12 Cores)", brand: "Intel", tier: "🔥 A+ High-End Alder Lake", rank: 25, multiplier: 1.18, cores: "12C / 20T" },
  { id: "r5_7600x", name: "AMD Ryzen 5 7600X / 7600 (6 Cores AM5)", brand: "AMD", tier: "🔥 A+ AM5 Value Gaming", rank: 26, multiplier: 1.18, cores: "6C / 12T" },
  { id: "r5_7500f", name: "AMD Ryzen 5 7500F (6 Cores AM5)", brand: "AMD", tier: "🔥 A+ Budget AM5 King", rank: 27, multiplier: 1.17, cores: "6C / 12T" },
  { id: "apple_m3", name: "Apple M3 / M3 Pro CPU", brand: "Apple", tier: "🔥 A+ Apple Silicon Performance", rank: 28, multiplier: 1.18, cores: "8-12 Cores" },
  { id: "r7_8845hs", name: "AMD Ryzen 7 8845HS / 7840HS (8 Cores)", brand: "AMD", tier: "🔥 A+ High Performance Laptop", rank: 29, multiplier: 1.17, cores: "8C / 16T" },
  { id: "i9_10900k", name: "Intel Core i9-10900K / 11900K (8-10 Cores)", brand: "Intel", tier: "🔥 A+ High Clocked 5.3GHz", rank: 30, multiplier: 1.15, cores: "10C / 20T" },
  { id: "r9_5950x", name: "AMD Ryzen 9 5950X / 5900X (12-16 Cores)", brand: "AMD", tier: "🔥 A+ AM4 Workhorse", rank: 31, multiplier: 1.15, cores: "16C / 32T" },
  { id: "i5_14400f", name: "Intel Core i5-14400F / 14400 (10 Cores)", brand: "Intel", tier: "🔥 A+ Modern 10-Core Value", rank: 32, multiplier: 1.12, cores: "10C / 16T" },
  { id: "r7_5800x", name: "AMD Ryzen 7 5800X / 5700X (8 Cores)", brand: "AMD", tier: "🔥 A+ Popular AM4 8-Core", rank: 33, multiplier: 1.12, cores: "8C / 16T" },

  // --- TIER 3: MAINSTREAM 6-CORE POPULAR PICKS (Multiplier 1.00 - 1.10) ---
  { id: "i5_13400f", name: "Intel Core i5-13400F / 13500 (10-14 Cores)", brand: "Intel", tier: "🎮 A Mainstream Value", rank: 34, multiplier: 1.10, cores: "10C / 16T" },
  { id: "i7_10700k", name: "Intel Core i7-10700K / 9900K / 8700K", brand: "Intel", tier: "🎮 A Classic 8-Core", rank: 35, multiplier: 1.10, cores: "8C / 16T" },
  { id: "i5_12400f", name: "Intel Core i5-12400F / 12400 (6 Cores)", brand: "Intel", tier: "🎮 A 1080p Value King", rank: 36, multiplier: 1.06, cores: "6C / 12T" },
  { id: "r5_5600x", name: "AMD Ryzen 5 5600X / 5600 (6 Cores AM4)", brand: "AMD", tier: "🎮 A Most Popular Budget AM4", rank: 37, multiplier: 1.05, cores: "6C / 12T" },
  { id: "apple_m2_m1", name: "Apple M2 / M1 Series CPU", brand: "Apple", tier: "🎮 A Efficient ARM", rank: 38, multiplier: 1.05, cores: "8 Cores" },
  { id: "r5_5500", name: "AMD Ryzen 5 5500 / 3600XT (6 Cores)", brand: "AMD", tier: "🎮 A Budget 6-Core", rank: 39, multiplier: 1.00, cores: "6C / 12T" },
  { id: "i5_10600k", name: "Intel Core i5-10600K / 11600K (6 Cores)", brand: "Intel", tier: "🎮 A High-Clock 6-Core", rank: 40, multiplier: 1.00, cores: "6C / 12T" },

  // --- TIER 4: BUDGET & ENTRY LEVEL (Multiplier 0.85 - 0.98) ---
  { id: "i5_11400f", name: "Intel Core i5-11400F / 10400F (6 Cores)", brand: "Intel", tier: "📦 B Budget 6-Core", rank: 41, multiplier: 0.98, cores: "6C / 12T" },
  { id: "i3_12100f", name: "Intel Core i3-12100F / 13100 / 14100", brand: "Intel", tier: "📦 B Budget Quad-Core King", rank: 42, multiplier: 0.95, cores: "4C / 8T" },
  { id: "r5_3600", name: "AMD Ryzen 5 3600 / 2600X (6 Cores)", brand: "AMD", tier: "📦 B AM4 Veteran", rank: 43, multiplier: 0.92, cores: "6C / 12T" },
  { id: "i7_9700k", name: "Intel Core i7-9700K / 8700 (6-8 Cores)", brand: "Intel", tier: "📦 B Coffee Lake", rank: 44, multiplier: 0.92, cores: "8C / 8T" },
  { id: "i5_9400f", name: "Intel Core i5-9400F / 8400 (6 Cores)", brand: "Intel", tier: "📦 B Budget 6-Core", rank: 45, multiplier: 0.88, cores: "6C / 6T" },
  { id: "i7_4790k", name: "Intel Core i7-4790K / 4770K (Haswell)", brand: "Intel", tier: "📦 B Legendary Quad-Core", rank: 46, multiplier: 0.85, cores: "4C / 8T" },
  { id: "r5_2600", name: "AMD Ryzen 5 2600 / 1600AF (6 Cores)", brand: "AMD", tier: "📦 B Budget 6-Core", rank: 47, multiplier: 0.84, cores: "6C / 12T" },
  { id: "xeon_e5_2678", name: "Intel Xeon E5-2678v3 / E5-2680v4 (12-14 Cores)", brand: "Intel", tier: "📦 B Budget Server/Xeon", rank: 48, multiplier: 0.82, cores: "12C / 24T" },

  // --- TIER 5: LEGACY & VINTAGE QUAD/DUAL CORES (Multiplier < 0.80) ---
  { id: "r3_3100", name: "AMD Ryzen 3 3100 / 3200G / 2200G", brand: "AMD", tier: "🏛️ D Entry Quad-Core", rank: 49, multiplier: 0.78, cores: "4C / 4T" },
  { id: "i7_3770k", name: "Intel Core i7-3770K / 2600K (Sandy/Ivy)", brand: "Intel", tier: "🏛️ D Classic Quad-Core", rank: 50, multiplier: 0.75, cores: "4C / 8T" },
  { id: "i5_4690k", name: "Intel Core i5-4690K / 3570K / 2500K", brand: "Intel", tier: "🏛️ D Legacy i5 Quad", rank: 51, multiplier: 0.72, cores: "4C / 4T" },
  { id: "i3_10100f", name: "Intel Core i3-10100F / 9100F (4 Cores)", brand: "Intel", tier: "🏛️ D Entry 4-Core", rank: 52, multiplier: 0.72, cores: "4C / 8T" },
  { id: "r3_1200", name: "AMD Ryzen 3 1200 / Athlon 3000G (4 Cores)", brand: "AMD", tier: "🏛️ D Budget Entry", rank: 53, multiplier: 0.68, cores: "4C / 4T" },
  { id: "i7_920", name: "Intel Core i7-920 / Nehalem Classic", brand: "Intel", tier: "🏛️ D Vintage Quad-Core", rank: 54, multiplier: 0.62, cores: "4C / 8T" },
  { id: "i3_legacy", name: "Intel Core i3 / Pentium / Celeron Legacy", brand: "Intel", tier: "🏛️ D Vintage Dual-Core", rank: 55, multiplier: 0.55, cores: "2C / 4T" }
];


export default function BenchmarksPage() {
  const { lang } = useEcosystem();

  // Selected Hardware State (Default: RTX 4050 Laptop + i7-13650HX matching user rig)
  const [selectedGpu, setSelectedGpu] = useState<GpuSpec>(ALL_GPUS[56]); 
  const [selectedCpu, setSelectedCpu] = useState<CpuSpec>(ALL_CPUS[15]); 

  const selectedGpuCardRef = useRef<HTMLDivElement>(null);
  const selectedCpuCardRef = useRef<HTMLDivElement>(null);

  // Automatic Hardware Detection & Smooth Auto-Scroll on Page Mount
  useEffect(() => {
    if (typeof window === "undefined") return;

    // 1. Detect GPU via WebGL Debug Renderer Info
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
      if (gl) {
        const debugInfo = (gl as WebGLRenderingContext).getExtension("WEBGL_debug_renderer_info");
        if (debugInfo) {
          const renderer = ((gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || "").toLowerCase();
          
          // Accurate model number regex extraction (e.g. 4050, 4060, 3060, 1660, M3, Iris, Radeon 780M)
          const modelMatches = renderer.match(/\b(5090|5080|5070|4090|4080|4070|4060|4050|3090|3080|3070|3060|3050|2080|2070|2060|1660|1650|1080|1070|1060|1050|7900|7800|7700|7600|6950|6800|6700|6600|5700|580|570|m4|m3|m2|m1|b580|a770|a750|iris|uhd|vega)\b/i);
          
          if (modelMatches && modelMatches[0]) {
            const detectedModel = modelMatches[0].toLowerCase();
            const isLaptop = renderer.includes("laptop") || renderer.includes("mobile") || renderer.includes("max-q");
            
            const exactGpu = ALL_GPUS.find(g => {
              const gName = g.name.toLowerCase();
              const hasModel = gName.includes(detectedModel);
              if (isLaptop) {
                return hasModel && (gName.includes("laptop") || g.id.endsWith("m") || !ALL_GPUS.some(x => x.name.toLowerCase().includes(detectedModel) && x.name.toLowerCase().includes("laptop")));
              }
              return hasModel;
            });
            
            if (exactGpu) {
              setSelectedGpu(exactGpu);
            }
          } else {
            // Default realistic mainstream GPU
            const fallbackGpu = ALL_GPUS.find(g => g.id === "rtx4060" || g.id === "rtx3060") || ALL_GPUS[43];
            setSelectedGpu(fallbackGpu);
          }
        }
      }
    } catch (e) {
      console.warn("GPU auto-detection note:", e);
    }

    // 2. Detect CPU threads & match optimal tier
    try {
      const threads = navigator.hardwareConcurrency || 16;
      if (threads >= 24) {
        const cpuMatch = ALL_CPUS.find(c => c.id === "i9_14900k") || ALL_CPUS[4];
        setSelectedCpu(cpuMatch);
      } else if (threads >= 16) {
        const cpuMatch = ALL_CPUS.find(c => c.id === "i7_13700k" || c.id === "r7_7700x") || ALL_CPUS[10];
        setSelectedCpu(cpuMatch);
      } else if (threads >= 12) {
        const cpuMatch = ALL_CPUS.find(c => c.id === "i5_13400" || c.id === "i5_12400f") || ALL_CPUS[20];
        setSelectedCpu(cpuMatch);
      } else {
        const cpuMatch = ALL_CPUS.find(c => c.id === "i5_12400f" || c.id === "r5_5600x") || ALL_CPUS[25];
        setSelectedCpu(cpuMatch);
      }
    } catch {}

    // 3. Smooth Auto-Scroll to detected items
    const timer = setTimeout(() => {
      selectedGpuCardRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      selectedCpuCardRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 450);

    return () => clearTimeout(timer);
  }, []);

  // Search & Filter State
  const [gpuSearch, setGpuSearch] = useState("");
  const [gpuBrandFilter, setGpuBrandFilter] = useState<string>("All");
  const [cpuSearch, setCpuSearch] = useState("");
  const [cpuBrandFilter, setCpuBrandFilter] = useState<string>("All");

  // Rig Configuration Tweaks
  const [targetRes, setTargetRes] = useState<string>("1080p");
  const [ramAllocated, setRamAllocated] = useState<number>(6); // GB
  const [selectedProfile, setSelectedProfile] = useState<string>("all");

  const isAr = lang === "ar";

  // Filtered GPU list (Always logically sorted by performance rank)
  const filteredGpus = useMemo(() => {
    return ALL_GPUS.filter(g => {
      const matchBrand = gpuBrandFilter === "All" || g.brand === gpuBrandFilter;
      const matchQuery = !gpuSearch || g.name.toLowerCase().includes(gpuSearch.toLowerCase()) || g.tier.toLowerCase().includes(gpuSearch.toLowerCase()) || g.vram.toLowerCase().includes(gpuSearch.toLowerCase());
      return matchBrand && matchQuery;
    }).sort((a, b) => a.rank - b.rank);
  }, [gpuSearch, gpuBrandFilter]);

  // Filtered CPU list (Always logically sorted by performance rank)
  const filteredCpus = useMemo(() => {
    return ALL_CPUS.filter(c => {
      const matchBrand = cpuBrandFilter === "All" || c.brand === cpuBrandFilter;
      const matchQuery = !cpuSearch || c.name.toLowerCase().includes(cpuSearch.toLowerCase()) || c.tier.toLowerCase().includes(cpuSearch.toLowerCase()) || c.cores.toLowerCase().includes(cpuSearch.toLowerCase());
      return matchBrand && matchQuery;
    }).sort((a, b) => a.rank - b.rank);
  }, [cpuSearch, cpuBrandFilter]);

  // Calibrated Realistic Physics FPS Calculations
  const calcResults = useMemo(() => {
    const gpuBase = selectedGpu.baseFps;
    const cpuMult = selectedCpu.multiplier;
    
    // Exact Resolution Multipliers
    const resMult = 
      targetRes === "720p" ? 1.38 :
      targetRes === "1080p" ? 1.0 :
      targetRes === "1440p" ? 0.74 :
      targetRes === "1600p" ? 0.67 :
      targetRes === "1800p" ? 0.56 :
      targetRes === "4k" ? 0.42 :
      targetRes === "5k" ? 0.30 : 0.16;

    // Exact RAM Multipliers
    const ramMult =
      ramAllocated <= 2 ? 0.75 :
      ramAllocated === 4 ? 0.92 :
      ramAllocated === 6 ? 1.02 :
      ramAllocated === 8 ? 1.05 :
      ramAllocated >= 16 ? 1.08 : 1.0;

    // 1. Extreme Shaders (Raytracing, 3D POM, Volumetric Godrays)
    const extremeAvg = Math.max(18, Math.round(gpuBase * 0.92 * (cpuMult * 0.35 + 0.65) * resMult * ramMult));
    const extreme1PctLow = Math.max(12, Math.round(extremeAvg * 0.76));
    const extremeFrameTime = (1000 / extremeAvg).toFixed(1);

    // 2. Balanced Shaders (144+ FPS High-Refresh)
    const balancedAvg = Math.max(35, Math.round(gpuBase * 1.55 * (cpuMult * 0.50 + 0.50) * Math.sqrt(resMult) * ramMult));
    const balanced1PctLow = Math.max(24, Math.round(balancedAvg * 0.80));
    const balancedFrameTime = (1000 / balancedAvg).toFixed(1);

    // 3. Competitive Modern 26.2 (Pure Sodium + Culling)
    const compAvg = Math.max(75, Math.round(gpuBase * 1.15 * Math.pow(cpuMult, 1.35) * 2.80 * ramMult));
    const comp1PctLow = Math.max(50, Math.round(compAvg * 0.78));
    const compFrameTime = (1000 / compAvg).toFixed(1);

    // 4. Legacy 1.8.9 PvP Engine (Forge + OptiFine + HitDelayFix)
    const legacyAvg = Math.max(140, Math.round(gpuBase * 0.95 * Math.pow(cpuMult, 1.50) * 4.90 * ramMult));
    const legacy1PctLow = Math.max(90, Math.round(legacyAvg * 0.82));
    const legacyFrameTime = (1000 / legacyAvg).toFixed(1);

    // 5. Vanilla 1.21.4 (Unmodded Standard Java)
    const vanilla121Avg = Math.max(25, Math.round(gpuBase * 0.42 * (cpuMult * 0.70 + 0.30) * resMult * ramMult * 1.2));
    const vanilla121Low = Math.max(15, Math.round(vanilla121Avg * 0.60));
    const vanilla121FrameTime = (1000 / vanilla121Avg).toFixed(1);

    // 6. Vanilla 1.8.9 (Unmodded Standard)
    const vanilla18Avg = Math.max(45, Math.round(gpuBase * 0.50 * Math.pow(cpuMult, 1.10) * 1.8 * ramMult));
    const vanilla18Low = Math.max(25, Math.round(vanilla18Avg * 0.65));
    const vanilla18FrameTime = (1000 / vanilla18Avg).toFixed(1);

    return {
      extremeAvg,
      extreme1PctLow,
      extremeFrameTime,
      balancedAvg,
      balanced1PctLow,
      balancedFrameTime,
      compAvg,
      comp1PctLow,
      compFrameTime,
      legacyAvg,
      legacy1PctLow,
      legacyFrameTime,
      vanilla121Avg,
      vanilla121Low,
      vanilla121FrameTime,
      vanilla18Avg,
      vanilla18Low,
      vanilla18FrameTime,
    };
  }, [selectedGpu, selectedCpu, targetRes, ramAllocated]);

  const getRecommendedProfile = () => {
    if (calcResults.extremeAvg >= 120) return isAr ? "حزمة Modern 26.2 Ultra Extreme (أعلى جودة)" : "Modern 26.2 Ultra Extreme Master (4K Raytracing)";
    if (calcResults.balancedAvg >= 120) return isAr ? "حزمة Modern 26.2 Balanced 144+ FPS (الأداء المتوازن)" : "Modern 26.2 Balanced 144+ FPS SIR Shader (High Refresh)";
    if (calcResults.compAvg >= 180) return isAr ? "حزمة Modern 26.2 Competitive Speed (أعلى سلاسة)" : "Modern 26.2 Competitive Speed (Pure Sodium)";
    return isAr ? "حزمة Legacy 1.8.9 PvP Battle Suite (أداء خفيف فائق)" : "Legacy 1.8.9 PvP Battle Suite (1000+ FPS Hypixel)";
  };

  return (
    <AuthGate featureName="Hardware & FPS Benchmarks" featureNameAr="اختبارات الأداء وقياس الإطارات">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-6xl mx-auto px-6 space-y-8">

        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Activity className="w-3.5 h-3.5" />
            <span>{isAr ? "محرك الذكاء الحسابي ودليل المواصفات الشامل (150+ قطعة)" : "Global Hardware FPS Intelligence Engine (150+ Rig Specs)"}</span>
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "حاسبة توقع الإطارات ومواصفات العتاد الشاملة" : "Global Rig Benchmark & Predicted FPS Engine"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr
              ? "ابحث عن أي بطاقة رسومات أو معالج مركزي في العالم لمعاينة الإطارات المتوقعة (FPS) وزمن التأخير (Frame Time) بدقة عبر كافة مستويات الشيدرز والـ PvP."
              : "Search across 150+ global GPUs and CPUs sorted by real-world performance tiers to calculate calibrated framerates, 1% lows, and frame time latency."}
          </p>
        </div>

        {/* Tweak Bar: Resolution, RAM & Game Profile Selector (CyberSelect Animated Lists) */}
        <div className="p-5 rounded-3xl bg-white dark:bg-[#101624]/95 border border-slate-200 dark:border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-6 shadow-lg relative z-30">
          <div className="flex-1 min-w-[220px]">
            <CyberSelect
              label={isAr ? "بروفايل اللعبة المستهدف (Profile):" : "Target Game / Modpack Profile:"}
              icon={<Sparkles className="w-4 h-4 text-amber-400" />}
              accentColor="amber"
              value={selectedProfile}
              onChange={(val) => setSelectedProfile(val as string)}
              options={[
                { value: "all", label: "All Profiles (Side-by-Side Comparison)", badge: "Overview" },
                { value: "extreme", label: "Modern 26.2 (SIR Extreme Raytracing)", badge: "Max 4K" },
                { value: "balanced", label: "Modern 26.2 (SIR Balanced 144+ FPS)", badge: "144Hz" },
                { value: "comp", label: "Modern 26.2 (Competitive Pure Sodium)", badge: "Speed" },
                { value: "legacy", label: "Legacy 1.8.9 (Hypixel PvP Master)", badge: "1000+ FPS" },
                { value: "vanilla_modern", label: "Vanilla Minecraft 1.21.4 (Unmodded)", badge: "Standard" },
                { value: "vanilla_legacy", label: "Vanilla Minecraft 1.8.9 (Unmodded)", badge: "Classic" },
              ]}
            />
          </div>

          <div className="flex-1 min-w-[220px]">
            <CyberSelect
              label={isAr ? "دقة العرض المستهدفة (Resolution):" : "Target Display Resolution:"}
              icon={<Monitor className="w-4 h-4 text-cyan-400" />}
              accentColor="cyan"
              value={targetRes}
              onChange={(val) => setTargetRes(val as string)}
              options={[
                { value: "720p", label: "720p HD (1280x720)", badge: "Fast 1.38x" },
                { value: "1080p", label: "1080p Full HD (1920x1080)", badge: "1.0x Baseline" },
                { value: "1440p", label: "1440p 2K QHD (2560x1440)", badge: "2K Retina" },
                { value: "1600p", label: "1600p WQXGA (2560x1600)", badge: "Mac 16:10" },
                { value: "1800p", label: "1800p 3K (2880x1800)", badge: "3K Ultra" },
                { value: "4k", label: "2160p 4K UHD (3840x2160)", badge: "4K Extreme" },
                { value: "5k", label: "2880p 5K Studio (5120x2880)", badge: "5K Master" },
                { value: "8k", label: "4320p 8K Cinematic (7680x4320)", badge: "8K Enthusiast" },
              ]}
            />
          </div>

          <div className="flex-1 min-w-[220px]">
            <CyberSelect
              label={isAr ? "ذاكرة الرام المخصصة للعبة (Allocated RAM):" : "Allocated Client Memory (RAM):"}
              icon={<HardDrive className="w-4 h-4 text-emerald-400" />}
              accentColor="emerald"
              value={ramAllocated}
              onChange={(val) => setRamAllocated(Number(val))}
              options={[
                { value: 2, label: "2 GB RAM (Minimal / Low Heap)", badge: "Bottleneck" },
                { value: 4, label: "4 GB RAM (Vanilla / Balanced)", badge: "Standard" },
                { value: 6, label: "6 GB RAM (Golden Sweetspot)", badge: "Recommended" },
                { value: 8, label: "8 GB RAM (Extreme Shaders & POM)", badge: "Optimal" },
                { value: 12, label: "12 GB RAM (Distant Horizons LOD)", badge: "High Heap" },
                { value: 16, label: "16 GB RAM (Massive Render Distance)", badge: "Heavy" },
                { value: 24, label: "24 GB RAM (Pro Studio / Ultra Rig)", badge: "Enthusiast" },
                { value: 32, label: "32 GB RAM (Server Hosting & Client)", badge: "Extreme" },
                { value: 64, label: "64 GB RAM (Maximum Memory Rig)", badge: "Master" },
              ]}
            />
          </div>
        </div>

        {/* Dual Hardware Selector Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* GPU Selector Panel */}
          <div className="p-6 rounded-3xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
                <Gauge className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
                <span>{isAr ? "اختر بطاقة الرسومات (GPU):" : "Select Graphics Card (GPU):"}</span>
              </label>
              <span className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 font-bold px-2 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-950 border border-cyan-300 dark:border-cyan-800/40">
                {filteredGpus.length} Models (Sorted by Tier)
              </span>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none z-10" />
              <input
                type="text"
                placeholder={isAr ? "ابحث عن أي كارت (مثل RTX 4070, RX 7800, GTX 1660, Apple M3)..." : "Search GPU (e.g. RTX 4070, RX 7800 XT, GTX 1660, Apple M3)..."}
                value={gpuSearch}
                onChange={e => setGpuSearch(e.target.value)}
                className="w-full bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800 rounded-2xl pl-10 pr-4 py-2.5 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium transition-colors"
              />
            </div>

            {/* Brand Filter Tabs */}
            <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
              {["All", "NVIDIA", "AMD", "Intel", "Apple", "APU"].map(b => (
                <button
                  key={b}
                  onClick={() => setGpuBrandFilter(b)}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    gpuBrandFilter === b
                      ? "bg-cyan-500 text-slate-950 shadow-md"
                      : "bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800"
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>

            {/* Scrollable GPU List */}
            <div className="max-h-[340px] overflow-y-auto p-1 pr-3 space-y-2.5 custom-scrollbar">
              {filteredGpus.map(gpu => {
                const isSelected = selectedGpu.id === gpu.id;
                return (
                  <div
                    key={gpu.id}
                    ref={isSelected ? selectedGpuCardRef : null}
                    onClick={() => setSelectedGpu(gpu)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between group overflow-hidden ${
                      isSelected
                        ? "bg-cyan-500/15 border-cyan-500 text-slate-900 dark:text-white shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/30"
                        : "bg-slate-50 dark:bg-[#080c14] border-slate-200 dark:border-slate-800/80 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-white dark:hover:bg-slate-900/60"
                    }`}
                  >
                    <div className="min-w-0 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-slate-500 font-bold">#{gpu.rank}</span>
                        <h4 className="font-bold text-xs truncate group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors">
                          {gpu.name}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-slate-500 dark:text-slate-400">{gpu.tier}</span>
                        <span className="text-[9px] font-mono text-cyan-600 dark:text-cyan-400/80 bg-cyan-100 dark:bg-cyan-950/60 px-1.5 py-0.2 rounded border border-cyan-300 dark:border-cyan-900/40">
                          {gpu.vram}
                        </span>
                      </div>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-cyan-500 shrink-0 animate-in zoom-in-50 duration-150" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* CPU Selector Panel */}
          <div className="p-6 rounded-3xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                <span>{isAr ? "اختر المعالج المركزي (CPU):" : "Select Processor (CPU):"}</span>
              </label>
              <span className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 border border-emerald-300 dark:border-emerald-800/40">
                {filteredCpus.length} Models (Sorted by Rank)
              </span>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none z-10" />
              <input
                type="text"
                placeholder={isAr ? "ابحث عن أي معالج (مثل 7800X3D, i7-13700K, 12400F, Apple M4)..." : "Search CPU (e.g. 7800X3D, i7-13700K, 12400F, Apple M4)..."}
                value={cpuSearch}
                onChange={e => setCpuSearch(e.target.value)}
                className="w-full bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800 rounded-2xl pl-10 pr-4 py-2.5 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-medium transition-colors"
              />
            </div>

            {/* Brand Filter Tabs */}
            <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
              {["All", "Intel", "AMD", "Apple"].map(b => (
                <button
                  key={b}
                  onClick={() => setCpuBrandFilter(b)}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    cpuBrandFilter === b
                      ? "bg-emerald-500 text-slate-950 shadow-md"
                      : "bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800"
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>

            {/* Scrollable CPU List */}
            <div className="max-h-[340px] overflow-y-auto p-1 pr-3 space-y-2.5 custom-scrollbar">
              {filteredCpus.map(cpu => {
                const isSelected = selectedCpu.id === cpu.id;
                return (
                  <div
                    key={cpu.id}
                    ref={isSelected ? selectedCpuCardRef : null}
                    onClick={() => setSelectedCpu(cpu)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between group overflow-hidden ${
                      isSelected
                        ? "bg-emerald-500/15 border-emerald-500 text-slate-900 dark:text-white shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/30"
                        : "bg-slate-50 dark:bg-[#080c14] border-slate-200 dark:border-slate-800/80 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-white dark:hover:bg-slate-900/60"
                    }`}
                  >
                    <div className="min-w-0 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-slate-500 font-bold">#{cpu.rank}</span>
                        <h4 className="font-bold text-xs truncate group-hover:text-emerald-600 dark:group-hover:text-emerald-300 transition-colors">
                          {cpu.name}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-slate-500 dark:text-slate-400">{cpu.tier}</span>
                        <span className="text-[9px] font-mono text-emerald-600 dark:text-emerald-400/80 bg-emerald-100 dark:bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-300 dark:border-emerald-900/40">
                          {cpu.cores}
                        </span>
                      </div>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 animate-in zoom-in-50 duration-150" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Real-Time Benchmark Calculations Matrix Card */}
        <div className="p-8 rounded-3xl bg-white dark:bg-gradient-to-br dark:from-[#0c101d] dark:via-[#101626] dark:to-[#0a0d18] border border-cyan-400/40 dark:border-cyan-500/30 shadow-2xl shadow-cyan-500/10 space-y-6">
          
          {/* Active Hardware Header Badge */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-500 dark:text-cyan-400">
                <Gauge className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase tracking-widest font-bold">
                  {isAr ? "العتاد المختار حالياً للاختبار" : "Selected Benchmark Hardware Configuration"}
                </span>
                <h3 className="text-base sm:text-lg font-black text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
                  <span className="text-cyan-600 dark:text-cyan-400">{selectedGpu.name}</span>
                  <span className="text-slate-400">•</span>
                  <span className="text-emerald-600 dark:text-emerald-400">{selectedCpu.name}</span>
                </h3>
              </div>
            </div>

            <div className="text-right">
              <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 block">{isAr ? "البروفايل الموصى به" : "Recommended Suite Profile"}</span>
              <span className="text-xs font-black text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/10 border border-amber-400 dark:border-amber-500/30 px-3 py-1 rounded-xl inline-block mt-0.5">
                {getRecommendedProfile()}
              </span>
            </div>
          </div>

          {/* Output Cards Grid (Responsive, filtered by selectedProfile or displaying all 6 side-by-side) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            
            {/* 1. SIR Extreme Shaders */}
            {(selectedProfile === "all" || selectedProfile === "extreme") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-amber-400/40 dark:border-amber-500/30 space-y-3 relative overflow-hidden group hover:border-amber-500 dark:hover:border-amber-400 transition-all shadow-md">
                <div className="flex items-center justify-between text-amber-600 dark:text-amber-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    {isAr ? "شيدرز Extreme 4K" : "SIR Extreme Shaders"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
                    Raytracing
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.extremeAvg} <span className="text-sm font-bold text-amber-500 dark:text-amber-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.extreme1PctLow} FPS</strong></span>
                    <span>{calcResults.extremeFrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "تتبع ضوئي كامل، انكسارات ماء كريستالية، وبروز بلوكات 3D POM." : "Full volumetric lighting, labPBR POM relief, and crystal water caustics."}
                </p>
              </div>
            )}

            {/* 2. SIR Balanced Shaders */}
            {(selectedProfile === "all" || selectedProfile === "balanced") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-cyan-400/40 dark:border-cyan-500/30 space-y-3 relative overflow-hidden group hover:border-cyan-500 dark:hover:border-cyan-400 transition-all shadow-md">
                <div className="flex items-center justify-between text-cyan-600 dark:text-cyan-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5" />
                    {isAr ? "شيدرز Balanced 144+" : "SIR Balanced Shaders"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-800">
                    144+ FPS
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.balancedAvg} <span className="text-sm font-bold text-cyan-500 dark:text-cyan-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.balanced1PctLow} FPS</strong></span>
                    <span>{calcResults.balancedFrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "مظهر خيالي بقرص شمس واقعي مع ثبات تام على شاشات التردد العالي." : "Identical glorious sun disk and transparent water tuned for 144Hz+ monitors."}
                </p>
              </div>
            )}

            {/* 3. Modern 26.2 Competitive */}
            {(selectedProfile === "all" || selectedProfile === "comp") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-emerald-400/40 dark:border-emerald-500/30 space-y-3 relative overflow-hidden group hover:border-emerald-500 dark:hover:border-emerald-400 transition-all shadow-md">
                <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5" />
                    {isAr ? "الحديث 26.2 بدون شيدر" : "Modern 26.2 Pure FPS"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                    Sodium
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.compAvg} <span className="text-sm font-bold text-emerald-500 dark:text-emerald-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.comp1PctLow} FPS</strong></span>
                    <span>{calcResults.compFrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "محرك Sodium و Lithium المحسن لسلاسة وسرعة استجابة مذهلة." : "Pure Sodium & Lithium optimization matrix with instant chunk rendering."}
                </p>
              </div>
            )}

            {/* 4. Legacy 1.8.9 PvP Engine */}
            {(selectedProfile === "all" || selectedProfile === "legacy") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-purple-400/40 dark:border-purple-500/30 space-y-3 relative overflow-hidden group hover:border-purple-500 dark:hover:border-purple-400 transition-all shadow-md">
                <div className="flex items-center justify-between text-purple-600 dark:text-purple-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Swords className="w-3.5 h-3.5" />
                    {isAr ? "الكلاسيكي 1.8.9 PvP" : "Legacy 1.8.9 PvP Engine"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                    Hypixel Ready
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.legacyAvg} <span className="text-sm font-bold text-purple-500 dark:text-purple-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.legacy1PctLow} FPS</strong></span>
                    <span>{calcResults.legacyFrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "استجابة 1000Hz ونظام كليكات فوري وثبات إطارات خيالي للمبارزات." : "1000Hz polling rate raw input and zero hit registration drop in Duels & Bedwars."}
                </p>
              </div>
            )}

            {/* 5. Vanilla Minecraft 1.21.4 (Unmodded) */}
            {(selectedProfile === "all" || selectedProfile === "vanilla_modern") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-slate-300 dark:border-slate-800 space-y-3 relative overflow-hidden group hover:border-slate-400 dark:hover:border-slate-700 transition-all shadow-md">
                <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Monitor className="w-3.5 h-3.5" />
                    {isAr ? "ماينكرافت الأصلية (فانيلا 1.21.4)" : "Vanilla Minecraft 1.21.4"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700">
                    Unmodded
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.vanilla121Avg} <span className="text-sm font-bold text-slate-500 dark:text-slate-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.vanilla121Low} FPS</strong></span>
                    <span>{calcResults.vanilla121FrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "أداء اللعبة الخام بدون أي مودات تسريع أو تحسينات جافا." : "Raw vanilla performance without Sodium memory or thread optimizations."}
                </p>
              </div>
            )}

            {/* 6. Vanilla Minecraft 1.8.9 (Unmodded) */}
            {(selectedProfile === "all" || selectedProfile === "vanilla_legacy") && (
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080c14] border border-slate-300 dark:border-slate-800 space-y-3 relative overflow-hidden group hover:border-slate-400 dark:hover:border-slate-700 transition-all shadow-md">
                <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Monitor className="w-3.5 h-3.5" />
                    {isAr ? "ماينكرافت الأصلية (فانيلا 1.8.9)" : "Vanilla Minecraft 1.8.9"}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700">
                    Unmodded
                  </span>
                </div>
                <div>
                  <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {calcResults.vanilla18Avg} <span className="text-sm font-bold text-slate-500 dark:text-slate-400 font-mono">FPS</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
                    <span>1% Low: <strong className="text-slate-700 dark:text-slate-200">{calcResults.vanilla18Low} FPS</strong></span>
                    <span>{calcResults.vanilla18FrameTime} ms</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {isAr ? "نسخة 1.8.9 القديمة بدون مودات تحسين كليكات أو OptiFine." : "Standard legacy Minecraft without HitDelayFix or memory heap tuners."}
                </p>
              </div>
            )}

          </div>
        </div>

        {/* Global Features Launchpad */}
        <ConnectedFeaturesHub />

      </div>
    </div>
    </AuthGate>);
}