'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi } from '@/src/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { user, isAuthenticated } = useAuth();
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Check if user is authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      // Redirect to login if not authenticated
      window.location.href = '/auth/signin';
    }
  }, [isAuthenticated]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const [currentConversationId, setCurrentConversationId] = useState<number | null | undefined>(undefined);

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
      const response: any = await chatApi.sendMessage(
        userId,
        inputMessage,
        currentConversationId ?? undefined
      );

      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: typeof response === 'object' && response?.response ? response.response : (typeof response === 'string' ? response : 'I processed your request successfully.'),
        timestamp: new Date(),
      };

      // Update conversation ID if returned in response
      if (response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
      }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-indigo-950">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="bg-black/30 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border-b border-white/10">
            <CardTitle className="flex items-center gap-3 text-2xl text-white">
              <Bot className="h-8 w-8 text-indigo-400" />
              <span>Todo Assistant</span>
            </CardTitle>
            <p className="text-gray-400">
              Chat with your AI assistant to manage your tasks
            </p>
          </CardHeader>

          <CardContent className="p-0">
            <ScrollArea className="h-[60vh] p-4" ref={scrollAreaRef}>
              <div className="space-y-6">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center py-12">
                    <Bot className="h-16 w-16 text-indigo-400 mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">Welcome to Todo Assistant!</h3>
                    <p className="text-gray-400 max-w-md">
                      I can help you manage your tasks. Try asking me to add, list, complete, or delete tasks.
                    </p>
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-lg">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setInputMessage("Add a task to buy groceries")}
                        className="text-left justify-start"
                      >
                        Add a task
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setInputMessage("Show my tasks")}
                        className="text-left justify-start"
                      >
                        List tasks
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setInputMessage("Complete task 1")}
                        className="text-left justify-start"
                      >
                        Complete task
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setInputMessage("Delete task 1")}
                        className="text-left justify-start"
                      >
                        Delete task
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
                          className={`max-w-[80%] rounded-2xl p-4 ${
                            message.role === 'user'
                              ? 'bg-indigo-600 text-white rounded-br-none'
                              : 'bg-gray-800 text-gray-100 rounded-bl-none'
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            {message.role === 'assistant' && (
                              <Bot className="h-5 w-5 mt-0.5 text-indigo-400 flex-shrink-0" />
                            )}
                            <div className="flex-1">
                              <p className="whitespace-pre-wrap">{message.content}</p>
                              <p className={`text-xs mt-2 ${
                                message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                              }`}>
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>
                            {message.role === 'user' && (
                              <User className="h-5 w-5 mt-0.5 text-indigo-200 flex-shrink-0" />
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
                        <div className="max-w-[80%] rounded-2xl rounded-bl-none bg-gray-800 text-gray-100 p-4">
                          <div className="flex items-center gap-3">
                            <Bot className="h-5 w-5 mt-0.5 text-indigo-400" />
                            <div className="flex space-x-2">
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
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
              <div className="flex gap-3">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message here..."
                  disabled={isLoading}
                  className="flex-1 bg-gray-800/50 border-white/10 text-white placeholder:text-gray-500"
                />
                <Button
                  type="submit"
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                {user?.id
                  ? "Ask me to add, list, complete, or delete tasks"
                  : "Please log in to start chatting"}
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}





