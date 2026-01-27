// app/(dashboard)/layout.tsx
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/sidebar"
import { Navbar } from "@/components/layout/navbar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    // 1. Provider must be the ROOT of this layout
    <SidebarProvider> 
      <div className="flex h-screen w-full">
        {/* 2. AppSidebar uses useSidebar() internally -> MUST be inside Provider */}
        <AppSidebar /> 
        
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          {/* 3. Navbar has SidebarTrigger which uses useSidebar() -> MUST be inside Provider */}
          <Navbar /> 
          
          <main className="flex-1 overflow-y-auto bg-background p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}