# Career Guidance AI Agent

> An intelligent, bilingual career guidance system that helps Indian 12th-grade students discover the perfect career path based on their academic stream and interests.

# Demo Link of AI Agent 

## https://shivamsonawane2003.github.io/career-guidance-ai/

---

## What is This Project? (Simple Explanation)

Imagine you're a 12th-grade student in India, confused about what career to choose after school. This project is like having a smart career counselor available 24/7 on your computer or phone!

**In the simplest terms:**
- You open a website
- The AI asks you questions about your favorite subjects, interests, and marks
- Based on your answers, it figures out which stream you're in (like Science, Commerce, Arts, etc.)
- Then it gives you 3 personalized career suggestions that match your stream
- Everything works in both English and Marathi!

**Think of it like this:**
- **Frontend (frontend/)**: The beautiful website you see and interact with (HTML/CSS/JavaScript)
- **Backend (main.py)**: The brain that processes your answers and generates recommendations
- **AI Agent (career_agent/)**: The smart counselor that asks questions and gives advice
- **Data (data.json)**: The database of all careers, questions, and information

---

## How Does It Work? (Step by Step)

1. **You open the website** → The frontend (app.py) loads
2. **You select a language** → English or Marathi
3. **You answer questions** → "What are your favorite subjects?"
4. **Your answers go to the backend** → main.py receives them
5. **The AI agent processes** → agent.py figures out your stream
6. **Stream detection happens** → logic.py matches keywords to find your stream
7. **More questions are asked** → Stream-specific questions
8. **Career filtering** → logic.py finds careers matching your stream
9. **AI generates recommendations** → llm.py uses Gemini AI to personalize
10. **You get 3 career options** → Each with details about education, exams, skills

---

## Project Structure Explained

```
career_guidance_ai/
├── main.py                    # Backend server (API)
├── app.py                     # Streamlit frontend (legacy, optional)
├── frontend/                  # Modern HTML/CSS/JS frontend (NEW!)
│   ├── index.html            # Main HTML file
│   ├── style.css             # All styling
│   ├── script.js             # JavaScript logic
│   └── README.md             # Frontend documentation
├── career_agent/              # The "brain" folder
│   ├── __init__.py           # Makes it a Python package
│   ├── agent.py              # Main conversation manager
│   ├── logic.py              # Stream detection & career matching
│   ├── llm.py                # AI integration (Gemini/Ollama)
│   └── data.json             # All questions and career data
├── requirements.txt           # List of Python packages needed
├── .env                       # Your API keys (you create this)
├── DEPLOYMENT.md              # How to deploy online
└── README.md                  # This file!
```

---

### `requirements.txt` - Dependencies List

**What it does:** Lists all Python packages needed to run this project.

**Key packages:**
- `streamlit` - For the frontend website
- `fastapi` - For the backend API
- `uvicorn` - Server to run FastAPI
- `httpx` - HTTP client for making requests
- `langchain` - AI conversation management
- `google-generativeai` - Gemini AI integration
- `python-dotenv` - Load .env file
- `langdetect` - Detect language from text

---

## How Everything Works Together (Flow Diagram)

```
User opens website (app.py)
    ↓
User selects language (Marathi/English)
    ↓
User types answer
    ↓
app.py sends HTTP request to main.py
    ↓
main.py receives request
    ↓
main.py calls agent.process_input()
    ↓
agent.py processes answer
    ↓
logic.py detects stream / filters careers
    ↓
llm.py generates personalized recommendations (if needed)
    ↓
agent.py formats response
    ↓
main.py returns JSON response
    ↓
app.py displays response to user
    ↓
User sees next question or recommendations!
```

---

## Key Features Explained Simply

### 1. **Bilingual Support**
- System detects if you type in Marathi or English
- All questions and responses switch to your language
- You can manually switch using sidebar buttons

### 2. **Stream Detection**
- System looks for keywords in your answers
- Example: If you say "physics, chemistry, math" → PCM stream
- Example: If you say "biology, medical" → PCB stream

### 3. **One Question at a Time**
- System waits for your answer before asking next question
- This makes it feel like a real conversation
- No overwhelming list of questions!

### 4. **Stream-Aligned Recommendations**
- **CRITICAL**: System NEVER suggests careers outside your stream
- Example: Arts student will NEVER get Engineering recommendation
- This is enforced by rule-based filtering

### 5. **Exactly 3 Recommendations**
- System always returns exactly 3 career options
- Each has: pathway, exams, skills, risks
- Personalized using Gemini AI

---

## Quick Start (5 Minutes)

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### Step 2: Install Python

Make sure you have Python 3.8 or higher:
```bash
python --version
```

### Step 3: Setup the Project

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Add Your API Key

Create a file named `.env` in the project folder:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Step 5: Run the Application

**Terminal 1 - Start Backend:**
```bash
python main.py
```

**Terminal 2 - Start Frontend (Modern HTML/CSS/JS):**
```bash
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080` in your browser! 🎉

**Alternative - Streamlit Frontend (Legacy):**
```bash
streamlit run app.py
```
This opens at `http://localhost:8501`

---

## What Questions Will Be Asked?

### General Questions (Everyone)
1. What are your favorite subjects?
2. Which subjects do you find difficult?
3. What's your marks range?
4. What are your interests?

### Stream-Specific Questions

**For Science (PCM):**
- How comfortable are you with mathematics?
- Are you interested in engineering?

**For Science (PCB):**
- How interested are you in biology?
- Are you considering a medical career?

**For Commerce:**
- Are you interested in business?
- How comfortable are you with accounting?

**For Arts:**
- How creative are you?
- How strong are your communication skills?

**For Vocational:**
- What practical skills do you have?
- Are you interested in certifications?

---

## Supported Streams

- **PCM** (Physics, Chemistry, Mathematics) → Engineering, Architecture, Data Science
- **PCB** (Physics, Chemistry, Biology) → Medical, Pharmacy, Biotechnology
- **Commerce** → CA, Business Administration, Finance
- **Arts** → Psychology, Law, Journalism
- **Vocational** → Skill-based careers, Technical trades

---

## Troubleshooting

### "Can't connect to backend"
- Make sure `main.py` is running in Terminal 1
- Check it says "Uvicorn running on http://0.0.0.0:8000"

### "API Key Error"
- Check your `.env` file exists
- Verify API key is correct (no extra spaces)

### "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## Privacy & Safety

- **Your data stays private**: All conversations stored only in your session
- **No personal information collected**: Only academic interests
- **Disclaimer**: This is guidance, not professional counseling
- **Always verify**: Confirm decisions with certified human counselor

---

## Technical Details

**Technologies Used:**
- **FastAPI**: Modern Python web framework for backend
- **Streamlit**: Easy-to-use framework for frontend
- **LangChain**: AI conversation management
- **Google Gemini**: AI for generating recommendations
- **Rule-based filtering**: Ensures accuracy

---

## Important Notes

1. **This is guidance, not a decision**: Always consult a real career counselor
2. **Stream alignment is strict**: Never suggests careers outside your stream
3. **Exactly 3 recommendations**: Always 3 options, no more, no less
4. **One question at a time**: Waits for your answer before proceeding

---

## Deployment

Want to share this online? See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step guide to deploy on Streamlit Cloud.

---

**Made for Indian students**

*Remember: Your career is a journey, not a destination. Take your time, explore your options, and always seek guidance from experienced professionals.*
