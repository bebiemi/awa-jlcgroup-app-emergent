

import { useSidebarTheme } from '@/contexts/SidebarThemeContext'
import clsx from 'clsx'

export default function SidebarThemeSelector() {
  const { theme, setTheme } = useSidebarTheme()

  const themes = [
    {
      id: 'dark',
      label: 'Dark JLC',
      className:
        'bg-gradient-to-br from-[#913975] to-[#56335d] shadow-[0_0_6px_#56335daa]',
    },
    {
      id: 'magenta',
      label: 'Magenta Glow',
      className:
        'bg-gradient-to-br from-[#743669] to-[#A35AAE] shadow-[0_0_12px_#743669aa]',
    },
    {
      id: 'light',
      label: 'Light',
      className:
        'bg-gradient-to-br from-white to-[#f4f4f9] border border-[#362f50]',
    },
    

  ]

  return (
    <div className="p-4 rounded-xl bg-white/10 border border-white/10 mt-4">
      <h3 className="text-sm font-semibold mb-2">Thème de la Sidebar</h3>
      <p className="text-xs opacity-70 mb-4">Personnalisez l’apparence selon vos préférences</p>

      <div className="flex items-center justify-between gap-4">
        {themes.map((t) => (
          <button
            key={t.id}
            title={t.label}
            onClick={() => setTheme(t.id as any)}
            className={clsx(
              'relative w-10 h-10 transition-all duration-200 ease-out',
              'hover:scale-[1.12] active:ring-2 active:ring-white/70',
              'rounded-lg',
              t.className,
              {
                'ring-2 ring-white': theme === t.id,
                'opacity-70': theme !== t.id,
              }
            )}
            style={{
              clipPath:
                'polygon(25% 5%, 75% 5%, 100% 50%, 75% 95%, 25% 95%, 0% 50%)',
            }}
          ></button>
        ))}
      </div>
    </div>
  )
}