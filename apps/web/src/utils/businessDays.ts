/**
 * Utilitaires pour le calcul des jours ouvrés au Gabon
 */

// Jours fériés fixes au Gabon (2025)
const GABON_PUBLIC_HOLIDAYS_2025 = [
  '2025-01-01', // Jour de l'an
  '2025-04-17', // Journée des Droits de la femme
  '2025-04-21', // Lundi de Pâques
  '2025-05-01', // Fête du Travail
  '2025-06-08', // Pentecôte
  '2025-07-28', // Fin du Ramadan
  '2025-08-15', // Assomption
  '2025-08-16', // Indépendance
  '2025-08-17', // Indépendance (jour 2)
  '2025-10-03', // Fête du sacrifice
  '2025-11-01', // Toussaint
  '2025-12-25', // Noël
];

/**
 * Vérifier si une date est un jour férié
 */
export function isPublicHoliday(date: Date): boolean {
  const dateStr = date.toISOString().split('T')[0];
  return GABON_PUBLIC_HOLIDAYS_2025.includes(dateStr);
}

/**
 * Vérifier si une date est un week-end (samedi ou dimanche)
 */
export function isWeekend(date: Date): boolean {
  const day = date.getDay();
  return day === 0 || day === 6; // 0 = dimanche, 6 = samedi
}

/**
 * Vérifier si une date est un jour ouvré
 */
export function isWorkingDay(date: Date): boolean {
  return !isWeekend(date) && !isPublicHoliday(date);
}

/**
 * Ajouter des jours ouvrés à une date
 * @param startDate Date de départ
 * @param workingDays Nombre de jours ouvrés à ajouter
 * @returns Nouvelle date après ajout des jours ouvrés
 */
export function addWorkingDays(startDate: Date, workingDays: number): Date {
  const result = new Date(startDate);
  let daysAdded = 0;

  while (daysAdded < workingDays) {
    result.setDate(result.getDate() + 1);
    if (isWorkingDay(result)) {
      daysAdded++;
    }
  }

  return result;
}

/**
 * Soustraire des jours ouvrés à une date
 * @param startDate Date de départ
 * @param workingDays Nombre de jours ouvrés à soustraire
 * @returns Nouvelle date après soustraction des jours ouvrés
 */
export function subtractWorkingDays(startDate: Date, workingDays: number): Date {
  const result = new Date(startDate);
  let daysSubtracted = 0;

  while (daysSubtracted < workingDays) {
    result.setDate(result.getDate() - 1);
    if (isWorkingDay(result)) {
      daysSubtracted++;
    }
  }

  return result;
}

/**
 * Calculer le nombre de jours ouvrés entre deux dates
 * @param startDate Date de début
 * @param endDate Date de fin
 * @returns Nombre de jours ouvrés
 */
export function getWorkingDaysBetween(startDate: Date, endDate: Date): number {
  let count = 0;
  const current = new Date(startDate);

  while (current <= endDate) {
    if (isWorkingDay(current)) {
      count++;
    }
    current.setDate(current.getDate() + 1);
  }

  return count;
}

/**
 * Vérifier si on est à J-X jours ouvrés d'une date
 * @param targetDate Date cible
 * @param workingDays Nombre de jours ouvrés avant
 * @returns true si on est dans la période
 */
export function isWithinWorkingDays(targetDate: Date, workingDays: number): boolean {
  const now = new Date();
  const threshold = subtractWorkingDays(targetDate, workingDays);
  return now >= threshold && now <= targetDate;
}

/**
 * Calculer les jours restants (calendaires et ouvrés) jusqu'à une date
 */
export function getDaysUntil(targetDate: Date): {
  calendar: number;
  working: number;
  isWithinTwoWeeks: boolean;
} {
  const now = new Date();
  const diffTime = targetDate.getTime() - now.getTime();
  const calendarDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const workingDays = getWorkingDaysBetween(now, targetDate);

  return {
    calendar: Math.max(0, calendarDays),
    working: Math.max(0, workingDays),
    isWithinTwoWeeks: calendarDays <= 14 && calendarDays > 0,
  };
}
