'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi } from '@/src/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, Sparkles, Trash2, Copy, CheckCircle2, Plus, List, Clock, Flag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { user } = useAuth();
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check if user is authenticated
  useEffect(() => {
    const storedAuth = localStorage.getItem('auth');
    const authData = storedAuth ? JSON.parse(storedAuth) : null;
    if (!authData || !authData.token) {
      // Redirect to login if not authenticated
      window.location.href = '/auth/signin';
    } else {
      // Simulate initialization delay for better UX
      setTimeout(() => {
        setIsInitializing(false);
      }, 500);
    }
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const [currentConversationId, setCurrentConversationId] = useState<number | null | undefined>(undefined);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Copy message to clipboard
  const handleCopyMessage = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedId(messageId);
      toast.success('Message copied to clipboard!');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      toast.error('Failed to copy message');
    }
  };

  // Clear all messages
  const handleClearChat = () => {
    setMessages([]);
    setCurrentConversationId(undefined);
    toast.success('Chat cleared!');
  };

  // Quick action handler
  const handleQuickAction = (message: string) => {
    setInputMessage(message);
    inputRef.current?.focus();
  };

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
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50">
      <div className="container mx-auto px-4 py-4 sm:py-8 max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-black/30 backdrop-blur-xl border-white/10 shadow-2xl rounded-xl sm:rounded-2xl overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-600/20 border-b border-white/10 pb-4 sm:pb-6">
              <div className="flex flex-col sm:flex-row items-center sm:items-center justify-between gap-4 sm:gap-0">
                <div className="flex items-center gap-3 sm:gap-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur-lg opacity-50 animate-pulse"></div>
                    <div className="relative bg-gradient-to-br from-indigo-500 to-purple-500 p-2 sm:p-3 rounded-full">
                      <Bot className="h-6 sm:h-8 w-6 sm:w-8 text-white" />
                    </div>
                  </div>
                  <div className="text-center sm:text-left">
                    <CardTitle className="flex flex-col sm:flex-row items-center gap-1 sm:gap-2 text-xl sm:text-3xl font-bold bg-gradient-to-r from-white via-indigo-200 to-purple-200 bg-clip-text text-transparent">
                      <span>Todo AI Assistant</span>
                      <Sparkles className="h-4 sm:h-6 w-4 sm:w-6 text-yellow-400 animate-pulse" />
                    </CardTitle>
                    <p className="text-gray-400 text-sm mt-1">
                      Your intelligent task management companion
                    </p>
                  </div>
                </div>
                {messages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClearChat}
                    className="text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg sm:rounded-xl transition-all self-start sm:self-auto"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear Chat
                  </Button>
                )}
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <ScrollArea className="h-[calc(100vh-320px)] sm:h-[calc(100vh-400px)] min-h-[300px] sm:min-h-[400px] p-4 sm:p-6" ref={scrollAreaRef}>
                <div className="space-y-3 sm:space-y-4">
                  {isInitializing ? (
                    // Skeleton screen for initial loading
                    <div className="flex flex-col space-y-4 py-12">
                      {/* Skeleton for welcome message */}
                      <div className="flex flex-col items-center justify-center h-full text-center py-12">
                        <div className="relative mb-6">
                          <div className="w-20 h-20 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-full blur-2xl"></div>
                          <div className="relative w-20 h-20 bg-gray-700/50 rounded-full animate-pulse" />
                        </div>
                        <div className="h-6 bg-gray-700/50 rounded w-64 mb-3 animate-pulse"></div>
                        <div className="h-4 bg-gray-700/30 rounded w-80 mb-8 animate-pulse"></div>

                        {/* Skeleton for quick action buttons */}
                        <div className="grid grid-cols-1 gap-2 sm:gap-3 w-full max-w-2xl">
                          {[...Array(4)].map((_, idx) => (
                            <div
                              key={idx}
                              className="w-full h-auto py-3 sm:py-4 px-4 sm:px-5 bg-gray-800/30 border border-gray-700/30 rounded-lg sm:rounded-xl animate-pulse"
                            >
                              <div className="flex items-start gap-2 sm:gap-3 text-left">
                                <div className="h-4 sm:h-5 w-4 sm:w-5 bg-gray-700/50 rounded mt-0.5"></div>
                                <div className="flex-1">
                                  <div className="h-3 sm:h-4 bg-gray-700/50 rounded w-1/3 mb-1 sm:mb-2"></div>
                                  <div className="h-2 sm:h-3 bg-gray-700/30 rounded w-2/3"></div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : messages.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.5 }}
                      className="flex flex-col items-center justify-center h-full text-center py-12"
                    >
                      <div className="relative mb-6">
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                        <Bot className="relative h-20 w-20 text-indigo-400" />
                      </div>
                      <h3 className="text-2xl font-bold bg-gradient-to-r from-white via-indigo-200 to-purple-200 bg-clip-text text-transparent mb-3">
                        Welcome to Your AI Assistant!
                      </h3>
                      <p className="text-gray-400 max-w-md mb-8 leading-relaxed">
                        I'm here to help you manage your tasks efficiently. Ask me anything about your todos!
                      </p>

                      <div className="grid grid-cols-1 gap-2 sm:gap-3 w-full max-w-2xl">
                        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            variant="outline"
                            onClick={() => handleQuickAction("Add a high priority task to finish the project report by tomorrow")}
                            className="w-full h-auto py-3 sm:py-4 px-4 sm:px-5 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border-indigo-500/30 hover:border-indigo-500/50 hover:bg-indigo-500/20 text-white rounded-lg sm:rounded-xl transition-all group"
                          >
                            <div className="flex items-start gap-2 sm:gap-3 text-left">
                              <Plus className="h-4 sm:h-5 w-4 sm:w-5 text-indigo-400 mt-0.5 group-hover:scale-110 transition-transform" />
                              <div>
                                <div className="font-semibold text-sm sm:text-base mb-1">Add a Task</div>
                                <div className="text-xs text-gray-400">Create new tasks with priority and due dates</div>
                              </div>
                            </div>
                          </Button>
                        </motion.div>

                        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            variant="outline"
                            onClick={() => handleQuickAction("Show me all my pending tasks sorted by priority")}
                            className="w-full h-auto py-3 sm:py-4 px-4 sm:px-5 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30 hover:border-green-500/50 hover:bg-green-500/20 text-white rounded-lg sm:rounded-xl transition-all group"
                          >
                            <div className="flex items-start gap-2 sm:gap-3 text-left">
                              <List className="h-4 sm:h-5 w-4 sm:w-5 text-green-400 mt-0.5 group-hover:scale-110 transition-transform" />
                              <div>
                                <div className="font-semibold text-sm sm:text-base mb-1">List Tasks</div>
                                <div className="text-xs text-gray-400">View all your tasks with filters</div>
                              </div>
                            </div>
                          </Button>
                        </motion.div>

                        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            variant="outline"
                            onClick={() => handleQuickAction("Mark task #1 as completed")}
                            className="w-full h-auto py-3 sm:py-4 px-4 sm:px-5 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/30 hover:border-blue-500/50 hover:bg-blue-500/20 text-white rounded-lg sm:rounded-xl transition-all group"
                          >
                            <div className="flex items-start gap-2 sm:gap-3 text-left">
                              <CheckCircle2 className="h-4 sm:h-5 w-4 sm:w-5 text-blue-400 mt-0.5 group-hover:scale-110 transition-transform" />
                              <div>
                                <div className="font-semibold text-sm sm:text-base mb-1">Complete Task</div>
                                <div className="text-xs text-gray-400">Mark tasks as done</div>
                              </div>
                            </div>
                          </Button>
                        </motion.div>

                        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            variant="outline"
                            onClick={() => handleQuickAction("Show me tasks due this week")}
                            className="w-full h-auto py-3 sm:py-4 px-4 sm:px-5 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/30 hover:border-yellow-500/50 hover:bg-yellow-500/20 text-white rounded-lg sm:rounded-xl transition-all group"
                          >
                            <div className="flex items-start gap-2 sm:gap-3 text-left">
                              <Clock className="h-4 sm:h-5 w-4 sm:w-5 text-yellow-400 mt-0.5 group-hover:scale-110 transition-transform" />
                              <div>
                                <div className="font-semibold text-sm sm:text-base mb-1">Due Soon</div>
                                <div className="text-xs text-gray-400">Check upcoming deadlines</div>
                              </div>
                            </div>
                          </Button>
                        </motion.div>
                      </div>
                    </motion.div>
                  ) : (
                    <AnimatePresence>
                      {messages.map((message, index) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 20, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, y: -20, scale: 0.95 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`group relative max-w-[90%] sm:max-w-[85%] rounded-xl sm:rounded-2xl p-3 sm:p-4 shadow-lg transition-all duration-200 hover:shadow-xl ${
                              message.role === 'user'
                                ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-br-md'
                                : 'bg-gradient-to-br from-gray-800/90 to-gray-900/90 backdrop-blur-lg border border-white/10 text-gray-100 rounded-bl-md'
                            }`}
                          >
                            <div className="flex items-start gap-2 sm:gap-3">
                              {message.role === 'assistant' && (
                                <div className="flex-shrink-0 bg-gradient-to-br from-indigo-500 to-purple-500 p-1.5 sm:p-2 rounded-lg">
                                  <Bot className="h-3.5 sm:h-4 w-3.5 sm:w-4 text-white" />
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <p className="whitespace-pre-wrap leading-relaxed text-sm sm:text-base">{message.content}</p>
                                <div className="flex items-center justify-between mt-2 sm:mt-3 pt-2 border-t border-white/10">
                                  <p className={`text-xs ${
                                    message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                                  }`}>
                                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </p>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleCopyMessage(message.content, message.id)}
                                    className={`h-5 sm:h-6 px-1.5 sm:px-2 opacity-0 group-hover:opacity-100 transition-opacity ${
                                      message.role === 'user'
                                        ? 'hover:bg-white/20 text-indigo-200'
                                        : 'hover:bg-white/10 text-gray-400'
                                    }`}
                                  >
                                    {copiedId === message.id ? (
                                      <CheckCircle2 className="h-2.5 sm:h-3 w-2.5 sm:w-3" />
                                    ) : (
                                      <Copy className="h-2.5 sm:h-3 w-2.5 sm:w-3" />
                                    )}
                                  </Button>
                                </div>
                              </div>
                              {message.role === 'user' && (
                                <div className="flex-shrink-0 bg-white/20 p-1.5 sm:p-2 rounded-lg">
                                  <User className="h-3.5 sm:h-4 w-3.5 sm:w-4 text-white" />
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}

                      {isLoading && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex justify-start"
                        >
                          <div className="max-w-[90%] sm:max-w-[85%] rounded-xl sm:rounded-2xl rounded-bl-md bg-gradient-to-br from-gray-800/90 to-gray-900/90 backdrop-blur-lg border border-white/10 text-gray-100 p-3 sm:p-4 shadow-lg">
                            <div className="flex items-center gap-2 sm:gap-3">
                              <div className="flex-shrink-0 bg-gradient-to-br from-indigo-500 to-purple-500 p-1.5 sm:p-2 rounded-lg">
                                <Bot className="h-3.5 sm:h-4 w-3.5 sm:w-4 text-white" />
                              </div>
                              <div className="flex space-x-1.5 sm:space-x-2">
                                <div className="h-2 w-2 sm:h-2.5 sm:w-2.5 bg-indigo-400 rounded-full animate-bounce"></div>
                                <div className="h-2 w-2 sm:h-2.5 sm:w-2.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="h-2 w-2 sm:h-2.5 sm:w-2.5 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  )}
                </div>
              </ScrollArea>

              <div className="p-4 sm:p-6 border-t border-white/10 bg-black/20 backdrop-blur-lg">
                <form onSubmit={handleSubmit} className="space-y-3">
                  <div className="flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                      <Input
                        ref={inputRef}
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Ask me anything about your tasks..."
                        disabled={isLoading}
                        className="bg-black/30 backdrop-blur-lg border-white/10 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent rounded-lg sm:rounded-xl h-11 sm:h-12 pr-10 sm:pr-12 transition-all text-sm sm:text-base"
                      />
                      <div className="absolute right-2.5 sm:right-3 top-1/2 -translate-y-1/2 text-gray-500">
                        <Sparkles className="h-3.5 sm:h-4 w-3.5 sm:w-4" />
                      </div>
                    </div>
                    <Button
                      type="submit"
                      disabled={isLoading || !inputMessage.trim()}
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-indigo-500/50 hover:scale-105 transition-all rounded-lg sm:rounded-xl h-11 sm:h-12 px-4 sm:px-6 text-sm sm:text-base"
                    >
                      <Send className="h-3.5 sm:h-4 w-3.5 sm:w-4 mr-1 sm:mr-2" />
                      <span className="hidden sm:inline">Send</span>
                      <span className="sm:hidden">Go</span>
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500 text-center">
                    {user?.id
                      ? "💡 Try: 'Add a task', 'Show my tasks', 'Complete task #1', 'Tasks due this week'"
                      : "Please log in to start chatting"}
                  </p>
                </form>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}





