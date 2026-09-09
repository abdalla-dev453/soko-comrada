import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

import { Navbar } from "./Navbar";
import { MobileDrawer } from "./MobileDrawer";
import { BottomTabBar } from "./BottomTabBar";
import { Footer } from "./Footer";
import { CookieBanner } from "./CookieBanner";
import { ToastViewport } from "../common/Toast";
import { trackPageView } from "../../utils/analytics";

export function RootLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setDrawerOpen(false);
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
    trackPageView(location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink">
      <Navbar onOpenDrawer={() => setDrawerOpen(true)} />
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <main className="flex-1 pb-16 md:pb-0">
        <Outlet />
      </main>

      <Footer />
      <BottomTabBar />
      <CookieBanner />
      <ToastViewport />
    </div>
  );
}