import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Array<{
    type: string;
    title: string;
    url: string;
  }>;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInterface({
  messages,
  onSendMessage,
  disabled = false,
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isSending) {
      setIsSending(true);
      const message = input.trim();
      setInput('');
      await onSendMessage(message);
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg flex flex-col h-[calc(100vh-12rem)]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
        <h2 className="text-2xl font-semibold text-slate-800 dark:text-white flex items-center gap-2">
          <Bot className="w-6 h-6" />
          AI Assistant
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Ask questions about the search results
        </p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-slate-400 dark:text-slate-500">
            <div className="text-center">
              <Bot className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">Start a conversation</p>
              <p className="text-sm mt-2">
                {disabled
                  ? 'Search for a profile first'
                  : 'Ask me anything about the results'}
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}

                <div
                  className={`flex flex-col max-w-[80%] ${
                    message.role === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div
                    className={`rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-white'
                    }`}
                  >
                    {message.role === 'assistant' ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                  </div>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-slate-500 dark:text-slate-400">Sources:</p>
                      {message.sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-xs text-primary-600 dark:text-primary-400 hover:underline"
                        >
                          {source.title}
                        </a>
                      ))}
                    </div>
                  )}

                  <span className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center">
                      <User className="w-5 h-5 text-slate-600 dark:text-slate-300" />
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? 'Perform a search first...'
                : 'Ask a question... (Shift+Enter for new line)'
            }
            disabled={disabled || isSending}
            rows={2}
            className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg
                     bg-white dark:bg-slate-700 text-slate-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed
                     resize-none"
          />
          <button
            type="submit"
            disabled={disabled || isSending || !input.trim()}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg
                     transition-colors duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
