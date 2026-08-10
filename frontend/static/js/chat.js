const API_URL = 'http://127.0.0.1:8000/api/chat';

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const inputField = document.getElementById('userInput');
    const message = inputField.value.trim();
    
    if (message === '') return;
    
    // Clear input
    inputField.value = '';
    
    // Add user message to UI
    appendMessage(message, 'user');
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        // Call the API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('API error');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeElement(typingId);
        
        // Add bot response to UI
        appendMessage(data.reply, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        removeElement(typingId);
        appendMessage("দুঃখিত, সার্ভারের সাথে কানেক্ট করতে সমস্যা হচ্ছে। একটু পর আবার চেষ্টা করুন।", 'bot');
    }
}

function appendMessage(text, sender) {
    const chatBox = document.getElementById('chatBox');
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerText = text; // innerText prevents HTML injection
    
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    
    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById('chatBox');
    const typingId = 'typing-' + Date.now();
    
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot';
    msgDiv.id = typingId;
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    bubble.appendChild(indicator);
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return typingId;
}

function removeElement(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}
