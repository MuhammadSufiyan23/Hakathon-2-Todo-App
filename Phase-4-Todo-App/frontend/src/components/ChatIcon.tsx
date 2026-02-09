'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import ChatWidget with ssr disabled to prevent auth context issues during build
const DynamicChatWidget = dynamic(() => import('./ChatWidget'), {
  ssr: false
});

interface ChatIconProps {
  onClick?: () => void;
}

const ChatIcon = ({ onClick }: ChatIconProps) => {
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);

  const handleToggle = () => {
    setIsChatOpen(!isChatOpen);
    if (onClick) {
      onClick();
    }
  };

  return (
    <>
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={handleToggle}
          className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 transform hover:scale-105"
          aria-label={isChatOpen ? "Close chat" : "Open chat"}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      </div>

      <DynamicChatWidget
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
};

export default ChatIcon;