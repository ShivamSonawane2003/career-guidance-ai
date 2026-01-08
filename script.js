// ============================================
// Career Guidance AI - Frontend JavaScript
// ============================================

// ============================================
// Configuration
// ============================================
// Update API_BASE_URL if your backend runs on a different port or domain
const CONFIG = {
    API_BASE_URL: 'https://career-guidance-ai-xo2g.onrender.com',  // Change this if backend is on different URL
    MAX_CHAT_HISTORY: 10,                     // Maximum number of chat sessions to store
    STORAGE_KEY_CHATS: 'career_guidance_chats',  // localStorage key for chat history
    STORAGE_KEY_CURRENT: 'career_guidance_current_session'  // localStorage key for current session
};

// Global State
const state = {
    currentSessionId: null,
    currentLanguage: 'en',
    messages: [],
    questionCount: 0,
    isComplete: false,
    isProcessing: false,
    chatHistory: []
};

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    chatHistory: document.getElementById('chatHistory'),
    chatContainer: document.getElementById('chatContainer'),
    welcomeMessage: document.getElementById('welcomeMessage'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    micBtn: document.getElementById('micBtn'),
    newChatBtn: document.getElementById('newChatBtn'),
    restartBtn: document.getElementById('restartBtn'),
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    startBtn: document.getElementById('startBtn'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    questionCounter: document.getElementById('questionCounter'),
    currentQuestion: document.getElementById('currentQuestion'),
    questionLabel: document.getElementById('questionLabel'),
    langEn: document.getElementById('langEn'),
    langMr: document.getElementById('langMr')
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadChatHistory();
});

function initializeApp() {
    // Set initial language based on browser preference
    const browserLang = navigator.language || navigator.userLanguage || 'en';
    const initialLang = browserLang.startsWith('mr') ? 'mr' : 'en';
    setLanguage(initialLang);
    
    // Load current session from storage
    const savedSession = localStorage.getItem(CONFIG.STORAGE_KEY_CURRENT);
    if (savedSession) {
        try {
            const sessionData = JSON.parse(savedSession);
            state.currentSessionId = sessionData.sessionId;
            state.messages = sessionData.messages || [];
            state.questionCount = sessionData.questionCount || 0;
            state.currentLanguage = sessionData.language || initialLang;
            state.isComplete = sessionData.isComplete || false;
            
            // Restore UI
            restoreChatUI();
            updateLanguageButtons();
            setLanguage(state.currentLanguage);
        } catch (error) {
            console.error('Error parsing saved session:', error);
            // Remove corrupted entry
            localStorage.removeItem(CONFIG.STORAGE_KEY_CURRENT);
            // Use defaults
            state.currentLanguage = initialLang;
            setLanguage(initialLang);
            showWelcomeMessage();
        }
    } else {
        // New session
        showWelcomeMessage();
    }
    
    // Check for audio support
    checkAudioSupport();
    
    // Initialize theme
    initializeTheme();
}

function setupEventListeners() {
    // Send button
    elements.sendBtn.addEventListener('click', handleSendMessage);
    
    // Enter key in input
    elements.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // New chat button
    elements.newChatBtn.addEventListener('click', createNewChat);
    
    // Restart button
    elements.restartBtn.addEventListener('click', restartConversation);
    
    // Start button
    elements.startBtn.addEventListener('click', async () => {
        // Disable button during initialization
        elements.startBtn.disabled = true;
        try {
            await sendInitialMessage('hello');
            // Focus input after starting conversation
            setTimeout(() => {
                elements.messageInput.focus();
            }, 100);
        } catch (error) {
            console.error('Error starting conversation:', error);
        } finally {
            elements.startBtn.disabled = false;
        }
    });
    
    // Language buttons
    elements.langEn.addEventListener('click', () => switchLanguage('en'));
    elements.langMr.addEventListener('click', () => switchLanguage('mr'));
    
    // Microphone button
    elements.micBtn.addEventListener('click', handleVoiceInput);
    
    // Theme toggle button
    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleDarkMode);
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.chat-history-menu') && !e.target.closest('.chat-history-menu-btn')) {
            document.querySelectorAll('.chat-history-menu').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
}

// ============================================
// Chat History Management
// ============================================

