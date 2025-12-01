import { useState } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  // send question to backend
  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      })

      const data = await response.json()

      // add assistant response with sources
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `error: ${error.message}`,
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>policy chatbot</h1>
        <p>ask me anything about company policies</p>
      </div>

      <div className="chat-container">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>👋 hi there!</h2>
            <p>try asking questions like:</p>
            <ul>
              <li>how many vacation days do employees get?</li>
              <li>what is the parental leave policy?</li>
              <li>when do employees get paid?</li>
            </ul>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              <strong>{msg.role === 'user' ? 'you' : 'assistant'}:</strong>
              <p>{msg.content}</p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <strong>sources:</strong>
                  {msg.sources.map((src, i) => (
                    <div key={i} className="source">
                      📄 {src.source_file} (page {src.page_number}) - score: {src.relevance_score.toFixed(3)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <strong>assistant:</strong>
              <p className="loading">thinking...</p>
            </div>
          </div>
        )}
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="ask a question about company policies..."
          disabled={loading}
          rows="2"
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          send
        </button>
      </div>
    </div>
  )
}

export default App
