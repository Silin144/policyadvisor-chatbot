document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');


    function formatTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function addMessage(message, isUser, time = formatTime()) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Format the message with proper HTML
        messageContent.innerHTML = formatMessage(message);

function formatMessage(message) {
    // Replace numbered points with line breaks
    message = message.replace(/(\d+\. )/g, '<br><br>$1');
    
    // Replace asterisk bold with HTML bold
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format tables if present
    if (message.includes('|')) {
        message = formatTable(message);
    }
    
    // Add line breaks for bullet points
    message = message.replace(/- /g, '<br>- ');
    
    // Remove extra line breaks at the start
    message = message.replace(/^(<br>)+/, '');
    
    return message;
}

function formatTable(message) {
    // Split message into lines
    const lines = message.split('\n');
    let inTable = false;
    let formattedContent = '';
    let currentTable = '';

    for (const line of lines) {
        if (line.includes('|')) {
            if (!inTable) {
                // Start new table
                inTable = true;
                currentTable = '<table class="chat-table"><tbody>';
            }
            // Convert line to table row
            const cells = line.split('|').filter(cell => cell.trim());
            const isHeader = line.includes('---');
            
            if (!isHeader) {
                currentTable += '<tr>';
                cells.forEach(cell => {
                    currentTable += `<td>${cell.trim()}</td>`;
                });
                currentTable += '</tr>';
            }
        } else {
            if (inTable) {
                // Close table
                inTable = false;
                currentTable += '</tbody></table>';
                formattedContent += currentTable;
                currentTable = '';
            }
            formattedContent += `<p>${line}</p>`;
        }
    }

    // Close any remaining table
    if (inTable) {
        currentTable += '</tbody></table>';
        formattedContent += currentTable;
    }

    return formattedContent;
}
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-time';
        timestamp.textContent = time;
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function loadConversationHistory(history) {
        // Clear existing messages except the welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Add messages from history
        history.forEach(msg => {
            addMessage(msg.content, msg.role === 'user');
        });
    }

    // Handle file selection
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = '';
        }
    });

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot bot-typing';
        typingDiv.textContent = 'Bot is typing';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Disable input and button while processing
        userInput.disabled = true;
        sendButton.disabled = true;

        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            // Create FormData and append message
            const formData = new FormData();
            formData.append('message', message);

            // Append file if selected
            if (fileInput.files.length > 0) {
                formData.append('file', fileInput.files[0]);
                // Clear file input and filename display after sending
                fileInput.value = '';
                fileName.textContent = '';
            }

            // Send message and file to backend
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();

            // Only add the new response
            addMessage(data.response, false);
        } catch (error) {
            console.error('Error:', error);
            // Remove typing indicator in case of error
            typingIndicator.remove();
            addMessage('Sorry, I encountered an error. Please try again.', false);
        } finally {
            // Re-enable input and button
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});