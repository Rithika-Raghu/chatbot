import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Wrench, CheckCircle } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: history
        }),
      });

      const data = await response.json();

      if (data.error) {
        setMessages(prev => [...prev, { 
          role: 'error', 
          content: `Error: ${data.error}` 
        }]);
      } else {
        if (data.tool_calls && data.tool_calls.length > 0) {
          setMessages(prev => [...prev, { 
            role: 'tool_calls', 
            content: data.tool_calls 
          }]);
        }

        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }]);

        setHistory(data.history);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: `Network error: ${error.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="header-icon">
            <Bot size={24} color="white" />
          </div>
          <div>
            <h1>AI Tool Chatbot</h1>
            <p className="subtitle">Powered by Llama 3.3</p>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="messages-wrapper">
          <div className="messages-area">
            {messages.length === 0 && (
              <div className="empty-state">
                <Bot size={64} color="#ccc" />
                <h2>Start a Conversation</h2>
                <p>Try asking: "What's the time?", "Calculate 25*4", or "Weather in Chennai"</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div key={index}>
                {message.role === 'user' && (
                  <div className="message-row user-row">
                    <div className="message user-message">
                      <p>{message.content}</p>
                    </div>
                    <div className="avatar user-avatar">
                      <User size={20} />
                    </div>
                  </div>
                )}

                {message.role === 'tool_calls' && (
                  <div className="message-row assistant-row">
                    <div className="tool-calls">
                      {message.content.map((tool, toolIndex) => (
                        <div key={toolIndex} className="tool-call">
                          <div className="tool-header">
                            <Wrench size={16} />
                            <span className="tool-name">{tool.tool}</span>
                          </div>
                          
                          <div className="tool-content">
                            <div className="tool-section">
                              <span className="tool-label">📥 Input:</span>
                              <div className="tool-value">{tool.input}</div>
                            </div>
                            
                            <div className="tool-section">
                              <div className="tool-result-header">
                                {tool.success ? (
                                  <CheckCircle size={14} color="#10b981" />
                                ) : (
                                  <span style={{color: '#ef4444'}}>❌</span>
                                )}
                                <span className="tool-label">📤 Output:</span>
                              </div>
                              <div className="tool-value output">{tool.output}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}


                {message.role === 'assistant' && (
                  <div className="message-row assistant-row">
                    <div className="avatar bot-avatar">
                      <Bot size={20} />
                    </div>
                    <div className="message assistant-message">
                      <p>{message.content}</p>
                    </div>
                  </div>
                )}

                {message.role === 'error' && (
                  <div className="message-row center-row">
                    <div className="error-message">
                      {message.content}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="message-row assistant-row">
                <div className="avatar bot-avatar">
                  <Bot size={20} />
                </div>
                <div className="message assistant-message">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
          >
            <Send size={20} />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
