"""
Core Logic Module: Stream detection, validation, and career recommendation engine.
Ensures stream-aligned recommendations with rule-based filtering.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from langdetect import detect, LangDetectException
import logging

logger = logging.getLogger(__name__)


class StreamDetector:
    """Detects student stream from academic inputs."""
    
    # Stream keywords
    STREAM_KEYWORDS = {
        "PCM": {
            "en": ["physics", "chemistry", "mathematics", "math", "pcm", "engineering", "tech"],
            "mr": ["भौतिकशास्त्र", "रसायनशास्त्र", "गणित", "अभियांत्रिकी"]
        },
        "PCB": {
            "en": ["biology", "bio", "medical", "medicine", "pcb", "healthcare", "doctor", "neet"],
            "mr": ["जीवशास्त्र", "वैद्यकीय", "औषध", "डॉक्टर", "आरोग्य"]
        },
        "Commerce": {
            "en": ["commerce", "accounting", "accountancy", "business", "economics", "finance", "ca"],
            "mr": ["वाणिज्य", "लेखा", "व्यवसाय", "अर्थशास्त्र", "वित्त"]
        },
        "Arts": {
            "en": ["arts", "humanities", "history", "psychology", "sociology", "literature", "political"],
            "mr": ["कला", "मानवतावादी", "इतिहास", "मानसशास्त्र", "समाजशास्त्र", "साहित्य"]
        },
        "Vocational": {
            "en": ["vocational", "skill", "trade", "technical", "certification", "diploma", "iti"],
            "mr": ["व्यावसायिक", "कौशल्य", "व्यापार", "तांत्रिक", "प्रमाणपत्र"]
        }
    }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language from text."""
        try:
            lang = detect(text)
            return "mr" if lang == "mr" else "en"
        except LangDetectException:
            return "en"
    
    @staticmethod
    def detect_stream(favourite_subjects: str, weak_subjects: str = "", 
                     interests: str = "") -> Optional[str]:
        """
        Detect stream from student inputs.
        Returns stream code or None if ambiguous.
        """
        text = f"{favourite_subjects} {weak_subjects} {interests}".lower()
        
        stream_scores = {stream: 0 for stream in StreamDetector.STREAM_KEYWORDS.keys()}
        
        for stream, keywords in StreamDetector.STREAM_KEYWORDS.items():
            for lang in ["en", "mr"]:
                for keyword in keywords[lang]:
                    if keyword in text:
                        stream_scores[stream] += 1
        
        # Find stream with highest score
        max_score = max(stream_scores.values())
        if max_score == 0:
            return None
        
        detected_stream = max(stream_scores, key=stream_scores.get)
        
        # Require minimum confidence
        if max_score >= 2:
            return detected_stream
        
        return None
    
    @staticmethod
    def validate_stream_alignment(career_name: str, student_stream: str, 
                                  career_data: Dict) -> bool:
        """
        Validate that career recommendation aligns with student stream.
        CRITICAL: Prevents cross-stream recommendations.
        """
        if student_stream not in career_data["streams"]:
            return False
        
        stream_careers = [c["name"].lower() for c in career_data["streams"][student_stream]["careers"]]
        career_lower = career_name.lower()
        
        # Check if career exists in stream's career list
        for stream_career in stream_careers:
            if stream_career in career_lower or career_lower in stream_career:
                return True
        
        # Additional validation: Check for forbidden cross-stream patterns
        forbidden_patterns = {
            "Arts": ["engineering", "medical", "doctor", "mbbs", "neet", "jee", "ca", "chartered accountancy"],
            "Commerce": ["medical", "doctor", "mbbs", "neet", "engineering", "jee", "core engineering"],
            "PCM": ["medical", "doctor", "mbbs", "neet", "biology"],
            "PCB": ["software engineer", "core engineering", "jee", "computer science engineering"],
            "Vocational": ["mbbs", "neet", "jee", "engineering degree", "medical degree"]
        }
        
        if student_stream in forbidden_patterns:
            for pattern in forbidden_patterns[student_stream]:
                if pattern in career_lower:
                    logger.warning(f"Blocked cross-stream recommendation: {career_name} for {student_stream}")
                    return False
        
        return True


