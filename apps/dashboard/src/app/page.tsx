"use client";

import React, { useState } from "react";
import { DashboardApp } from "../../DashboardApp";

export default function Page() {
  const [isDark, setIsDark] = useState(true);

  return (
    <div className={isDark ? "dark bg-[#0B0F19] text-white min-h-screen" : "bg-white text-slate-900 min-h-screen"}>
      <DashboardApp
        isDark={isDark}
        onToggleTheme={() => setIsDark((prev) => !prev)}
      />
    </div>
  );
}

