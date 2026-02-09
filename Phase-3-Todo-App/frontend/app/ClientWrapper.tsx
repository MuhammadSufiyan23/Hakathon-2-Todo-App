'use client';

import { ReactNode } from 'react';
import ChatIcon from '@/src/components/ChatIcon';

export default function ClientWrapper({ children }: { children: ReactNode }) {
  return (
    <>
      {children}
      <ChatIcon />
    </>
  );
}