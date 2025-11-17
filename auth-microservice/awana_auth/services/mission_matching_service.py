"""
Mission Matching Service
Service de calcul du score de correspondance entre profil utilisateur et missions
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MissionMatchingService:
    """
    Service pour calculer le score de matching entre un profil et une mission
    
    Algorithme de score pondéré :
    - Compétences (skills) : 40%
    - Années d'expérience : 25%
    - Secteurs d'activité : 20%
    - Niveau d'études : 15%
    
    Score final : 0-100
    """
    
    # Pondérations pour le calcul du score
    WEIGHTS = {
        'skills': 0.40,      # 40%
        'experience': 0.25,  # 25%
        'sectors': 0.20,     # 20%
        'education': 0.15    # 15%
    }
    
    # Mapping des niveaux d'expérience (en années)
    EXPERIENCE_LEVELS = {
        'junior': (0, 2),
        '0-2 ans': (0, 2),
        'intermediate': (2, 5),
        '2-5 ans': (2, 5),
        'senior': (5, 10),
        '5-10 ans': (5, 10),
        'expert': (10, 100),
        '10+ ans': (10, 100),
        '10 ans et plus': (10, 100),
    }
    
    # Mapping des niveaux d'études
    EDUCATION_LEVELS = {
        'aucun': 0,
        'primaire': 1,
        'collège': 2,
        'lycée': 3,
        'bac': 4,
        'bac+2': 5,
        'bac+3': 6,
        'licence': 6,
        'bac+5': 7,
        'master': 7,
        'bac+8': 8,
        'doctorat': 8,
        'phd': 8
    }
    
    @classmethod
    def calculate_matching_score(
        cls,
        mission: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score de matching entre une mission et un profil utilisateur
        
        Args:
            mission: Dictionnaire contenant les infos de la mission
            user_profile: Dictionnaire contenant le profil utilisateur
            
        Returns:
            Dict contenant :
            - score: score total (0-100)
            - breakdown: détail des scores par catégorie
            - matched_skills: compétences communes
            - matched_sectors: secteurs communs
            - recommendations: suggestions pour améliorer le matching
        """
        
        # Initialisation
        breakdown = {
            'skills': {'score': 0, 'weight': cls.WEIGHTS['skills'] * 100},
            'experience': {'score': 0, 'weight': cls.WEIGHTS['experience'] * 100},
            'sectors': {'score': 0, 'weight': cls.WEIGHTS['sectors'] * 100},
            'education': {'score': 0, 'weight': cls.WEIGHTS['education'] * 100}
        }
        
        matched_skills = []
        matched_sectors = []
        recommendations = []
        
        # 1. Score des compétences (40%)
        skills_score, matched_skills = cls._calculate_skills_score(
            mission.get('required_skills', []),
            user_profile.get('skills', [])
        )
        breakdown['skills']['score'] = skills_score
        breakdown['skills']['matched'] = len(matched_skills)
        breakdown['skills']['total_required'] = len(mission.get('required_skills', []))
        
        # 2. Score de l'expérience (25%)
        experience_score, exp_details = cls._calculate_experience_score(
            mission.get('experience_required', ''),
            user_profile.get('years_of_experience', 0)
        )
        breakdown['experience']['score'] = experience_score
        breakdown['experience'].update(exp_details)
        
        # 3. Score des secteurs (20%)
        sectors_score, matched_sectors = cls._calculate_sectors_score(
            mission.get('job_type', ''),
            user_profile.get('sectors', [])
        )
        breakdown['sectors']['score'] = sectors_score
        breakdown['sectors']['matched'] = len(matched_sectors)
        
        # 4. Score du niveau d'études (15%)
        education_score, edu_details = cls._calculate_education_score(
            mission.get('education_level', ''),
            user_profile.get('education_level', '')
        )
        breakdown['education']['score'] = education_score
        breakdown['education'].update(edu_details)
        
        # Calcul du score total pondéré
        total_score = (
            skills_score * cls.WEIGHTS['skills'] +
            experience_score * cls.WEIGHTS['experience'] +
            sectors_score * cls.WEIGHTS['sectors'] +
            education_score * cls.WEIGHTS['education']
        )
        
        # Générer des recommandations
        recommendations = cls._generate_recommendations(breakdown, matched_skills, user_profile, mission)
        
        return {
            'score': round(total_score, 2),
            'breakdown': breakdown,
            'matched_skills': matched_skills,
            'matched_sectors': matched_sectors,
            'recommendations': recommendations,
            'is_good_match': total_score >= 70,  # Seuil de "bon match"
            'is_excellent_match': total_score >= 85,  # Seuil de "excellent match"
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    @classmethod
    def _calculate_skills_score(
        cls,
        required_skills: List[str],
        user_skills: List[Dict]
    ) -> tuple[float, List[str]]:
        """
        Calcule le score de correspondance des compétences
        
        Returns:
            (score sur 100, liste des compétences matchées)
        """
        if not required_skills:
            return 100.0, []  # Pas de compétences requises = 100%
        
        # Extraire les noms de compétences de l'utilisateur (normaliser)
        user_skill_names = [
            skill.get('name', '').lower().strip() 
            if isinstance(skill, dict) else str(skill).lower().strip()
            for skill in user_skills
        ]
        
        # Normaliser les compétences requises
        required_skills_normalized = [s.lower().strip() for s in required_skills]
        
        # Trouver les correspondances exactes
        matched = []
        for required in required_skills_normalized:
            if required in user_skill_names:
                matched.append(required)
        
        # Calcul du score : pourcentage de compétences requises possédées
        score = (len(matched) / len(required_skills)) * 100
        
        return round(score, 2), matched
    
    @classmethod
    def _calculate_experience_score(
        cls,
        required_experience: str,
        user_experience_years: int
    ) -> tuple[float, Dict]:
        """
        Calcule le score d'expérience
        
        Returns:
            (score sur 100, détails)
        """
        if not required_experience:
            return 100.0, {'required': 'non spécifié', 'user_has': user_experience_years}
        
        # Normaliser
        required_exp_normalized = required_experience.lower().strip()
        
        # Trouver la plage d'expérience requise
        exp_range = None
        for key, value in cls.EXPERIENCE_LEVELS.items():
            if key in required_exp_normalized:
                exp_range = value
                break
        
        if not exp_range:
            # Si on ne peut pas parser, essayer d'extraire des nombres
            try:
                # Chercher des patterns comme "3 ans", "5-7 ans", etc.
                import re
                numbers = re.findall(r'\d+', required_experience)
                if numbers:
                    if len(numbers) == 1:
                        exp_range = (int(numbers[0]), int(numbers[0]) + 2)
                    else:
                        exp_range = (int(numbers[0]), int(numbers[-1]))
            except:
                pass
        
        if not exp_range:
            # Par défaut, considérer comme correspondance partielle
            return 50.0, {'required': required_experience, 'user_has': user_experience_years, 'status': 'unclear'}
        
        min_exp, max_exp = exp_range
        
        # Calcul du score
        if min_exp <= user_experience_years <= max_exp:
            # Expérience dans la plage requise = 100%
            score = 100.0
            status = 'perfect_match'
        elif user_experience_years > max_exp:
            # Surqualifié (peut être bon ou mauvais selon le contexte)
            # Score décroissant au-delà de max_exp
            excess = user_experience_years - max_exp
            penalty = min(excess * 5, 30)  # Max 30% de pénalité
            score = max(70.0, 100.0 - penalty)
            status = 'overqualified'
        else:
            # Sous-qualifié
            # Score proportionnel à l'expérience possédée
            if min_exp > 0:
                score = (user_experience_years / min_exp) * 100
                score = min(score, 80.0)  # Max 80% si sous-qualifié
            else:
                score = 50.0
            status = 'underqualified'
        
        return round(score, 2), {
            'required_range': f"{min_exp}-{max_exp} ans",
            'user_has': user_experience_years,
            'status': status
        }
    
    @classmethod
    def _calculate_sectors_score(
        cls,
        mission_job_type: str,
        user_sectors: List[str]
    ) -> tuple[float, List[str]]:
        """
        Calcule le score de correspondance des secteurs d'activité
        
        Returns:
            (score sur 100, secteurs matchés)
        """
        if not mission_job_type:
            return 100.0, []
        
        if not user_sectors:
            return 0.0, []
        
        # Normaliser
        job_type_normalized = mission_job_type.lower().strip()
        user_sectors_normalized = [s.lower().strip() for s in user_sectors]
        
        # Correspondance exacte
        matched = []
        if job_type_normalized in user_sectors_normalized:
            matched.append(job_type_normalized)
            return 100.0, matched
        
        # Correspondance partielle (recherche de mots-clés)
        for sector in user_sectors_normalized:
            if sector in job_type_normalized or job_type_normalized in sector:
                matched.append(sector)
        
        if matched:
            return 70.0, matched  # Correspondance partielle = 70%
        
        return 0.0, []
    
    @classmethod
    def _calculate_education_score(
        cls,
        required_education: str,
        user_education: str
    ) -> tuple[float, Dict]:
        """
        Calcule le score du niveau d'études
        
        Returns:
            (score sur 100, détails)
        """
        if not required_education:
            return 100.0, {'required': 'non spécifié', 'user_has': user_education}
        
        # Normaliser
        required_normalized = required_education.lower().strip()
        user_normalized = user_education.lower().strip() if user_education else ''
        
        # Trouver les niveaux
        required_level = None
        user_level = None
        
        for key, value in cls.EDUCATION_LEVELS.items():
            if key in required_normalized:
                required_level = value
            if key in user_normalized:
                user_level = value
        
        if required_level is None:
            # Niveau requis non reconnu, score neutre
            return 50.0, {'required': required_education, 'user_has': user_education, 'status': 'unclear'}
        
        if user_level is None:
            # Niveau utilisateur non renseigné
            return 30.0, {'required': required_education, 'user_has': user_education or 'non renseigné', 'status': 'missing'}
        
        # Calcul du score
        if user_level >= required_level:
            # Niveau égal ou supérieur = 100%
            score = 100.0
            status = 'qualified'
        else:
            # Niveau inférieur : score proportionnel
            score = (user_level / required_level) * 100
            score = min(score, 70.0)  # Max 70% si sous-qualifié
            status = 'underqualified'
        
        return round(score, 2), {
            'required': required_education,
            'user_has': user_education,
            'status': status
        }
    
    @classmethod
    def _generate_recommendations(
        cls,
        breakdown: Dict,
        matched_skills: List[str],
        user_profile: Dict,
        mission: Dict
    ) -> List[str]:
        """
        Génère des recommandations pour améliorer le matching
        """
        recommendations = []
        
        # Compétences manquantes
        if breakdown['skills']['score'] < 70:
            required = set(s.lower() for s in mission.get('required_skills', []))
            user_has = set(matched_skills)
            missing = required - user_has
            if missing:
                recommendations.append(
                    f"Compétences à acquérir : {', '.join(list(missing)[:3])}"
                )
        
        # Expérience insuffisante
        if breakdown['experience']['score'] < 70 and breakdown['experience'].get('status') == 'underqualified':
            recommendations.append(
                f"Vous pourriez avoir besoin de plus d'expérience ({breakdown['experience'].get('required_range', '')})"
            )
        
        # Secteur différent
        if breakdown['sectors']['score'] < 50:
            recommendations.append(
                f"Considérez développer votre expérience dans le secteur : {mission.get('job_type', '')}"
            )
        
        # Niveau d'études
        if breakdown['education']['score'] < 70 and breakdown['education'].get('status') == 'underqualified':
            recommendations.append(
                f"Formation recommandée : {mission.get('education_level', '')}"
            )
        
        return recommendations