class CareerRecommender:
    """Generates stream-aligned career recommendations."""
    
    def __init__(self, data_file: Optional[str] = None):
        """Load career data."""
        if data_file is None:
            data_file = os.path.join(os.path.dirname(__file__), "data.json")
        with open(data_file, "r", encoding="utf-8") as f:
            self.career_data = json.load(f)
    
    def get_stream_careers(self, stream: str) -> List[Dict]:
        """Get all careers for a specific stream."""
        if stream not in self.career_data["streams"]:
            return []
        return self.career_data["streams"][stream]["careers"]
    
    def filter_careers(self, stream: str, student_profile: Dict) -> List[Dict]:
        """
        Filter careers based on student profile.
        Rule-based filtering ensures stream alignment.
        """
        careers = self.get_stream_careers(stream)
        if not careers:
            return []
        
        # Apply filters based on profile
        filtered = []
        
        for career in careers:
            score = 0
            
            # Match based on interests
            interests = student_profile.get("interests", "").lower()
            career_name = career["name"].lower()
            
            # Scoring logic
            if any(keyword in interests for keyword in ["tech", "technology", "innovation"]):
                if "engineering" in career_name or "data" in career_name:
                    score += 2
            
            if any(keyword in interests for keyword in ["medical", "health", "doctor"]):
                if "medical" in career_name or "pharmacy" in career_name or "biotechnology" in career_name:
                    score += 2
            
            if any(keyword in interests for keyword in ["business", "finance", "money"]):
                if "business" in career_name or "finance" in career_name or "ca" in career_name:
                    score += 2
            
            if any(keyword in interests for keyword in ["creative", "writing", "communication"]):
                if "journalism" in career_name or "psychology" in career_name:
                    score += 2
            
            # Marks-based filtering
            marks_range = student_profile.get("marks_range", "")
            if "80-90" in marks_range or "90+" in marks_range:
                # High achievers can consider competitive careers
                score += 1
            elif "70-80" in marks_range:
                # Medium achievers
                score += 0.5
            
            # Stream-specific aptitude matching
            stream_aptitude = student_profile.get("stream_aptitude", {})
            if stream == "PCM":
                if stream_aptitude.get("math_aptitude", "").lower() in ["high", "very high", "comfortable"]:
                    if "engineering" in career_name or "data" in career_name:
                        score += 1.5
            elif stream == "PCB":
                if stream_aptitude.get("biology_interest", "").lower() in ["high", "very high", "yes"]:
                    if "medical" in career_name or "biotechnology" in career_name:
                        score += 1.5
            elif stream == "Commerce":
                if stream_aptitude.get("accounting_aptitude", "").lower() in ["high", "comfortable", "yes"]:
                    if "ca" in career_name or "accounting" in career_name:
                        score += 1.5
            elif stream == "Arts":
                if stream_aptitude.get("communication", "").lower() in ["high", "strong", "yes"]:
                    if "journalism" in career_name or "law" in career_name:
                        score += 1.5
            
            filtered.append((career, score))
        
        # Sort by score and return top 3
        filtered.sort(key=lambda x: x[1], reverse=True)
        top_careers = [career for career, score in filtered[:3]]
        
        # If we have less than 3, fill with remaining careers
        if len(top_careers) < 3:
            remaining = [c for c in careers if c not in top_careers]
            top_careers.extend(remaining[:3 - len(top_careers)])
        
        return top_careers[:3]
    
    def format_recommendation(self, career: Dict, stream: str, language: str = "en") -> Dict:
        """Format career recommendation with all required details."""
        if language == "mr":
            return {
                "name": career["name"],
                "pathway": career["pathway"],
                "entrance_exams": career["entrance_exams"],
                "skills": career["skills"],
                "risks": career["risks"],
                "stream_justification": f"ही करिअर {self.career_data['streams'][stream]['name']} स्ट्रीमशी संरेखित आहे."
            }
        else:
            return {
                "name": career["name"],
                "pathway": career["pathway"],
                "entrance_exams": career["entrance_exams"],
                "skills": career["skills"],
                "risks": career["risks"],
                "stream_justification": f"This career aligns with {self.career_data['streams'][stream]['name']} stream."
            }


class StudentProfile:
    """Manages student profile data throughout the conversation."""
    
    def __init__(self):
        self.data = {
            "favourite_subjects": "",
            "weak_subjects": "",
            "marks_range": "",
            "interests": "",
            "stream": None,
            "stream_aptitude": {},
            "personality_traits": "",
            "budget_preference": "",
            "language": "en"
        }
    
    def update(self, field: str, value: str):
        """Update a field in the profile."""
        if field in self.data:
            self.data[field] = value
    
    def set_stream(self, stream: str):
        """Set confirmed stream."""
        self.data["stream"] = stream
    
    def set_language(self, language: str):
        """Set conversation language."""
        self.data["language"] = language
    
    def get(self, field: str, default=None):
        """Get a field value."""
        return self.data.get(field, default)
    
    def is_complete(self) -> bool:
        """Check if profile has minimum required data."""
        required = ["favourite_subjects", "weak_subjects", "marks_range", "interests", "stream"]
        return all(self.data.get(field) for field in required)
    
    def reset(self):
        """Reset profile to initial state."""
        self.data = {
            "favourite_subjects": "",
            "weak_subjects": "",
            "marks_range": "",
            "interests": "",
            "stream": None,
            "stream_aptitude": {},
            "personality_traits": "",
            "budget_preference": "",
            "language": "en"
        }
    
    def to_dict(self) -> Dict:
        """Get profile as dictionary."""
        return self.data.copy()

