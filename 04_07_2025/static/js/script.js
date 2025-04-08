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

    // Chat history items
    document.querySelectorAll('.chat-history-item').forEach(item => {
        item.addEventListener('click', () => {
            const chatId = item.dataset.chatId;
            if (chatId) {
                window.location.href = `/chat/${chatId}`;
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
        avatarHtml = `<div class="message-avatar user-message-avatar">P</div>`;
        senderName = 'You';
    } else {
        avatarHtml = `
            <div class="message-avatar bot-avatar">
                <img src="/static/img/white_logo.png" alt="GoGoPrint Logo" width="24" height="24">
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
        let modelImage = 'model1.jpg';
        if (botData.model_name.includes('lamp') || botData.model_name.includes('light')) {
            modelImage = 'model2