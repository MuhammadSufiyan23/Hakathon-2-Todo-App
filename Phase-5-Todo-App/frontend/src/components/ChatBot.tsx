import React, { useState, useEffect, useRef } from 'react';
import { chatApi } from '@/src/services/api';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatBotProps {
  isOpen: boolean;
  onClose: () => void;
  userId?: string;
}

const ChatBot = ({ isOpen, onClose, userId }: ChatBotProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userText = inputValue;
    setInputValue('');

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: userText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Check for token existence before proceeding
      const storedAuth = localStorage.getItem('auth');
      const hasValidToken = storedAuth && JSON.parse(storedAuth).token;

      if (!hasValidToken) {
        throw new Error('Authentication required. Please log in to continue.');
      }

      // Use provided userId if available, otherwise try to extract from token
      let effectiveUserId = userId;

      if (!effectiveUserId) {
        // Extract user ID from token as fallback
        try {
          const token = JSON.parse(storedAuth!).token;
          const tokenParts = token.split('.');
          if (tokenParts.length === 3) {
            const payload = tokenParts[1];
            const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
            const decodedPayload = atob(paddedPayload);
            const decodedToken = JSON.parse(decodedPayload);
            effectiveUserId = decodedToken.userId || decodedToken.sub || decodedToken.id;
          }
        } catch (tokenError) {
          console.error('Failed to extract user ID from token:', tokenError);
        }
      }

      if (!effectiveUserId) {
        throw new Error('Unable to determine user ID from token.');
      }

      const result: any = await chatApi.sendMessage(effectiveUserId, userText);

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: typeof result === 'object' && result?.response ? result.response : (typeof result === 'string' ? result : 'Task processed successfully.'),
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('[CHATBOT ERROR]', err);

      let errorMessageText = 'Unable to process your request.';

      // Check if it's an authentication error
      if (err.message?.includes('Authentication required') ||
          (err.response && (err.response.status === 401 || err.response.status === 403))) {
        errorMessageText = 'Your session expired. Please log in again.';
      } else if (err.message?.includes('Network error')) {
        errorMessageText = 'Unable to reach the server. Please check your connection.';
      } else if (err.message?.includes('Unable to determine user ID')) {
        errorMessageText = 'Authentication issue. Please refresh the page or log in again.';
      }

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 2,
          role: 'assistant',
          content: errorMessageText,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-24 right-6 w-96 h-96 bg-white border rounded-lg shadow-xl flex flex-col z-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-t-lg flex justify-between items-center">
        <h3 className="font-bold flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
          AI Todo Assistant
        </h3>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-gray-100 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8 text-sm">
            <div className="inline-block p-3 bg-blue-50 rounded-full mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p className="font-medium mb-2">How can I help you today?</p>
            <div className="space-y-1">
              <p>Try saying:</p>
              <div className="flex flex-wrap gap-1 mt-2">
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Add task meeting</span>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Show my tasks</span>
                <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">Complete task 1</span>
              </div>
            </div>
          </div>
        )}

        {messages.map(msg => (
          <div
            key={msg.id}
            className={`p-3 rounded-2xl max-w-[80%] text-sm ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white ml-auto text-right rounded-br-none'
                : 'bg-gray-200 text-gray-800 mr-auto rounded-bl-none'
            }`}
          >
            <div className="text-xs font-semibold mb-1 opacity-90">
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className="whitespace-pre-wrap break-words">{msg.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className="p-3 rounded-2xl bg-gray-200 mr-auto rounded-bl-none text-sm">
            <div className="flex items-center">
              <div className="mr-2">Thinking…</div>
              <div className="flex space-x-1">
                <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t bg-white flex">
        <input
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ask me about your tasks..."
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 rounded-r-lg text-sm hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </form>
    </div>
  );
};

export default ChatBot;
