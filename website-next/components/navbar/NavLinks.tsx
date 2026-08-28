"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { soundFx } from "@/lib/sound";

export interface NavLinkItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  highlight?: boolean;
}

interface NavLinksProps {
  links: NavLinkItem[];
}

export function NavLinks({ links }: NavLinksProps) {
  const pathname = usePathname();

  return (
    <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
      {links.slice(0, 7).map((link) => {
        const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
        const Icon = link.icon;

        return (
          <Link
            key={link.href}
            href={link.href}
            onClick={() => soundFx.playTab()}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              isActive
                ? "bg-cyan-500/15 text-cyan-600 dark:text-[#00e5ff] border border-cyan-500/30 shadow-sm"
                : link.highlight
                ? "bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 text-cyan-600 dark:text-[#00e5ff] border border-cyan-500/40 hover:brightness-110"
                : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/60"
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
