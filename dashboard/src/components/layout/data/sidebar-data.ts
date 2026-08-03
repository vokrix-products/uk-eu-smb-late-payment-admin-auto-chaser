import { TASKS_NAV_LABEL, TASKS_NAV_ICON, SHOW_TASKS_NAV } from '@/product-config'
import { LayoutDashboard, BookOpen } from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: SidebarData = {
  navGroups: [
    {
      title: 'General',
      items: [
        {
          title: 'Dashboard',
          url: '/',
          icon: LayoutDashboard,
        },
        ...(SHOW_TASKS_NAV
          ? [{ title: TASKS_NAV_LABEL, url: '/tasks', icon: TASKS_NAV_ICON }]
          : []),
        {
          title: 'Help',
          url: '/help',
          icon: BookOpen,
        },
      ],
    },
  ],
}
