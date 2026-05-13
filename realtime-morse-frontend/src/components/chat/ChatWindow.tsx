// src/components/chat/ChatWindow.tsx
import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useMorseStore } from '@/store/morseStore';
import { useMessages } from '@/hooks/chat/useMessages';
import { usePresence } from '@/hooks/chat/usePresence';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';

export const ChatWindow = () => {
  const { activeConversation, messages } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat hooks
  useMessages();
  usePresence();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!activeConversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center text-gray-400">
          <div className="text-6xl mb-4">⚡</div>
          <h2 className="text-xl font-semibold mb-2">Select a conversation</h2>
          <p>Choose someone to start Morse messaging</p>
        </div>
      </div>
    );
  }

  const conversationMessages = messages.filter(
    msg => msg.conversationId === activeConversation
  );

  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {conversationMessages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          <TypingIndicator conversationId={activeConversation} />
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Message Input */}
      <div className="border-t border-gray-700 bg-gray-800">
        <MessageInput />
      </div>
    </div>
  );
};