'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi } from '@/src/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatWidget({ isOpen, onClose }: ChatWidgetProps) {
  const { user, isAuthenticated } = useAuth();
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    // Check for token existence before proceeding
    const storedAuth = localStorage.getItem('auth');
    const hasValidToken = storedAuth && JSON.parse(storedAuth).token;

    if (!hasValidToken) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Authentication required. Please log in to continue.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Use user.id if available, otherwise try to extract from token
      let userId = user?.id;

      if (!userId) {
        // Extract user ID from token as fallback
        try {
          const token = JSON.parse(storedAuth!).token;
          const tokenParts = token.split('.');
          if (tokenParts.length === 3) {
            const payload = tokenParts[1];
            const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
            const decodedPayload = atob(paddedPayload);
            const decodedToken = JSON.parse(decodedPayload);
            userId = decodedToken.userId || decodedToken.sub || decodedToken.id;
          }
        } catch (tokenError) {
          console.error('Failed to extract user ID from token:', tokenError);
        }
      }

      if (!userId) {
        throw new Error('Unable to determine user ID from token.');
      }

      // Send message to backend
      const response: any = await chatApi.sendMessage(userId, inputMessage);

      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: typeof response === 'object' && response?.response ? response.response : (typeof response === 'string' ? response : 'I processed your request successfully.'),
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Error sending message:', error);

      let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';

      // Check if it's an authentication error
      if (error.message?.includes('Authentication required') ||
          (error.response && (error.response.status === 401 || error.response.status === 403))) {
        errorMessageText = 'Your session expired. Please log in again.';
      } else if (error.message?.includes('Network error')) {
        errorMessageText = 'Unable to reach the server. Please check your connection.';
      } else if (error.message?.includes('Unable to determine user ID')) {
        errorMessageText = 'Authentication issue. Please refresh the page or log in again.';
      }

      // Add error message to UI
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: errorMessageText,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="fixed bottom-24 right-6 z-50 w-full max-w-md"
    >
      <Card className="bg-gray-900/90 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border-b border-white/10 p-4">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-indigo-400" />
            <h3 className="font-semibold text-white">Todo Assistant</h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-gray-400 hover:text-white hover:bg-gray-800/50"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <CardContent className="p-0">
          <ScrollArea className="h-80 p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-8">
                  <div className="p-3 bg-indigo-500/10 rounded-full mb-3">
                    <Bot className="h-10 w-10 text-indigo-400" />
                  </div>
                  <h4 className="font-medium text-white mb-1">How can I help?</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    Ask me to manage your tasks
                  </p>
                  <div className="grid grid-cols-2 gap-2 w-full max-w-xs">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputMessage("Add a task to buy groceries")}
                      className="text-xs text-left justify-start"
                    >
                      Add task
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputMessage("Show my tasks")}
                      className="text-xs text-left justify-start"
                    >
                      List tasks
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputMessage("Complete task 1")}
                      className="text-xs text-left justify-start"
                    >
                      Complete
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputMessage("Delete task 1")}
                      className="text-xs text-left justify-start"
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ) : (
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl p-3 ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none'
                            : 'bg-gray-800 text-gray-100 rounded-bl-none'
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          {message.role === 'assistant' && (
                            <Bot className="h-4 w-4 mt-0.5 text-indigo-400 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            <p className={`text-xs mt-1 ${
                              message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                            }`}>
                              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                          {message.role === 'user' && (
                            <User className="h-4 w-4 mt-0.5 text-indigo-200 flex-shrink-0" />
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}

                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex justify-start"
                    >
                      <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-gray-800 text-gray-100 p-3">
                        <div className="flex items-center gap-2">
                          <Bot className="h-4 w-4 mt-0.5 text-indigo-400" />
                          <div className="flex space-x-1">
                            <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              )}
            </div>
          </ScrollArea>

          <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
            <div className="flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about your tasks..."
                disabled={isLoading}
                className="flex-1 bg-gray-800/50 border-white/10 text-white text-sm placeholder:text-gray-500 h-9 focus-visible:ring-1 focus-visible:ring-indigo-500"
              />
              <Button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                size="sm"
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 h-9 transition-all duration-200"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}