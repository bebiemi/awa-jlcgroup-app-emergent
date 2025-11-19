import { useEffect, useState } from 'react'

export default function AnimatedGradientBar() {
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      // Calculer la position du breadcrumb (header height = 64px)
      const headerHeight = 64
      const scrollY = window.scrollY
      
      // La barre se remplit de 0 à headerHeight pixels de scroll
      // 0px scroll = 0% largeur
      // headerHeight scroll = 100% largeur
      const progress = Math.min(scrollY / headerHeight, 1)
      setScrollProgress(progress)
    }

    // Écouter le scroll
    window.addEventListener('scroll', handleScroll, { passive: true })
    
    // Initialiser au montage
    handleScroll()

    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  return (
    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-200 overflow-hidden">
      <div 
        className="h-full bg-gradient-to-r from-jlc-neon-pink-gray via-jlc-magenta to-jlc-indigo-dark transition-all duration-300 ease-out"
        style={{ 
          width: `${scrollProgress * 100}%`,
          transformOrigin: 'left'
        }}
      />
    </div>
  )
}
