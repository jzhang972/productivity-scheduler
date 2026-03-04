"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils/cn"
import { Calendar, BarChart3, ClipboardList, TrendingUp } from "lucide-react"

const links = [
  { href: "/today", label: "Today", icon: Calendar },
  { href: "/weekly", label: "Weekly", icon: BarChart3 },
  { href: "/review", label: "Review", icon: ClipboardList },
  { href: "/analytics", label: "Analytics", icon: TrendingUp },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex h-14 items-center gap-6">
          <Link href="/today" className="font-semibold text-sm">
            Scheduler
          </Link>
          <div className="flex gap-1">
            {links.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                  pathname === href || pathname.startsWith(href + "/")
                    ? "bg-secondary text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
