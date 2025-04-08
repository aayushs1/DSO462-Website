// DOM Elements
const newChatBtn = document.getElementById('new-chat-btn');
const chatArea = document.getElementById('chat-area');
const welcomeContainer = document.getElementById('welcome-container');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const exampleQueries = document.querySelectorAll('.example-query');

// Variables
let currentChatId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Enable/disable send button based on input
    messageInput.addEventListener('input', () => {
        sendBtn.disabled = messageInput.value.trim() === '';
    });

    // Send message on enter key (but allow shift+enter for new lines)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button click
    sendBtn.addEventListener('click', sendMessage);

    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewChat);
    }

    // Example queries
    exampleQueries.forEach(query => {
        query.addEventListener('click', () => {
            const prompt = query.dataset.prompt;
            if (prompt) {
                messageInput.value = prompt;
                messageInput.dispatchEvent(new Event('input'));
                sendMessage();
            }
        });
    });
});

// Create a new chat
function createNewChat() {
    fetch('/chat/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        currentChatId = data.chat_id;

        // Hide welcome container and show empty chat
        if (welcomeContainer) {
            welcomeContainer.style.display = 'none';
        }

        // Clear any existing messages
        chatMessages.innerHTML = '';
    })
    .catch(error => {
        console.error('Error creating new chat:', error);
    });
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Create chat if doesn't exist yet
    if (!currentChatId) {
        createNewChat().then(() => {
            sendMessageToServer(message);
        });
    } else {
        sendMessageToServer(message);
    }
}

// Send message to server
function sendMessageToServer(message) {
    // Add user message to UI
    addMessage('user', message);

    // Clear input
    messageInput.value = '';
    sendBtn.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    // Send to server
    fetch('/message/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            chat_id: currentChatId,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeTypingIndicator();

        // Process bot response
        const botResponse = data.bot_response;
        addMessage('bot', botResponse.content, botResponse);
    })
    .catch(error => {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        addMessage('bot', 'Sorry, there was an error processing your request. Please try again.', null);
    });
}

// Add message to UI
function addMessage(sender, content, botData = null) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender === 'user' ? 'user-message' : ''}`;

    let avatarHtml;
    let senderName;
    let currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === 'user') {
        avatarHtml = `<div class="message-avatar user-message-avatar">U</div>`;
        senderName = 'You';
    } else {
        avatarHtml = `
            <div class="message-avatar bot-avatar">
                <svg width="24" height="24" viewBox="0 0 300 300" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M240 60H60C49 60 40 69 40 80v140c0 11 9 20 20 20h30l-15 30 45-30h120c11 0 20-9 20-20V80c0-11-9-20-20-20z" stroke="#333" stroke-width="20" fill="white"/>
                    <path d="M150 90l-50 30v60l50 30 50-30v-60l-50-30z" stroke="#333" stroke-width="10" fill="none"/>
                    <path d="M150 90l50 30v60l-50 30" stroke="#333" stroke-width="10" fill="none"/>
                    <path d="M150 90l-50 30v60" stroke="#333" stroke-width="10" fill="none"/>
                    <path d="M150 90l50 30-50 30-50-30 50-30z" fill="#FFA42B"/>
                    <path d="M100 120l50 30v60" stroke="#333" stroke-width="10" fill="none"/>
                    <path d="M150 150l50-30" stroke="#333" stroke-width="10" fill="none"/>
                    <path d="M100 120v60l50 30" fill="#CCCCCC" fill-opacity="0.6"/>
                    <path d="M200 120v60l-50 30" fill="#AAAAAA" fill-opacity="0.4"/>
                </svg>
            </div>
        `;
        senderName = 'GoGoPrint AI';
    }

    let messageHtml = `
        <div class="message-content">
            <div class="message-header">
                <div class="message-sender">${senderName}</div>
                <div class="message-time">${currentTime}</div>
            </div>
            <div class="message-text">
                <p>${content}</p>
            </div>
    `;

    // Add model preview if it's a bot message with a model
    if (sender === 'bot' && botData && botData.model_preview) {
        messageHtml += `
            <div class="model-preview">
                <img src="/static/img/model1.jpg" alt="3D Model Preview">
                <div class="model-controls">
                    <div class="model-info">
                        ${botData.model_name} (${botData.model_size})
                    </div>
                    <div class="model-actions">
                        <button class="model-btn download-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 15V3m0 12l-4-4m4 4l4-4m-9 4v4h10v-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            Download
                        </button>
                        <button class="model-btn print-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6 9V2h12v7M6 18H4v-9h16v9h-2m-3 4H9v-6h6v6z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            Print
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    messageHtml += `</div>`;

    messageElement.innerHTML = avatarHtml + messageHtml;
    chatMessages.appendChild(messageElement);

    // Scroll to bottom
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const typingElement = document.createElement('div');
    typingElement.className = 'chat-message';
    typingElement.id = 'typing-indicator';

    typingElement.innerHTML = `
        <div class="message-avatar bot-avatar">
            <svg width="24" height="24" viewBox="0 0 300 300" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M240 60H60C49 60 40 69 40 80v140c0 11 9 20 20 20h30l-15 30 45-30h120c11 0 20-9 20-20V80c0-11-9-20-20-20z" stroke="#333" stroke-width="20" fill="white"/>
                <path d="M150 90l-50 30v60l50 30 50-30v-60l-50-30z" stroke="#333" stroke-width="10" fill="none"/>
                <path d="M150 90l50 30v60l-50 30" stroke="#333" stroke-width="10" fill="none"/>
                <path d="M150 90l-50 30v60" stroke="#333" stroke-width="10" fill="none"/>
                <path d="M150 90l50 30-50 30-50-30 50-30z" fill="#FFA42B"/>
                <path d="M100 120l50 30v60" stroke="#333" stroke-width="10" fill="none"/>
                <path d="M150 150l50-30" stroke="#333" stroke-width="10" fill="none"/>
                <path d="M100 120v60l50 30" fill="#CCCCCC" fill-opacity="0.6"/>
                <path d="M200 120v60l-50 30" fill="#AAAAAA" fill-opacity="0.4"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-header">
                <div class="message-sender">GoGoPrint AI</div>
                <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    chatMessages.appendChild(typingElement);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingElement = document.getElementById('typing-indicator');
    if (typingElement) {
        typingElement.remove();
    }
}