function loadChatHistory() {
    const saved = localStorage.getItem(CONFIG.STORAGE_KEY_CHATS);
    if (saved) {
        try {
            state.chatHistory = JSON.parse(saved);
        } catch (error) {
            console.error('Error parsing chat history:', error);
            // Clear corrupted entry
            localStorage.removeItem(CONFIG.STORAGE_KEY_CHATS);
            state.chatHistory = [];
        }
    }
    renderChatHistory();
}

function saveChatHistory() {
    // Keep only last MAX_CHAT_HISTORY chats
    if (state.chatHistory.length > CONFIG.MAX_CHAT_HISTORY) {
        state.chatHistory = state.chatHistory.slice(-CONFIG.MAX_CHAT_HISTORY);
    }
    localStorage.setItem(CONFIG.STORAGE_KEY_CHATS, JSON.stringify(state.chatHistory));
    renderChatHistory();
}

function addToChatHistory(sessionId, title) {
    // Remove if already exists
    state.chatHistory = state.chatHistory.filter(chat => chat.sessionId !== sessionId);
    
    // Add to beginning with full conversation data
    state.chatHistory.unshift({
        sessionId,
        title,
        timestamp: new Date().toISOString(),
        messageCount: state.messages.length,
        messages: [...state.messages], // Store full message history
        questionCount: state.questionCount,
        language: state.currentLanguage,
        isComplete: state.isComplete
    });
    
    saveChatHistory();
}

function renderChatHistory() {
    elements.chatHistory.innerHTML = '';
    
    if (state.chatHistory.length === 0) {
        elements.chatHistory.innerHTML = '<div style="padding: 1rem; text-align: center; color: #718096; font-size: 0.875rem;">No chat history yet</div>';
        return;
    }
    
    state.chatHistory.forEach(chat => {
        const item = document.createElement('div');
        item.className = 'chat-history-item';
        if (chat.sessionId === state.currentSessionId) {
            item.classList.add('active');
        }
        
        // Create content wrapper
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'chat-history-item-content';
        contentWrapper.style.flex = '1';
        
        const title = document.createElement('div');
        title.className = 'chat-history-item-title';
        title.textContent = chat.title;
        
        const time = document.createElement('div');
        time.className = 'chat-history-item-time';
        time.textContent = formatTimestamp(chat.timestamp);
        
        contentWrapper.appendChild(title);
        contentWrapper.appendChild(time);
        
        // Create three dots menu button
        const menuBtn = document.createElement('button');
        menuBtn.className = 'chat-history-menu-btn';
        menuBtn.innerHTML = '⋯';
        menuBtn.title = 'More options';
        menuBtn.onclick = (e) => {
            e.stopPropagation();
            toggleChatMenu(chat.sessionId, menuBtn);
        };
        
        // Create dropdown menu
        const menu = document.createElement('div');
        menu.className = 'chat-history-menu';
        menu.id = `menu-${chat.sessionId}`;
        menu.style.display = 'none';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-history-menu-item';
        deleteBtn.innerHTML = '🗑️ Delete';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteChat(chat.sessionId);
            menu.style.display = 'none';
        };
        
        menu.appendChild(deleteBtn);
        
        item.appendChild(contentWrapper);
        item.appendChild(menuBtn);
        item.appendChild(menu);
        
        // Click on item (not menu) loads chat
        contentWrapper.addEventListener('click', () => loadChatSession(chat.sessionId));
        
        elements.chatHistory.appendChild(item);
    });
}

function toggleChatMenu(sessionId, button) {
    // Close all other menus
    document.querySelectorAll('.chat-history-menu').forEach(menu => {
        if (menu.id !== `menu-${sessionId}`) {
            menu.style.display = 'none';
        }
    });
    
    // Toggle current menu
    const menu = document.getElementById(`menu-${sessionId}`);
    if (menu) {
        const isVisible = menu.style.display === 'block';
        menu.style.display = isVisible ? 'none' : 'block';
        
        // Add click-outside handler if menu is now visible
        if (!isVisible) {
            setTimeout(() => {
                const closeMenu = (e) => {
                    if (!menu.contains(e.target) && !button.contains(e.target)) {
                        menu.style.display = 'none';
                        document.removeEventListener('click', closeMenu);
                    }
                };
                document.addEventListener('click', closeMenu);
            }, 0);
        }
    }
}

