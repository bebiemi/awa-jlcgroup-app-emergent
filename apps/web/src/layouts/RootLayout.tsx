import React from "react";
import { useSidebar } from "@/contexts/SidebarContext";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const { isOpen, isCompact } = useSidebar();

  /**
   * Desktop only:
   * - Sidebar ouverte large = 18rem
   * - Sidebar ouverte compact = 6rem
   * - Sidebar fermée = 0
   */
  const fallbackWidth = isCompact ? 96 : 288 // 6rem / 18rem
  const desktopOffsetPx = isOpen ? fallbackWidth : 0

  return (
    <div
      className="min-h-screen transition-[margin-left] duration-200 ease-[cubic-bezier(0.4,0.0,0.2,1)]"
      style={{ marginLeft: `${desktopOffsetPx}px`, paddingLeft: 'env(safe-area-inset-left)' }}
    >
      {children}
    </div>
  );
}
