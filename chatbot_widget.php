<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biplob World - Ask Us Anything</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .chat-box {
            background: #f7f7f7;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 85%;
        }
        
        .question {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .answer {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .answer .confidence {
            font-size: 11px;
            color: #999;
            margin-top: 8px;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        #questionInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #questionInput:focus {
            border-color: #667eea;
        }
        
        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            color: #999;
            font-style: italic;
            padding: 10px;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐝 Biplob World</h1>
            <p>Ask me anything about our products and services!</p>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message answer">
                <div>Hello! I'm here to help you learn about Biplob World. Ask me anything!</div>
            </div>
        </div>
        
        <form method="POST" id="chatForm">
            <div class="input-group">
                <input 
                    type="text" 
                    id="questionInput" 
                    name="question" 
                    placeholder="Type your question here..." 
                    required
                    autocomplete="off"
                >
                <button type="submit" id="submitBtn">Ask</button>
            </div>
        </form>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const chatForm = document.getElementById('chatForm');
        const questionInput = document.getElementById('questionInput');
        const submitBtn = document.getElementById('submitBtn');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const question = questionInput.value.trim();
            if (!question) return;

            // Add question to chat
            addMessage(question, 'question');
            
            // Clear input
            questionInput.value = '';
            
            // Disable form
            submitBtn.disabled = true;
            addMessage('Thinking...', 'loading');

            try {
                const response = await fetch('chatbot_api.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question })
                });

                const data = await response.json();
                
                // Remove loading message
                removeLoading();
                
                if (data.error) {
                    addMessage('❌ ' + data.error, 'error');
                } else {
                    const confidence = Math.round(data.confidence * 100);
                    const answer = data.answer;
                    const confidenceText = `Confidence: ${confidence}% | ${data.response_time_ms}ms`;
                    addMessage(answer, 'answer', confidenceText);
                }
            } catch (error) {
                removeLoading();
                addMessage('❌ Connection error. Please make sure the chatbot server is running.', 'error');
            }

            // Re-enable form
            submitBtn.disabled = false;
            questionInput.focus();
        });

        function addMessage(text, type, extra = '') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            if (type === 'loading') {
                messageDiv.classList.add('loading');
                messageDiv.textContent = text;
            } else if (type === 'error') {
                messageDiv.className = 'error';
                messageDiv.textContent = text;
            } else {
                const textDiv = document.createElement('div');
                textDiv.textContent = text;
                messageDiv.appendChild(textDiv);
                
                if (extra && type === 'answer') {
                    const confidenceDiv = document.createElement('div');
                    confidenceDiv.className = 'confidence';
                    confidenceDiv.textContent = extra;
                    messageDiv.appendChild(confidenceDiv);
                }
            }
            
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function removeLoading() {
            const loading = chatBox.querySelector('.loading');
            if (loading) loading.remove();
        }
    </script>
</body>
</html>
