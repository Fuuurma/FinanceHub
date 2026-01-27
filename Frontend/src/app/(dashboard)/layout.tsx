// app/(dashboard)/layout.tsx
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/sidebar"
import { Navbar } from "@/components/layout/navbar"
import { RightSidebar } from "@/components/layout/right-sidebar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full overflow-hidden">
        {/* Left Sidebar - Navigation */}
        <AppSidebar />
        
        {/* Main Content Area */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto bg-background">
            {children}
          </main>
        </div>

        {/* Right Sidebar - Portfolios/Watchlists */}
        <RightSidebar />
      </div>
    </SidebarProvider>
  )
}