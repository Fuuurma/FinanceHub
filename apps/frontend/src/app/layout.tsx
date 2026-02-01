// app/layout.tsx
import type { Metadata } from "next";
import { Suspense, lazy } from "react";
import "./globals.css";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { FullPageSkeleton } from "@/components/ui/analytics-skeletons";
import { ShortcutHelpDialog } from "@/components/shortcuts/ShortcutHelpDialog";
import { registerDefaultShortcuts, shortcutRegistry } from "@/lib/shortcuts";
import { useEffect } from "react";

export const metadata: Metadata = {
  title: "FinanceHub - Professional Market Analysis",
  description: "Advanced financial terminal for market analysis and portfolio management",
};

// Lazy load heavy routes for code splitting
const Analytics = lazy(() => import("./(dashboard)/analytics/page"));
const Screener = lazy(() => import("./(dashboard)/screener/page"));
const Settings = lazy(() => import("./(dashboard)/settings/page"));
const ChartsAdvanced = lazy(() => import("./(dashboard)/charts/advanced/page"));
const Sentiment = lazy(() => import("./(dashboard)/sentiment/page"));

// Route configuration for code splitting
const routeConfig: Record<string, { component: React.ComponentType<any>; ssr: boolean }> = {
  analytics: { component: Analytics, ssr: false },
  screener: { component: Screener, ssr: false },
  settings: { component: Settings, ssr: true },
  "charts/advanced": { component: ChartsAdvanced, ssr: false },
  sentiment: { component: Sentiment, ssr: false },
};

// Higher-order component for lazy loading with skeleton
function LazyRoute({ route }: { route: string }) {
  const config = routeConfig[route];
  if (!config) return null;

  const Component = config.component;

  return (
    <Suspense fallback={<FullPageSkeleton />}>
      <Component />
    </Suspense>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased font-sans">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}