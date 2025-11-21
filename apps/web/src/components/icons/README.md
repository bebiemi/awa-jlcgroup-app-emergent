# Custom Icons - JLC Group

Collection d'icônes personnalisées pour l'application JLC Group.

## Icônes Disponibles

### 1. TalentsIcon / Intérimaires
Représente les travailleurs intérimaires et talents.
```tsx
import { TalentsIcon } from '@/components/icons/CustomIcons'

<TalentsIcon className="w-6 h-6 text-blue-600" />
```

### 2. MissionsIcon / Assignations
Représente les missions et assignations de travail.
```tsx
import { MissionsIcon } from '@/components/icons/CustomIcons'

<MissionsIcon className="w-6 h-6 text-indigo-600" />
```

### 3. EntreprisesIcon / Entreprises Clientes
Représente les entreprises clientes.
```tsx
import { EntreprisesIcon } from '@/components/icons/CustomIcons'

<EntreprisesIcon className="w-6 h-6 text-purple-600" />
```

### 4. RRHIcon / Ressources Humaines
Représente la gestion RH et les documents.
```tsx
import { RRHIcon } from '@/components/icons/CustomIcons'

<RRHIcon className="w-6 h-6 text-green-600" />
```

### 5. PlanningIcon / Disponibilités
Représente la gestion du planning et des disponibilités.
```tsx
import { PlanningIcon } from '@/components/icons/CustomIcons'

<PlanningIcon className="w-6 h-6 text-orange-600" />
```

### 6. PaieIcon / Facturation
Représente la gestion de la paie et de la facturation.
```tsx
import { PaieIcon } from '@/components/icons/CustomIcons'

<PaieIcon className="w-6 h-6 text-teal-600" />
```

### 7. RelationTripartiteIcon
Représente la relation tripartite (JLC – Client – Intérimaire).
```tsx
import { RelationTripartiteIcon } from '@/components/icons/CustomIcons'

<RelationTripartiteIcon className="w-6 h-6 text-pink-600" />
```

### 8. PresenceAfriqueIcon
Pictogramme stylisé représentant la présence en Afrique.
```tsx
import { PresenceAfriqueIcon } from '@/components/icons/CustomIcons'

<PresenceAfriqueIcon className="w-6 h-6 text-yellow-600" />
```

## Utilisation

### Import individuel
```tsx
import { TalentsIcon, MissionsIcon } from '@/components/icons/CustomIcons'

function MyComponent() {
  return (
    <div>
      <TalentsIcon className="w-5 h-5" />
      <MissionsIcon className="w-5 h-5" />
    </div>
  )
}
```

### Import de toute la collection
```tsx
import CustomIcons from '@/components/icons/CustomIcons'

function MyComponent() {
  return (
    <div>
      <CustomIcons.Talents className="w-5 h-5" />
      <CustomIcons.Missions className="w-5 h-5" />
    </div>
  )
}
```

### Props disponibles
Toutes les icônes acceptent les props suivantes :
- `className` (string) - Classes CSS Tailwind ou autres
- `width` (number | string) - Largeur de l'icône (défaut: 24)
- `height` (number | string) - Hauteur de l'icône (défaut: 24)

### Exemple avec Sidebar
```tsx
import { TalentsIcon } from '@/components/icons/CustomIcons'

const navigationItems = [
  { 
    label: 'Talents', 
    path: '/talents', 
    icon: TalentsIcon 
  },
]
```

## Recommandations de couleurs

Pour maintenir la cohérence visuelle :

| Icône | Couleur recommandée | Classe Tailwind |
|-------|---------------------|-----------------|
| Talents | Bleu | `text-blue-600` |
| Missions | Indigo | `text-indigo-600` |
| Entreprises | Violet | `text-purple-600` |
| RRH | Vert | `text-green-600` |
| Planning | Orange | `text-orange-600` |
| Paie | Turquoise | `text-teal-600` |
| Relation Tripartite | Rose | `text-pink-600` |
| Présence Afrique | Jaune/Or | `text-yellow-600` |

## Notes techniques

- Les icônes utilisent `currentColor` pour hériter de la couleur du texte parent
- Dimensions par défaut : 24x24px
- ViewBox : 0 0 24 24
- Format : SVG optimisé
- Stroke width : 1.4 - 1.6 pour une apparence cohérente avec Heroicons
