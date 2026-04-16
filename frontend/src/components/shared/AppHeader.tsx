"use client";

import Link from "next/link";
import { Heart } from "lucide-react";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-teal-400 shadow-sm">
            <Heart className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-gray-900">
            AutiScreen
          </span>
        </Link>
      </div>
    </header>
  );
}
