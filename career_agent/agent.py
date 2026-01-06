"""
Agent Module: Orchestrates conversation flow using LangChain.
Enforces one-question-at-a-time rule and manages conversation state.
"""

import json
import os
from typing import Dict, Optional, List, Tuple
from career_agent.logic import StreamDetector, CareerRecommender, StudentProfile
from career_agent.llm import LLMProvider
import logging

logger = logging.getLogger(__name__)


class CareerGuidanceAgent:
    """Main agent orchestrating the career guidance conversation."""
    
    # Conversation phases
    PHASE_WELCOME = "welcome"
    PHASE_GENERAL_QUESTIONS = "general_questions"
    PHASE_STREAM_CONFIRMATION = "stream_confirmation"
    PHASE_STREAM_QUESTIONS = "stream_questions"
    PHASE_RECOMMENDATIONS = "recommendations"
    PHASE_COMPLETE = "complete"
    
    def __init__(self):
        self.profile = StudentProfile()
        self.stream_detector = StreamDetector()
        self.recommender = CareerRecommender()
        self.llm = LLMProvider()
        self.phase = self.PHASE_WELCOME
        self.current_question_index = 0
        self.language = "en"
        
        # Load questions - handle path correctly
        data_file = os.path.join(os.path.dirname(__file__), "data.json")
        with open(data_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def _get_question_text(self, question: Dict) -> str:
        """Get question text in current language."""
        key = "text_mr" if self.language == "mr" else "text_en"
        return question.get(key, question.get("text_en", ""))
    
    def _detect_language(self, text: str):
        """Detect and set language from first user input."""
        if self.language == "en":  # Only detect on first input
            detected = self.stream_detector.detect_language(text)
            self.language = detected
            self.profile.set_language(detected)
            logger.info(f"Language detected: {self.language}")
    
    def _get_welcome_message(self) -> str:
        """Get welcome message in current language."""
        if self.language == "mr":
            return "नमस्कार! मी तुमचा करिअर मार्गदर्शन सहाय्यक आहे. मी तुम्हाला तुमच्या शैक्षणिक स्ट्रीम आणि आवडींवर आधारित करिअर शिफारसी देण्यात मदत करू. चला सुरू करूया!"
        else:
            return "Hello! I'm your career guidance assistant. I'll help you discover career options based on your academic stream and interests. Let's begin!"
    
    def _get_next_general_question(self) -> Optional[Dict]:
        """Get next general question."""
        questions = self.data["questions"]["general"]
        if self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None
    
    def _get_stream_questions(self, stream: str) -> List[Dict]:
        """Get stream-specific questions."""
        return self.data["questions"]["stream_specific"].get(stream, [])
    
    def _generate_stream_confirmation_prompt(self, detected_stream: str) -> str:
        """Generate prompt to confirm detected stream."""
        stream_name = self.data["streams"][detected_stream]["name"]
        if self.language == "mr":
            return f"तुमच्या उत्तरांवर आधारित, तुम्ही {stream_name} स्ट्रीममध्ये असल्याचे दिसते. हे बरोबर आहे का? (होय/नाही)"
        else:
            return f"Based on your answers, it appears you are in the {stream_name} stream. Is this correct? (Yes/No)"
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate career recommendations using rule-based filtering and LLM explanation."""
        stream = self.profile.get("stream")
        if not stream:
            return []
        
        # Rule-based filtering (CRITICAL: ensures stream alignment)
        filtered_careers = self.recommender.filter_careers(stream, self.profile.to_dict())
        
        # Format recommendations
        recommendations = []
        for career in filtered_careers:
            # Validate stream alignment (double-check)
            if not StreamDetector.validate_stream_alignment(
                career["name"], stream, self.data
            ):
                logger.warning(f"Skipping invalid career: {career['name']} for stream: {stream}")
                continue
            
            formatted = self.recommender.format_recommendation(career, stream, self.language)
            recommendations.append(formatted)
        
        # Ensure exactly 3 recommendations
        while len(recommendations) < 3 and len(filtered_careers) > len(recommendations):
            remaining = [c for c in filtered_careers if c not in [r["name"] for r in recommendations]]
            if remaining:
                career = remaining[0]
                if StreamDetector.validate_stream_alignment(career["name"], stream, self.data):
                    formatted = self.recommender.format_recommendation(career, stream, self.language)
                    recommendations.append(formatted)
            else:
                break
        
        return recommendations[:3]
    
    def _format_recommendations_response(self, recommendations: List[Dict]) -> str:
        """Format recommendations as final response with proper formatting."""
        if self.language == "mr":
            response = "तुमच्या प्रोफाइलवर आधारित, येथे 3 करिअर शिफारसी आहेत:\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"**{i}. {rec['name']}**\n\n"
                response += f"**स्ट्रीम औचित्य:** {rec['stream_justification']}\n\n"
                response += f"**शैक्षणिक मार्ग:** {rec['pathway']}\n\n"
                response += f"**प्रवेश परीक्षा:** {', '.join(rec['entrance_exams'])}\n\n"
                response += f"**आवश्यक कौशल्ये:** {', '.join(rec['skills'])}\n\n"
                response += f"**जोखीम/मर्यादा:** {rec['risks']}\n\n"
                response += "---\n\n"
            
            response += "\n⚠️ **महत्वाचे:** हे मार्गदर्शन केवळ सूचक आहे. कृपया तुमचा निर्णय प्रमाणित मानवी करिअर काउन्सेलरसोबत पुष्टी करा."
        else:
            response = "**Based on your profile, here are 3 career recommendations:**\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"**{i}. {rec['name']}**\n\n"
                response += f"**Stream Justification:** {rec['stream_justification']}\n\n"
                response += f"**Education Pathway:** {rec['pathway']}\n\n"
                response += f"**Entrance Exams:** {', '.join(rec['entrance_exams'])}\n\n"
                response += f"**Required Skills:** {', '.join(rec['skills'])}\n\n"
                response += f"**Risks/Limitations:** {rec['risks']}\n\n"
                response += "---\n\n"
            
            response += "\n⚠️ **Important:** This guidance is indicative only. Please confirm your decision with a certified human career counselor."
        
        return response
    
    def process_input(self, user_input: str) -> Tuple[str, bool]:
        """
        Process user input and return response.
        Returns: (response_text, is_complete)
        Enforces one-question-at-a-time rule.
        """
        if not user_input or not user_input.strip():
            if self.language == "mr":
                return "कृपया वैध उत्तर प्रदान करा.", False
            else:
                return "Please provide a valid answer.", False
        
        user_input = user_input.strip()
        
        # Detect language on first input
        if self.phase == self.PHASE_WELCOME or self.current_question_index == 0:
            self._detect_language(user_input)
        
        # Phase: Welcome
        if self.phase == self.PHASE_WELCOME:
            self.phase = self.PHASE_GENERAL_QUESTIONS
            self.current_question_index = 0
            question = self._get_next_general_question()
            if question:
                return self._get_question_text(question), False
            return self._get_welcome_message(), False
        
        # Phase: General Questions
        if self.phase == self.PHASE_GENERAL_QUESTIONS:
            question = self._get_next_general_question()
            if question:
                # Store answer
                self.profile.update(question["id"], user_input)
                self.current_question_index += 1
                
                # Check if more general questions
                next_question = self._get_next_general_question()
                if next_question:
                    return self._get_question_text(next_question), False
                else:
                    # All general questions answered, detect stream
                    self.phase = self.PHASE_STREAM_CONFIRMATION
                    detected = self.stream_detector.detect_stream(
                        self.profile.get("favourite_subjects"),
                        self.profile.get("weak_subjects"),
                        self.profile.get("interests")
                    )
                    
                    if detected:
                        self.detected_stream = detected
                        return self._generate_stream_confirmation_prompt(detected), False
                    else:
                        # Ambiguous, ask explicitly
                        if self.language == "mr":
                            return "तुमचा शैक्षणिक स्ट्रीम काय आहे? (PCM/PCB/Commerce/Arts/Vocational)", False
                        else:
                            return "What is your academic stream? (PCM/PCB/Commerce/Arts/Vocational)", False
        
        # Phase: Stream Confirmation
        if self.phase == self.PHASE_STREAM_CONFIRMATION:
            user_input_lower = user_input.lower()
            
            # Check for yes/no or direct stream input
            stream = None
            
            if self.language == "mr":
                if "होय" in user_input_lower or "yes" in user_input_lower or "हो" in user_input_lower:
                    if hasattr(self, 'detected_stream'):
                        stream = self.detected_stream
                        self.profile.set_stream(stream)
                    else:
                        # Should not happen, but handle gracefully
                        return "कृपया तुमचा स्ट्रीम स्पष्ट करा (PCM/PCB/Commerce/Arts/Vocational)", False
                elif "नाही" in user_input_lower or "no" in user_input_lower or "न" in user_input_lower:
                    return "कृपया तुमचा स्ट्रीम स्पष्ट करा (PCM/PCB/Commerce/Arts/Vocational)", False
                else:
                    # Direct stream input
                    stream_map = {
                        "pcm": "PCM", "pcb": "PCB", "commerce": "Commerce",
                        "arts": "Arts", "vocational": "Vocational"
                    }
                    stream = stream_map.get(user_input_lower, None)
                    if stream:
                        self.profile.set_stream(stream)
                    else:
                        return "अवैध स्ट्रीम. कृपया PCM, PCB, Commerce, Arts किंवा Vocational निवडा.", False
            else:
                # English
                if "yes" in user_input_lower or "y" == user_input_lower:
                    if hasattr(self, 'detected_stream'):
                        stream = self.detected_stream
                        self.profile.set_stream(stream)
                    else:
                        return "Please specify your stream (PCM/PCB/Commerce/Arts/Vocational)", False
                elif "no" in user_input_lower or "n" == user_input_lower:
                    return "Please specify your stream (PCM/PCB/Commerce/Arts/Vocational)", False
                else:
                    stream_map = {
                        "pcm": "PCM", "pcb": "PCB", "commerce": "Commerce",
                        "arts": "Arts", "vocational": "Vocational"
                    }
                    stream = stream_map.get(user_input_lower, None)
                    if stream:
                        self.profile.set_stream(stream)
                    else:
                        return "Invalid stream. Please choose PCM, PCB, Commerce, Arts, or Vocational.", False
            
            # Stream confirmed, move to stream-specific questions
            if self.profile.get("stream"):
                self.phase = self.PHASE_STREAM_QUESTIONS
                self.stream_questions = self._get_stream_questions(self.profile.get("stream"))
                self.current_question_index = 0
                
                if self.stream_questions:
                    question = self.stream_questions[0]
                    return self._get_question_text(question), False
                else:
                    # No stream-specific questions, move to recommendations
                    self.phase = self.PHASE_RECOMMENDATIONS
                    recommendations = self._generate_recommendations()
                    response = self._format_recommendations_response(recommendations)
                    self.phase = self.PHASE_COMPLETE
                    return response, True
        
        # Phase: Stream-specific Questions
        if self.phase == self.PHASE_STREAM_QUESTIONS:
            if hasattr(self, 'stream_questions') and self.current_question_index < len(self.stream_questions):
                question = self.stream_questions[self.current_question_index]
                # Store answer in stream_aptitude
                if "stream_aptitude" not in self.profile.data:
                    self.profile.data["stream_aptitude"] = {}
                self.profile.data["stream_aptitude"][question["id"]] = user_input
                
                self.current_question_index += 1
                
                # Check if more stream questions
                if self.current_question_index < len(self.stream_questions):
                    next_question = self.stream_questions[self.current_question_index]
                    return self._get_question_text(next_question), False
                else:
                    # All questions answered, generate recommendations
                    self.phase = self.PHASE_RECOMMENDATIONS
                    recommendations = self._generate_recommendations()
                    response = self._format_recommendations_response(recommendations)
                    self.phase = self.PHASE_COMPLETE
                    return response, True
        
        # Phase: Complete
        if self.phase == self.PHASE_COMPLETE:
            if self.language == "mr":
                return "संभाषण पूर्ण झाले आहे. पुन्हा सुरू करण्यासाठी, कृपया 'Restart' बटण वापरा.", True
            else:
                return "Conversation is complete. To start again, please use the 'Restart' button.", True
        
        # Fallback
        if self.language == "mr":
            return "अनपेक्षित त्रुटी. कृपया पुन्हा प्रयत्न करा.", False
        else:
            return "Unexpected error. Please try again.", False
    
    def reset(self):
        """Reset agent state completely."""
        self.profile.reset()
        self.llm.clear_history()
        self.phase = self.PHASE_WELCOME
        self.current_question_index = 0
        self.language = "en"
        if hasattr(self, 'detected_stream'):
            delattr(self, 'detected_stream')
        if hasattr(self, 'stream_questions'):
            delattr(self, 'stream_questions')
        logger.info("Agent reset complete")
    
    def get_current_phase(self) -> str:
        """Get current conversation phase."""
        return self.phase

