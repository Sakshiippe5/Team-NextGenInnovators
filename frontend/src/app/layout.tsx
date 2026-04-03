import AppBar from "@/components/app/appbar";
import Providers from "@/components/app/providers";
import type { Metadata, Viewport } from "next";
import { Nunito } from "next/font/google";
import NextTopLoader from "nextjs-toploader";
import "./globals.css";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ShellWithTooltip } from "@/components/app/shell-with-tooltip";
import { syncClerkUserToDb } from "@/actions/sync-user";

const nunito = Nunito({ subsets: ["latin"] });

/** Clerk `currentUser()` + DB sync need request context (not static prerender). */
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  metadataBase: new URL("https://www.airoadmapgenerator.com/"),
  title: "AI Roadmap Generator",
  description: "Generate your roadmaps with AI.",
  openGraph: {
    url: "https://www.airoadmapgenerator.com/",

    images: "/opengraph-image.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  await syncClerkUserToDb();

  return (
    <html lang="en" className="h-full">
      <body className={`${nunito.className} min-h-full antialiased`}>
        <ShellWithTooltip>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
                <div className="flex items-center gap-2 px-4">
                  <SidebarTrigger className="-ml-1" />
                  <Separator
                    orientation="vertical"
                    className="mr-2 data-[orientation=vertical]:h-4"
                  />
                  <Breadcrumb>
                    <BreadcrumbList>
                      <BreadcrumbItem className="hidden md:block">
                        <BreadcrumbLink href="#">
                          Build Your Application
                        </BreadcrumbLink>
                      </BreadcrumbItem>
                      <BreadcrumbSeparator className="hidden md:block" />
                      <BreadcrumbItem>
                        <BreadcrumbPage>Data Fetching</BreadcrumbPage>
                      </BreadcrumbItem>
                    </BreadcrumbList>
                  </Breadcrumb>
                </div>
              </header>
              <Providers>
                <NextTopLoader showSpinner={false} color="black" />
                <AppBar />
                {children}
              </Providers>
            </SidebarInset>
          </SidebarProvider>
        </ShellWithTooltip>
      </body>
    </html>
  );
}
