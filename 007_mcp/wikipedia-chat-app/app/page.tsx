'use client'

import { useState } from 'react'
import styles from './page.module.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')

  const loadingMessages = [
    'Searching Wikipedia articles...',
    'Gathering knowledge from multiple sources...',
    'Analyzing relevant information...',
    'Synthesizing research findings...',
    'Compiling comprehensive report...',
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Set a random loading message
    setLoadingMessage(
      loadingMessages[Math.floor(Math.random() * loadingMessages.length)]
    )

    // Add a placeholder for assistant response
    const assistantMessageIndex = messages.length + 1
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      // Stream the response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullText = ''

      if (reader) {
        let done = false
        while (!done) {
          const { value, done: readerDone } = await reader.read()
          done = readerDone

          if (value) {
            const chunk = decoder.decode(value, { stream: true })
            fullText += chunk

            // Update the last message with streamed content
            setMessages((prev) => {
              const updated = [...prev]
              if (updated[assistantMessageIndex]) {
                updated[assistantMessageIndex].content = fullText
              }
              return updated
            })
          }
        }
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const examplePrompts = [
    'Research and write a report on geotechnical engineering',
    'What are the key discoveries in quantum computing?',
    'Explain the history and impact of the Renaissance',
  ]

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Wikipedia Research Assistant</h1>
          <p className={styles.description}>
            Ask me to research any topic on Wikipedia. I&apos;ll gather information,
            analyze content, and create comprehensive reports for you.
          </p>
        </div>

        {messages.length === 0 && (
          <div className={styles.examples}>
            <p className={styles.examplesTitle}>Try commands like:</p>
            <div className={styles.examplesList}>
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  className={styles.exampleButton}
                  onClick={() => setInput(prompt)}
                >
                  &quot;{prompt}&quot;
                </button>
              ))}
            </div>
          </div>
        )}

        <div className={styles.chatContainer}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${styles.message} ${
                message.role === 'user'
                  ? styles.userMessage
                  : styles.assistantMessage
              }`}
            >
              <div className={styles.messageContent}>{message.content}</div>
            </div>
          ))}
          {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
            <div className={`${styles.message} ${styles.assistantMessage}`}>
              <div className={styles.messageContent}>
                <div className={styles.loader}>{loadingMessage}</div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about any Wikipedia topic..."
            className={styles.input}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </main>
  )
}
