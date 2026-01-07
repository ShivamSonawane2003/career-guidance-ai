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
            logger.debug(f"Detecting language from text: {text[:50]}...")
            detected = self.stream_detector.detect_language(text)
            self.language = detected
            self.profile.set_language(detected)
            logger.info(f"Language detected and set: {self.language}")
    
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
        """Generate career recommendations using rule-based filtering and Gemini LLM enhancement."""
        stream = self.profile.get("stream")
        logger.info(f"Generating recommendations for stream: {stream}")
        if not stream:
            logger.warning("No stream set in profile, cannot generate recommendations")
            return []
        
        # Rule-based filtering (CRITICAL: ensures stream alignment)
        logger.debug(f"Filtering careers for stream {stream} with profile: {list(self.profile.to_dict().keys())}")
        filtered_careers = self.recommender.filter_careers(stream, self.profile.to_dict())
        logger.info(f"Filtered {len(filtered_careers)} careers for stream {stream}")
        
        if not filtered_careers:
            logger.warning("No careers found after filtering")
            return []
        
        # Use Gemini to enhance recommendations with personalized explanations
        if not self.llm.use_gemini:
            logger.warning("Gemini not available, using rule-based formatting only")
            # Fallback to rule-based if Gemini not available
            recommendations = []
            for career in filtered_careers[:3]:
                if not StreamDetector.validate_stream_alignment(career["name"], stream, self.data):
                    logger.warning(f"Skipping invalid career: {career['name']} for stream: {stream}")
                    continue
                formatted = self.recommender.format_recommendation(career, stream, self.language)
                recommendations.append(formatted)
            logger.info(f"Generated {len(recommendations)} recommendations using rule-based formatting (Gemini unavailable)")
            return recommendations[:3]
        
        logger.info("Using Gemini to generate personalized recommendations")
        try:
            recommendations = self._generate_recommendations_with_gemini(filtered_careers, stream)
            logger.info(f"Gemini successfully generated {len(recommendations)} recommendations")
            return recommendations[:3]
        except Exception as e:
            logger.error(f"Gemini recommendation generation failed: {e}, falling back to rule-based formatting", exc_info=True)
            # Fallback to rule-based formatting if Gemini fails
            recommendations = []
            for career in filtered_careers[:3]:
                if not StreamDetector.validate_stream_alignment(career["name"], stream, self.data):
                    logger.warning(f"Skipping invalid career: {career['name']} for stream: {stream}")
                    continue
                formatted = self.recommender.format_recommendation(career, stream, self.language)
                recommendations.append(formatted)
            logger.info(f"Fallback: Generated {len(recommendations)} recommendations using rule-based formatting")
            return recommendations[:3]
    
    def _generate_recommendations_with_gemini(self, filtered_careers: List[Dict], stream: str) -> List[Dict]:
        """Use Gemini to generate personalized career recommendations."""
        # Build student profile summary for Gemini
        profile_summary = self._build_profile_summary()
        
        # Build career data for Gemini - send all available careers to give Gemini more options
        careers_info = []
        for career in filtered_careers:
            careers_info.append({
                "name": career["name"],
                "pathway": career["pathway"],
                "entrance_exams": career["entrance_exams"],
                "skills": career["skills"],
                "risks": career["risks"]
            })
        
        # Create prompt for Gemini with explicit instruction for exactly 3 recommendations
        if self.language == "mr":
            system_prompt = """तुम्ही एक करिअर मार्गदर्शन सहाय्यक आहात. तुम्हाला विद्यार्थ्याच्या प्रोफाइलवर आधारित नक्की 3 करिअर शिफारसी द्याव्या लागतील. 
प्रत्येक शिफारसीसाठी, खालील माहिती प्रदान करा:
1. करिअर नाव
2. स्ट्रीम औचित्य (का ही करिअर या स्ट्रीमशी संरेखित आहे)
3. शैक्षणिक मार्ग
4. प्रवेश परीक्षा
5. आवश्यक कौशल्ये
6. जोखीम/मर्यादा

महत्वाचे: 
- नक्की 3 करिअर शिफारसी द्या (कमी किंवा जास्त नाही)
- केवळ दिलेल्या करिअरपैकी निवड करा आणि त्यांची माहिती वापरा
- JSON स्वरूपात नक्की 3 ऑब्जेक्ट्स असलेली array द्या"""
            
            prompt = f"""विद्यार्थी प्रोफाइल:
{profile_summary}

उपलब्ध करिअर पर्याय ({stream} स्ट्रीम):
{json.dumps(careers_info, ensure_ascii=False, indent=2)}

कृपया या प्रोफाइलवर आधारित नक्की 3 सर्वोत्तम करिअर शिफारसी द्या. तुम्ही नक्की 3 करिअर निवडले पाहिजेत.

प्रत्येक शिफारसीसाठी, JSON स्वरूपात उत्तर द्या (नक्की 3 ऑब्जेक्ट्स):
[
  {{
    "name": "करिअर नाव",
    "stream_justification": "स्ट्रीम औचित्य",
    "pathway": "शैक्षणिक मार्ग",
    "entrance_exams": ["परीक्षा1", "परीक्षा2"],
    "skills": ["कौशल्य1", "कौशल्य2"],
    "risks": "जोखीम/मर्यादा"
  }},
  {{
    "name": "करिअर नाव 2",
    "stream_justification": "स्ट्रीम औचित्य",
    "pathway": "शैक्षणिक मार्ग",
    "entrance_exams": ["परीक्षा1", "परीक्षा2"],
    "skills": ["कौशल्य1", "कौशल्य2"],
    "risks": "जोखीम/मर्यादा"
  }},
  {{
    "name": "करिअर नाव 3",
    "stream_justification": "स्ट्रीम औचित्य",
    "pathway": "शैक्षणिक मार्ग",
    "entrance_exams": ["परीक्षा1", "परीक्षा2"],
    "skills": ["कौशल्य1", "कौशल्य2"],
    "risks": "जोखीम/मर्यादा"
  }}
]

केवळ JSON उत्तर द्या, कोणतीही अतिरिक्त मजकूर नाही. नक्की 3 करिअर शिफारसी असणे आवश्यक आहे."""
        else:
            system_prompt = """You are a career guidance assistant. You need to provide exactly 3 career recommendations based on the student's profile.
For each recommendation, provide:
1. Career name
2. Stream justification (why this career aligns with the stream)
3. Education pathway
4. Entrance exams
5. Required skills
6. Risks/limitations

Important: 
- Provide exactly 3 career recommendations (not less, not more)
- Only select from the provided careers and use their information
- Return a JSON array with exactly 3 objects"""
            
            prompt = f"""Student Profile:
{profile_summary}

Available Career Options ({stream} stream):
{json.dumps(careers_info, indent=2)}

Please provide exactly 3 best career recommendations based on this profile. You must select exactly 3 careers.

For each recommendation, respond in JSON format (exactly 3 objects):
[
  {{
    "name": "Career Name 1",
    "stream_justification": "Stream justification",
    "pathway": "Education pathway",
    "entrance_exams": ["Exam1", "Exam2"],
    "skills": ["Skill1", "Skill2"],
    "risks": "Risks/limitations"
  }},
  {{
    "name": "Career Name 2",
    "stream_justification": "Stream justification",
    "pathway": "Education pathway",
    "entrance_exams": ["Exam1", "Exam2"],
    "skills": ["Skill1", "Skill2"],
    "risks": "Risks/limitations"
  }},
  {{
    "name": "Career Name 3",
    "stream_justification": "Stream justification",
    "pathway": "Education pathway",
    "entrance_exams": ["Exam1", "Exam2"],
    "skills": ["Skill1", "Skill2"],
    "risks": "Risks/limitations"
  }}
]

Return ONLY JSON, no additional text. You must provide exactly 3 career recommendations."""
        
        logger.debug(f"Calling Gemini with prompt length: {len(prompt)}")
        logger.info(f"Requesting exactly 3 recommendations from Gemini for stream: {stream}")
        response_text = self.llm.generate(prompt, system_prompt)
        logger.debug(f"Gemini response received, length: {len(response_text)}")
        
        # Parse Gemini response
        recommendations = self._parse_gemini_recommendations(response_text, stream)
        logger.info(f"Gemini returned {len(recommendations)} recommendations")
        
        # Validate and ensure stream alignment
        validated_recommendations = []
        for rec in recommendations:
            # Find original career data
            original_career = None
            for career in filtered_careers:
                if career["name"].lower() == rec["name"].lower():
                    original_career = career
                    break
            
            if original_career:
                # Validate stream alignment
                if StreamDetector.validate_stream_alignment(rec["name"], stream, self.data):
                    # Use Gemini's personalized content but ensure we have all required fields
                    final_rec = {
                        "name": rec["name"],
                        "stream_justification": rec.get("stream_justification", 
                            f"This career aligns with {self.data['streams'][stream]['name']} stream."),
                        "pathway": rec.get("pathway", original_career["pathway"]),
                        "entrance_exams": rec.get("entrance_exams", original_career["entrance_exams"]),
                        "skills": rec.get("skills", original_career["skills"]),
                        "risks": rec.get("risks", original_career["risks"])
                    }
                    validated_recommendations.append(final_rec)
                    logger.info(f"Validated Gemini recommendation: {rec['name']}")
                else:
                    logger.warning(f"Gemini recommendation '{rec['name']}' failed stream validation")
            else:
                logger.warning(f"Gemini recommendation '{rec['name']}' not found in filtered careers")
        
        # Ensure we have exactly 3 recommendations
        if len(validated_recommendations) == 3:
            logger.info("Successfully received exactly 3 recommendations from Gemini")
            return validated_recommendations
        elif len(validated_recommendations) > 3:
            logger.warning(f"Gemini returned {len(validated_recommendations)} recommendations, taking first 3")
            return validated_recommendations[:3]
        else:
            # If Gemini didn't return 3 valid recommendations, fill with rule-based ones
            logger.info(f"Gemini returned {len(validated_recommendations)} valid recommendations, filling remaining with rule-based")
            used_names = [r["name"] for r in validated_recommendations]
            for career in filtered_careers:
                if career["name"] not in used_names:
                    if StreamDetector.validate_stream_alignment(career["name"], stream, self.data):
                        formatted = self.recommender.format_recommendation(career, stream, self.language)
                        validated_recommendations.append(formatted)
                        logger.info(f"Added rule-based recommendation to complete set: {career['name']}")
                        if len(validated_recommendations) >= 3:
                            break
            
            if len(validated_recommendations) < 3:
                logger.warning(f"Could only generate {len(validated_recommendations)} recommendations (target: 3)")
            
            return validated_recommendations[:3]
    
    def _build_profile_summary(self) -> str:
        """Build a summary of student profile for Gemini."""
        profile = self.profile.to_dict()
        summary_parts = []
        
        if profile.get("favourite_subjects"):
            summary_parts.append(f"Favourite Subjects: {profile['favourite_subjects']}")
        if profile.get("weak_subjects"):
            summary_parts.append(f"Weak Subjects: {profile['weak_subjects']}")
        if profile.get("marks_range"):
            summary_parts.append(f"Marks Range: {profile['marks_range']}")
        if profile.get("interests"):
            summary_parts.append(f"Interests: {profile['interests']}")
        if profile.get("stream"):
            summary_parts.append(f"Stream: {profile['stream']}")
        
        # Add stream-specific aptitude
        if profile.get("stream_aptitude"):
            summary_parts.append(f"Stream Aptitude: {json.dumps(profile['stream_aptitude'], ensure_ascii=False)}")
        
        return "\n".join(summary_parts)
    
    def _parse_gemini_recommendations(self, response_text: str, stream: str) -> List[Dict]:
        """Parse Gemini's JSON response into recommendation dictionaries."""
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Try to extract JSON array if there's extra text
            # Look for the first '[' and last ']'
            start_idx = cleaned.find('[')
            end_idx = cleaned.rfind(']')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx + 1]
            
            # Parse JSON
            recommendations = json.loads(cleaned)
            
            # Ensure it's a list
            if isinstance(recommendations, dict):
                recommendations = [recommendations]
            
            # Validate we have recommendations
            if not isinstance(recommendations, list):
                logger.error(f"Gemini response is not a list: {type(recommendations)}")
                raise ValueError("Gemini response is not a list")
            
            logger.info(f"Successfully parsed {len(recommendations)} recommendations from Gemini")
            
            # Log if we don't have exactly 3
            if len(recommendations) != 3:
                logger.warning(f"Gemini returned {len(recommendations)} recommendations instead of 3")
            
            return recommendations
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise
        except Exception as e:
            logger.error(f"Error parsing Gemini recommendations: {e}", exc_info=True)
            raise
    
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
                logger.debug(f"Processing answer for question {question['id']}: {user_input[:50]}...")
                # Store answer
                self.profile.update(question["id"], user_input)
                self.current_question_index += 1
                logger.info(f"Stored answer for question {question['id']}, moving to question index {self.current_question_index}")
                
                # Check if more general questions
                next_question = self._get_next_general_question()
                if next_question:
                    logger.debug(f"Next general question available: {next_question['id']}")
                    return self._get_question_text(next_question), False
                else:
                    # All general questions answered, detect stream
                    logger.info("All general questions answered, detecting stream")
                    self.phase = self.PHASE_STREAM_CONFIRMATION
                    detected = self.stream_detector.detect_stream(
                        self.profile.get("favourite_subjects"),
                        self.profile.get("weak_subjects"),
                        self.profile.get("interests")
                    )
                    
                    if detected:
                        logger.info(f"Stream detected: {detected}")
                        self.detected_stream = detected
                        return self._generate_stream_confirmation_prompt(detected), False
                    else:
                        logger.warning("Stream detection returned None - asking user explicitly")
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
                confirmed_stream = self.profile.get("stream")
                logger.info(f"Stream confirmed: {confirmed_stream}, moving to stream-specific questions")
                self.phase = self.PHASE_STREAM_QUESTIONS
                self.stream_questions = self._get_stream_questions(confirmed_stream)
                self.current_question_index = 0
                logger.debug(f"Loaded {len(self.stream_questions)} stream-specific questions for {confirmed_stream}")
                
                if self.stream_questions:
                    question = self.stream_questions[0]
                    logger.debug(f"First stream question: {question['id']}")
                    return self._get_question_text(question), False
                else:
                    # No stream-specific questions, move to recommendations
                    logger.info(f"No stream-specific questions for {confirmed_stream}, generating recommendations")
                    self.phase = self.PHASE_RECOMMENDATIONS
                    recommendations = self._generate_recommendations()
                    logger.info(f"Generated {len(recommendations)} recommendations")
                    response = self._format_recommendations_response(recommendations)
                    self.phase = self.PHASE_COMPLETE
                    return response, True
        
        # Phase: Stream-specific Questions
        if self.phase == self.PHASE_STREAM_QUESTIONS:
            if hasattr(self, 'stream_questions') and self.current_question_index < len(self.stream_questions):
                question = self.stream_questions[self.current_question_index]
                logger.debug(f"Processing stream question {question['id']}: {user_input[:50]}...")
                # Store answer in stream_aptitude
                if "stream_aptitude" not in self.profile.data:
                    self.profile.data["stream_aptitude"] = {}
                self.profile.data["stream_aptitude"][question["id"]] = user_input
                
                self.current_question_index += 1
                logger.info(f"Stored stream answer for {question['id']}, question {self.current_question_index}/{len(self.stream_questions)}")
                
                # Check if more stream questions
                if self.current_question_index < len(self.stream_questions):
                    next_question = self.stream_questions[self.current_question_index]
                    logger.debug(f"Next stream question: {next_question['id']}")
                    return self._get_question_text(next_question), False
                else:
                    # All questions answered, generate recommendations
                    logger.info("All stream-specific questions answered, generating recommendations")
                    self.phase = self.PHASE_RECOMMENDATIONS
                    recommendations = self._generate_recommendations()
                    logger.info(f"Generated {len(recommendations)} recommendations")
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