function deleteChat(sessionId) {
    if (!confirm('Are you sure you want to delete this chat?')) {
        return;
    }
    
    // Remove from history
    state.chatHistory = state.chatHistory.filter(chat => chat.sessionId !== sessionId);
    saveChatHistory();
    
    // If deleted chat was current, create new chat
    if (state.currentSessionId === sessionId) {
        createNewChat();
    }
    
    renderChatHistory();
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

function generateChatTitle() {
    // Try to get name from messages (first user message should be name)
    if (state.messages.length > 0) {
        // Find the first user message that's not "hello"
        const nameMessage = state.messages.find(m => 
            m.role === 'user' && 
            m.content.toLowerCase().trim() !== 'hello' &&
            m.content.trim().length > 0
        );
        if (nameMessage) {
            const name = nameMessage.content.trim();
            // Use name as title if it's reasonable length
            if (name.length > 0 && name.length < 30) {
                return `${name}'s Career Chat`;
            }
        }
    }
    return 'New Career Chat';
}

// ============================================
// Session Management
// ============================================

function generateSessionId() {
    // Generate a simple UUID v4-like ID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function createNewChat() {
    // Save current chat if exists and has messages
    if (state.currentSessionId && state.messages.length > 0) {
        const title = generateChatTitle();
        addToChatHistory(state.currentSessionId, title);
    }
    
    // Generate new session ID immediately
    const newSessionId = generateSessionId();
    
    // Reset state completely
    state.currentSessionId = newSessionId;
    state.messages = [];
    state.questionCount = 0;
    state.isComplete = false;
    
    // Save new session to storage
    saveCurrentSession();
    
    // Add new chat to sidebar immediately
    const newChatTitle = 'New Career Chat';
    addToChatHistory(newSessionId, newChatTitle);
    
    // Reset UI
    showWelcomeMessage();
    updateUIState();
    renderChatHistory();
}

function loadChatSession(sessionId) {
    // Find chat in history
    const chat = state.chatHistory.find(c => c.sessionId === sessionId);
    if (!chat) return;
    
    // Save current chat before switching
    if (state.currentSessionId && state.currentSessionId !== sessionId && state.messages.length > 0) {
        const title = generateChatTitle();
        addToChatHistory(state.currentSessionId, title);
    }
    
    // Move selected chat to top of list
    state.chatHistory = state.chatHistory.filter(c => c.sessionId !== sessionId);
    chat.timestamp = new Date().toISOString();
    state.chatHistory.unshift(chat);
    saveChatHistory();
    
    // Load from chat history first (has full message history)
    if (chat.messages && chat.messages.length > 0) {
        state.currentSessionId = sessionId;
        state.messages = [...chat.messages];
        state.questionCount = chat.questionCount || 0;
        // Restore the language that was used for this chat session
        state.currentLanguage = chat.language || 'en';
        state.isComplete = chat.isComplete || false;
        
        // Update HTML lang attribute to match the chat's language
        setLanguage(state.currentLanguage);
        
        // Update localStorage
        saveCurrentSession();
        
        // Restore UI
        restoreChatUI();
        updateLanguageButtons();
        updateQuestionCounter();
        updateUIState();
        renderChatHistory();
        return;
    } else {
        // Empty chat - show welcome message
        state.currentSessionId = sessionId;
        state.messages = [];
        state.questionCount = 0;
        state.currentLanguage = chat.language || state.currentLanguage || 'en';
        state.isComplete = false;
        
        setLanguage(state.currentLanguage);
        saveCurrentSession();
        showWelcomeMessage();
        updateLanguageButtons();
        updateQuestionCounter();
        updateUIState();
        renderChatHistory();
        return;
    }
    
    // Fallback: Load session from storage if available
    const savedSession = localStorage.getItem(CONFIG.STORAGE_KEY_CURRENT);
    if (savedSession) {
        try {
            const sessionData = JSON.parse(savedSession);
            if (sessionData.sessionId === sessionId) {
                // Restore this session
                state.currentSessionId = sessionId;
                state.messages = sessionData.messages || [];
                state.questionCount = sessionData.questionCount || 0;
                state.currentLanguage = sessionData.language || 'en';
                state.isComplete = sessionData.isComplete || false;
                
                setLanguage(state.currentLanguage);
                
                if (state.messages.length > 0) {
                    restoreChatUI();
                } else {
                    showWelcomeMessage();
                }
                updateLanguageButtons();
                updateQuestionCounter();
                updateUIState();
                renderChatHistory();
                return;
            }
        } catch (error) {
            console.error('Error parsing saved session in loadChatSession:', error);
            // Remove corrupted entry
            localStorage.removeItem(CONFIG.STORAGE_KEY_CURRENT);
        }
    }
    
    // If no history found, this is a new session - don't try to load old one
    // Just create a fresh session
    createNewChat();
}

function saveCurrentSession() {
    if (!state.currentSessionId) return;
    
    const sessionData = {
        sessionId: state.currentSessionId,
        messages: state.messages,
        questionCount: state.questionCount,
        language: state.currentLanguage,
        isComplete: state.isComplete
    };
    
    localStorage.setItem(CONFIG.STORAGE_KEY_CURRENT, JSON.stringify(sessionData));
}

// ============================================
// API Communication
// ============================================

async function sendMessage(message, showUserMessage = true) {
    if (state.isProcessing || !message.trim()) return;
    
    state.isProcessing = true;
    updateUIState();
    
    // Add user message to UI only if requested (don't show "hello" automatically)
    if (showUserMessage) {
        addMessageToUI('user', message);
    }
    // Store message with its language
    state.messages.push({ 
        role: 'user', 
        content: message,
        language: state.currentLanguage 
    });
    
    // Clear input
    elements.messageInput.value = '';
    
    // Show loading immediately
    elements.loadingIndicator.style.display = 'block';
    scrollToBottom();
    
    try {
        // Add 1 second delay before fetching (loader will be visible)
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: state.currentSessionId,
                language: state.currentLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID if new
        if (data.session_id && !state.currentSessionId) {
            state.currentSessionId = data.session_id;
        }
        
        // If this is the final recommendation (complete response), show loader before displaying
        if (data.complete) {
            // Keep loader visible for recommendations with delay
            elements.loadingIndicator.style.display = 'block';
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Check if response is empty or error
        if (!data.response || data.response.trim() === '') {
            console.error('Empty response from backend');
            const errorMsg = 'Sorry, I received an empty response. Please try again.';
            addMessageToUI('assistant', errorMsg);
            state.messages.push({ 
                role: 'assistant', 
                content: errorMsg,
                language: state.currentLanguage 
            });
        } else {
            // Add bot response
            addMessageToUI('assistant', data.response);
            // Store message with its language
            state.messages.push({ 
                role: 'assistant', 
                content: data.response,
                language: state.currentLanguage 
            });
        }
        
        // Update question count - extract from bot response if available
        if (!data.complete) {
            // Try to extract question number from response (format: "1 of 9 question:")
            let match = data.response.match(/(\d+)\s+of\s+(\d+)\s+question:/i);
            if (match) {
                state.questionCount = parseInt(match[1]);
            } else {
                // Fallback: count assistant messages
                const assistantCount = state.messages.filter(m => m.role === 'assistant').length;
                if (assistantCount > 0) {
                    state.questionCount++;
                }
            }
        } else {
            state.isComplete = true;
            // Save to chat history when complete
            const title = generateChatTitle();
            addToChatHistory(state.currentSessionId, title);
        }
        
        // Save session to localStorage
        saveCurrentSession();
        
        // Also update chat history if session already exists in history
        const existingChatIndex = state.chatHistory.findIndex(c => c.sessionId === state.currentSessionId);
        if (existingChatIndex !== -1) {
            // Update existing chat with latest data
            state.chatHistory[existingChatIndex].messages = [...state.messages];
            state.chatHistory[existingChatIndex].questionCount = state.questionCount;
            state.chatHistory[existingChatIndex].language = state.currentLanguage;
            state.chatHistory[existingChatIndex].isComplete = state.isComplete;
            saveChatHistory();
        }
        
        // Update UI
        updateQuestionCounter();
        updateUIState();
        
    } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = 'Sorry, I encountered an error. Please try again.';
        addMessageToUI('assistant', errorMessage);
        state.messages.push({ 
            role: 'assistant', 
            content: errorMessage,
            language: state.currentLanguage 
        });
    } finally {
        state.isProcessing = false;
        elements.loadingIndicator.style.display = 'none';
        updateUIState(); // Re-enable input after processing (includes focus)
        scrollToBottom();
    }
}

async function sendInitialMessage(message) {
    // Hide welcome message
    if (elements.welcomeMessage) {
        elements.welcomeMessage.style.display = 'none';
    }
    
    // Clear only chat messages, preserve welcome message element
    const messages = elements.chatContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
    
    // Send message without showing it in UI (silent "hello")
    await sendMessage(message, false);
}

async function restartConversation() {
    if (!state.currentSessionId) return;
    
    if (!confirm('Are you sure you want to restart this conversation?')) {
        return;
    }
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/restart`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: state.currentSessionId
            })
        });
        
        if (response.ok) {
            // Reset state
            state.messages = [];
            state.questionCount = 0;
            state.isComplete = false;
            
            // Clear only chat messages, preserve welcome message element
            const messages = elements.chatContainer.querySelectorAll('.message');
            messages.forEach(msg => msg.remove());
            // Hide welcome message if it exists
            if (elements.welcomeMessage) {
                elements.welcomeMessage.style.display = 'none';
            }
            
            // Start fresh
            await sendInitialMessage('hello');
        }
    } catch (error) {
        console.error('Error restarting conversation:', error);
        alert('Failed to restart conversation. Please try again.');
    }
}

// ============================================
// UI Updates
// ============================================

function addMessageToUI(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Convert markdown-like formatting to HTML
    contentDiv.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(contentDiv);
    elements.chatContainer.appendChild(messageDiv);
    
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessage(text) {
    // First escape HTML entities to prevent XSS
    let html = escapeHtml(text);
    
    // Then convert markdown-style formatting to HTML
    html = html
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Line breaks
        .replace(/\n/g, '<br>')
        // Numbered lists (basic)
        .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // Bullet points
        .replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
    
    // Wrap lists
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return html;
}

function showWelcomeMessage() {
    // Clear only the chat messages, but preserve the welcome message element
    // Remove all message divs but keep the welcome message
    const messages = elements.chatContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
    
    // Show welcome message
    if (elements.welcomeMessage) {
        elements.welcomeMessage.style.display = 'block';
    } else {
        // If welcome message was removed, recreate it
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.id = 'welcomeMessage';
        welcomeDiv.innerHTML = `
            <div class="welcome-icon">🎓</div>
            <h2>Welcome to Career Guidance AI!</h2>
            <p>I'll help you discover the perfect career path based on your academic stream and interests.</p>
            <p>Let's start by answering a few questions. Type "hello" or click the button below to begin.</p>
            <button class="btn-start" id="startBtn">Start Conversation</button>
        `;
        elements.chatContainer.appendChild(welcomeDiv);
        // Re-attach event listener
        const startBtn = welcomeDiv.querySelector('#startBtn');
        if (startBtn) {
            startBtn.addEventListener('click', async () => {
                startBtn.disabled = true;
                try {
                    await sendInitialMessage('hello');
                    setTimeout(() => {
                        elements.messageInput.focus();
                    }, 100);
                } catch (error) {
                    console.error('Error starting conversation:', error);
                } finally {
                    startBtn.disabled = false;
                }
            });
        }
        // Update elements reference
        elements.welcomeMessage = welcomeDiv;
        elements.startBtn = startBtn;
    }
    
    elements.questionCounter.style.display = 'none';
}

function restoreChatUI() {
    // Hide welcome message
    if (elements.welcomeMessage) {
        elements.welcomeMessage.style.display = 'none';
    }
    
    // Clear only chat messages, preserve welcome message element
    const messages = elements.chatContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
    
    // Restore all messages (skip silent "hello" messages)
    // Messages are displayed in their original language, not current language
    state.messages.forEach((msg, index) => {
        // Show user messages (but skip the first "hello" if it's the first message)
        if (msg.role === 'user') {
            // Only skip if it's the very first message and it's "hello"
            const isFirstMessage = index === 0;
            const isHello = msg.content.toLowerCase().trim() === 'hello';
            if (isFirstMessage && isHello) {
                // Skip silent hello
            } else {
                // Display message in its original language (stored with message)
                addMessageToUI('user', msg.content);
            }
        } else if (msg.role === 'assistant' || msg.role === 'bot') {
            // Display message in its original language (stored with message)
            // Support both 'assistant' and legacy 'bot' roles for backward compatibility
            addMessageToUI('assistant', msg.content);
        }
    });
    
    updateQuestionCounter();
    scrollToBottom();
}

function updateQuestionCounter(count) {
    if (state.isComplete) {
        elements.questionCounter.style.display = 'none';
        return;
    }
    
    let questionCount = count;
    
    // If count not provided, extract from bot's last message
    if (questionCount === undefined) {
        const lastBotMessage = [...state.messages].reverse().find(m => m.role === 'assistant');
        if (lastBotMessage && lastBotMessage.content) {
            // Try new format first: [X/Y]
            let match = lastBotMessage.content.match(/\[(\d+)\/(\d+)\]/);
            if (!match) {
                // Fallback to old format: X of Y question: or X पैकी Y प्रश्न:
                match = lastBotMessage.content.match(/(\d+)\s+(?:of|पैकी)\s+(\d+)\s+(?:question|प्रश्न):/i);
            }
            if (match) {
                questionCount = parseInt(match[1]);
            }
        }
        
        // Fallback: use state.questionCount if available
        if (questionCount === undefined && state.questionCount > 0) {
            questionCount = state.questionCount;
        }
    }
    
    if (questionCount && questionCount > 0) {
        elements.questionCounter.style.display = 'block';
        elements.currentQuestion.textContent = questionCount;
        // Handle pluralization
        if (elements.questionLabel) {
            elements.questionLabel.textContent = questionCount === 1 ? 'question' : 'questions';
        }
    } else {
        elements.questionCounter.style.display = 'none';
    }
}

function updateUIState() {
    // Disable/enable input during processing
    const shouldDisable = state.isProcessing || state.isComplete;
    elements.messageInput.disabled = shouldDisable;
    elements.sendBtn.disabled = shouldDisable;
    
    // Ensure input is not readonly
    elements.messageInput.readOnly = false;
    
    // Update placeholder
    if (state.isComplete) {
        elements.messageInput.placeholder = 'Conversation complete! Start a new chat to continue.';
    } else {
        elements.messageInput.placeholder = state.currentLanguage === 'mr' 
            ? 'तुमचा संदेश येथे टाइप करा...' 
            : 'Type your message here...';
    }
    
    // Focus input if not disabled and not already focused
    if (!shouldDisable && document.activeElement !== elements.messageInput) {
        setTimeout(() => {
            elements.messageInput.focus();
        }, 100);
    }
}

function scrollToBottom() {
    setTimeout(() => {
        elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    }, 100);
}

// ============================================
// Language Switching
// ============================================

function setLanguage(lang) {
    // Update HTML lang attribute for screen readers
    const htmlRoot = document.getElementById('htmlRoot') || document.documentElement;
    if (htmlRoot) {
        htmlRoot.setAttribute('lang', lang);
    }
}

function switchLanguage(lang) {
    if (state.currentLanguage === lang) return;
    
    state.currentLanguage = lang;
    setLanguage(lang);
    updateLanguageButtons();
    updateUIState();
    saveCurrentSession();
    
    // If conversation started, send language preference with next message
    // (Language will be sent with each API call)
}

function updateLanguageButtons() {
    if (state.currentLanguage === 'en') {
        elements.langEn.classList.add('active');
        elements.langMr.classList.remove('active');
    } else {
        elements.langMr.classList.add('active');
        elements.langEn.classList.remove('active');
    }
}

// ============================================
// Voice Input (Optional)
// ============================================

let recognition = null;
let isRecording = false;

function checkAudioSupport() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        initializeRecognition();
        elements.micBtn.style.display = 'block';
    } else {
        elements.micBtn.style.display = 'none';
    }
}

function initializeRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true; // Enable real-time transcription
    recognition.lang = state.currentLanguage === 'mr' ? 'mr-IN' : 'en-IN';
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show interim results in real-time
        if (interimTranscript) {
            elements.messageInput.value = finalTranscript + interimTranscript;
        } else if (finalTranscript) {
            elements.messageInput.value = finalTranscript;
        }
        
        // If we have a final result, send the message
        if (finalTranscript) {
            stopRecording();
            handleSendMessage();
        }
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopRecording();
        
        // Don't show alert for recoverable errors
        if (event.error === 'no-speech') {
            // User didn't speak, silently fail
            return;
        } else if (event.error === 'aborted') {
            // User or system aborted, silently fail
            return;
        } else if (event.error === 'network') {
            alert('Network error. Please check your connection and try again.');
        } else if (event.error === 'not-allowed') {
            alert('Microphone permission denied. Please allow microphone access and try again.');
        } else {
            // For other errors, try to reinitialize
            setTimeout(() => {
                initializeRecognition();
            }, 100);
        }
    };
    
    recognition.onend = () => {
        stopRecording();
    };
}

function handleVoiceInput() {
    if (!recognition) {
        alert('Voice input is not supported in your browser. Please type your message.');
        return;
    }
    
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    if (state.isProcessing) return;
    
    // Reinitialize if recognition is null or in bad state
    if (!recognition) {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            initializeRecognition();
        } else {
            alert('Voice input is not supported in your browser. Please type your message.');
            return;
        }
    }
    
    try {
        recognition.lang = state.currentLanguage === 'mr' ? 'mr-IN' : 'en-IN';
        recognition.start();
        isRecording = true;
        // Transform mic icon to cancel button
        elements.micBtn.innerHTML = '✕';
        elements.micBtn.classList.add('recording');
        elements.micBtn.title = 'Stop recording';
        // Clear input to show new transcription
        elements.messageInput.value = '';
    } catch (error) {
        console.error('Error starting recognition:', error);
        // If start fails, reinitialize and try again once
        if (error.name === 'InvalidStateError' || error.message.includes('start')) {
            initializeRecognition();
            try {
                recognition.start();
                isRecording = true;
                elements.micBtn.innerHTML = '✕';
                elements.micBtn.classList.add('recording');
                elements.micBtn.title = 'Stop recording';
                elements.messageInput.value = '';
            } catch (retryError) {
                console.error('Error on retry:', retryError);
                stopRecording();
            }
        } else {
            stopRecording();
        }
    }
}

function stopRecording() {
    if (recognition && isRecording) {
        try {
            recognition.stop();
        } catch (error) {
            // Ignore errors when stopping
            console.log('Error stopping recognition:', error);
        }
    }
    isRecording = false;
    // Transform cancel button back to mic icon
    elements.micBtn.innerHTML = '🎤';
    elements.micBtn.classList.remove('recording');
    elements.micBtn.title = 'Voice Input (if supported)';
}

// ============================================
// Message Handling
// ============================================

async function handleSendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || state.isProcessing || state.isComplete) {
        return;
    }
    
    // Clear input immediately for better UX
    elements.messageInput.value = '';
    
    await sendMessage(message, true);
}

// ============================================
// Health Check
// ============================================

async function checkBackendHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
        if (response.ok) {
            console.log('Backend is healthy');
            return true;
        }
    } catch (error) {
        console.error('Backend health check failed:', error);
        alert('Cannot connect to backend. Please make sure the server is running on ' + CONFIG.API_BASE_URL);
    }
    return false;
}

// Check backend on load
window.addEventListener('load', () => {
    checkBackendHealth();
});

// ============================================
// Dark Mode
// ============================================

function initializeTheme() {
    const savedTheme = localStorage.getItem('career_guidance_theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        updateThemeIcon(true);
    } else {
        document.documentElement.classList.remove('dark-mode');
        updateThemeIcon(false);
    }
}

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark-mode');
    localStorage.setItem('career_guidance_theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    if (!elements.themeIcon) return;
    
    if (isDark) {
        // Moon icon for dark mode
        elements.themeIcon.innerHTML = `
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        `;
    } else {
        // Sun icon for light mode
        elements.themeIcon.innerHTML = `
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        `;
    }
}

