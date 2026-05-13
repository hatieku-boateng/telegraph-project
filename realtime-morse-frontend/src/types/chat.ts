// src/types/chat.ts
export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  sender: User;
  content: string;
  morseCode?: string;
  messageType: 'text' | 'morse' | 'mixed';
  inputMethod: 'keyboard' | 'microphone' | 'text';
  createdAt: Date;
  isRead: boolean;
  reactions?: MessageReaction[];
}

export interface Conversation {
  id: string;
  name?: string;
  participants: User[];
  lastMessage?: Message;
  updatedAt: Date;
  unreadCount: number;
}

export interface MessageReaction {
  id: string;
  emoji: string;
  userId: string;
  createdAt: Date;
}

export interface TypingIndicator {
  userId: string;
  conversationId: string;
  timestamp: Date;
}

export type MessageType = 'text' | 'morse' | 'mixed';
export type InputMethod = 'keyboard' | 'microphone' | 'text';