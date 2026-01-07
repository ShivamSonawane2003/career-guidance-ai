# Career Guidance AI Agent

> An intelligent, bilingual career guidance system that helps Indian 12th-grade students discover the perfect career path based on their academic stream and interests.

## What is This?

This is an AI-powered career guidance assistant that talks to students in **Marathi or English** (automatically detects your language!) and helps them find the right career options. It's designed specifically for Indian students who have just completed or are about to complete their 12th grade.

### What Makes It Special?

- **Smart AI Assistant**: Uses Google's Gemini AI to provide personalized career recommendations
- **Bilingual Support**: Automatically understands and responds in Marathi or English
- **Stream-Specific**: Only suggests careers that match your academic stream (PCM, PCB, Commerce, Arts, or Vocational)
- **Conversational**: Asks you questions one at a time, just like talking to a real counselor
- **Accurate**: Uses smart rules to ensure you never get wrong career suggestions
- **Easy to Use**: Beautiful web interface that works on any device

##  Who Is This For?

- **12th-grade students** in India who are confused about their career path
- **Parents** who want to help their children make informed decisions
- **Teachers and counselors** who want to provide additional guidance to students
- **Anyone** interested in understanding Indian higher education pathways

## Quick Start (5 Minutes)

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (you'll need it in Step 3)

### Step 2: Install Python

Make sure you have Python 3.8 or higher installed. Check by running:
```bash
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/)

### Step 3: Setup the Project

**Windows:**
```bash
# Create a virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install everything needed
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install everything needed
pip install -r requirements.txt
```

### Step 4: Add Your API Key

Create a file named `.env` in the project folder and add:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Replace `your_api_key_here` with the key you got from Step 1.

### Step 5: Run the Application

Open **two terminal windows**:

**Terminal 1 - Start the Backend:**
```bash
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Start the Frontend:**
```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501` and you're ready to go! 🎉

## How to Use

1. **Start a Conversation**: The AI will greet you and ask about your favorite subjects
2. **Answer Questions**: Just type your answers naturally - in Marathi or English!
3. **Get Recommendations**: After answering a few questions, you'll get 3 personalized career suggestions
4. **Review Details**: Each recommendation includes:
   - Why it matches your stream
   - Education pathway (what courses to take)
   - Entrance exams you need to prepare for
   - Skills you'll need
   - Things to consider

## What Questions Will Be Asked?

### General Questions (Everyone)
- What are your favorite subjects?
- Which subjects do you find difficult?
- What's your marks range?
- What are your interests?

### Stream-Specific Questions (After stream is detected)

**For Science (PCM) students:**
- How comfortable are you with mathematics?
- Are you interested in engineering?

**For Science (PCB) students:**
- How interested are you in biology?
- Are you considering a medical career?

**For Commerce students:**
- Are you interested in business?
- How comfortable are you with accounting?

**For Arts students:**
- How creative are you?
- How strong are your communication skills?

**For Vocational students:**
- What practical skills do you have?
- Are you interested in certifications?

## Supported Streams

The system supports all major Indian academic streams:

- **PCM** (Physics, Chemistry, Mathematics) - Engineering, Architecture, Data Science
- **PCB** (Physics, Chemistry, Biology) - Medical, Pharmacy, Biotechnology
- **Commerce** - CA, Business Administration, Finance
- **Arts** - Psychology, Law, Journalism
- **Vocational** - Skill-based careers, Technical trades

## Troubleshooting

### "Can't connect to backend"
- Make sure you started `main.py` in Terminal 1
- Check that it says "Uvicorn running on http://0.0.0.0:8000"
- Wait a few seconds and try again

### "API Key Error"
- Double-check your `.env` file exists
- Make sure the API key is correct (no extra spaces)
- Verify your Gemini API key is active at [Google AI Studio](https://makersuite.google.com/app/apikey)

### "Module not found" errors
- Make sure your virtual environment is activated (you should see `(venv)` in your terminal)
- Run `pip install -r requirements.txt` again

### The app is slow
- This is normal! The AI needs a few seconds to think and generate recommendations
- Make sure you have a good internet connection (for Gemini API calls)

## Project Structure (Simple Version)

```
career_guidance_ai/
├── main.py              # Backend server (handles AI logic)
├── app.py               # Frontend interface (what you see)
├── career_agent/        # The "brain" of the system
│   ├── agent.py        # Conversation manager
│   ├── logic.py        # Stream detection & career matching
│   ├── llm.py          # AI integration (Gemini)
│   └── data.json       # Career database
├── requirements.txt     # List of needed packages
└── .env                # Your API key (create this!)
```

## Privacy & Safety

- **Your data stays private**: All conversations are stored only in your session
- **No personal information collected**: We only ask about your academic interests
- **Disclaimer**: This is a guidance tool, not a replacement for professional counseling
- **Always verify**: Please confirm any career decisions with a certified human counselor

## Deployment (Making It Available Online)

Want to share this with others? We have detailed guides:

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Deploy to Streamlit Cloud (easiest, free)
- **[DEPLOYMENT_UBUNTU.md](DEPLOYMENT_UBUNTU.md)**: Deploy on your own server (more control)

## Technical Details (For Developers)

If you want to understand how everything works under the hood, check out the detailed documentation in the code comments. The system uses:

- **FastAPI**: Modern Python web framework for the backend
- **Streamlit**: Easy-to-use framework for the frontend
- **LangChain**: For managing AI conversations
- **Google Gemini**: For generating intelligent responses
- **Rule-based filtering**: Ensures accuracy and stream alignment

## Important Notes

1. **This is guidance, not a decision**: Always consult with a real career counselor before making final choices
2. **Stream alignment is strict**: The system will never suggest careers outside your stream (this is by design!)
3. **Exactly 3 recommendations**: You'll always get 3 career options, no more, no less
4. **One question at a time**: The AI waits for your answer before asking the next question

## Need Help?

- Check the troubleshooting section above
- Review the deployment guides ([DEPLOYMENT.md](DEPLOYMENT.md)) if you want to host it online
- Check the code comments for technical implementation details
- Open an issue on GitHub if you find a bug

## Ready to Start?

1. Follow the Quick Start guide above
2. Start both terminals
3. Open your browser
4. Begin your career journey!

---

**Made for Indian students**

*Remember: Your career is a journey, not a destination. Take your time, explore your options, and always seek guidance from experienced professionals.*
