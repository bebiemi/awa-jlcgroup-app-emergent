import { useSidebarTheme } from '@/contexts/SidebarThemeContext'

export default function SidebarPreferencesPanel() {
  const { theme, setTheme } = useSidebarTheme()

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-lg font-semibold mb-4">Préférences de la sidebar</h2>

      <div>
        <label className="block text-sm mb-2">Thème</label>
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as any)}
          className="p-2 border rounded"
        >
          <option value="dark">Thème dark</option>
          <option value="magenta">Thème magenta</option>
          <option value="light">Thème clair</option>
        </select>
      </div>
    </div>
  )
}