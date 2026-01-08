# Career Guidance AI - Frontend

Modern HTML/CSS/JavaScript frontend for the Career Guidance AI application.

## Quick Start

### Option 1: Using Python HTTP Server (Recommended)

1. Open terminal in the `frontend` directory
2. Run:
   ```bash
   # Python 3
   python -m http.server 8080
   
   # Or Python 2
   python -m SimpleHTTPServer 8080
   ```
3. Open browser: `http://localhost:8080`

### Option 2: Using Live Server (VS Code Extension)

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### Option 3: Direct File Open

1. Simply open `index.html` in your browser
2. Note: Some features may be limited due to CORS

## Configuration

Update the API URL in `script.js` if your backend runs on a different port:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // Change this if needed
    // ...
};
```

## Features

- ✅ Modern chatbot UI (ChatGPT-style)
- ✅ Chat history sidebar (last 10 chats)
- ✅ Session management with localStorage
- ✅ Bilingual support (English/Marathi)
- ✅ Voice input (if browser supports)
- ✅ Question counter (Question X of 9)
- ✅ Responsive design
- ✅ Loading indicators
- ✅ Smooth animations

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # All styling
├── script.js       # JavaScript logic
└── README.md       # This file
```

## Browser Compatibility

- Chrome/Edge: Full support (including voice input)
- Firefox: Full support (voice input may vary)
- Safari: Full support (voice input may vary)
- Mobile browsers: Responsive design supported

## Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running: `python main.py`
- Check backend URL in `script.js`
- Verify CORS settings in `main.py`

### "Voice input not working"
- Voice input requires HTTPS or localhost
- Some browsers may not support it
- Falls back to text input automatically

### "Chat history not saving"
- Check browser localStorage is enabled
- Clear browser cache if issues persist

