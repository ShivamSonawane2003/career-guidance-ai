# Quick Start Guide - Frontend

## Running the Frontend

### Step 1: Start the Backend

In the project root directory:
```bash
python main.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Start the Frontend Server

In the `frontend` directory:
```bash
cd frontend
python -m http.server 8080
```

### Step 3: Open in Browser

Open: `http://localhost:8080`

## Testing Checklist

- [ ] Backend is running (check Terminal 1)
- [ ] Frontend server is running (check Terminal 2)
- [ ] Browser opens without errors
- [ ] Can click "Start Conversation"
- [ ] First question appears
- [ ] Can type and send answers
- [ ] Question counter updates
- [ ] Can switch language (English/Marathi)
- [ ] Can create new chat
- [ ] Chat history appears in sidebar
- [ ] Can switch between chats
- [ ] Recommendations appear at the end (3 careers)
- [ ] Voice input works (if browser supports)

## Troubleshooting

### Frontend shows "Cannot connect to backend"
- Check backend is running on port 8000
- Check `API_BASE_URL` in `script.js` matches your backend URL
- Check browser console for CORS errors

### Chat history not saving
- Check browser allows localStorage
- Try clearing browser cache
- Check browser console for errors

### Questions not appearing
- Check backend logs for errors
- Verify API endpoint is working: `http://localhost:8000/health`
- Check browser console for API errors

