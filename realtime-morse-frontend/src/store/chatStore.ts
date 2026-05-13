// src/store/chatStore.ts
import { create } from 'zustand';
import { socketService } from '../services/socket/socket';
import { Conversation, Message, MessageType, InputMethod } from '../types/chat';

interface ChatState {
  conversations: Conversation[];
  activeConversation: string | null;
  messages: Message[];
  onlineUsers: string[];
  isLoading: boolean;

  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setActiveConversation: (conversationId: string | null) => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  updateOnlineUsers: (users: string[] | ((prev: string[]) => string[])) => void;
  sendMessage: (content: string, morseCode?: string, type?: MessageType, method?: InputMethod) => void;
  markAsRead: (conversationId: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversation: null,
  messages: [],
  onlineUsers: [],
  isLoading: false,

  setConversations: (conversations) => set({ conversations }),

  setActiveConversation: (conversationId) => set({ activeConversation: conversationId }),

  addMessage: (message) => set((state) => {
    if (state.messages.some((existingMessage) => existingMessage.id === message.id)) {
      return state;
    }

    return {
      messages: [...state.messages, message],
      conversations: state.conversations.map(conv =>
        conv.id === message.conversationId
          ? { ...conv, lastMessage: message, updatedAt: new Date() }
          : conv
      ),
    };
  }),

  setMessages: (messages) => set({ messages }),

  updateOnlineUsers: (users) => set((state) => ({
    onlineUsers: typeof users === 'function' ? users(state.onlineUsers) : users,
  })),

  sendMessage: (content, morseCode, type = 'text', method = 'text') => {
    const { activeConversation } = get();
    if (!activeConversation) return;

    const messageData = {
      conversation_id: Number(activeConversation),
      content,
      morse_code: morseCode,
      message_type: type,
      input_method: method,
    };

    socketService.emit('send_message', messageData);

    // We'll receive the message back via the 'message_received' event
    // For now, we can keep optimistic updates for immediate feedback
    const tempMessage: Message = {
      id: `temp-${Date.now()}`,
      conversationId: activeConversation,
      senderId: 'current-user', // Will be replaced by actual user ID from backend
      sender: {} as any, // Will be populated by backend response
      content,
      morseCode,
      messageType: type,
      inputMethod: method,
      createdAt: new Date(),
      isRead: false,
    };

    get().addMessage(tempMessage);
  },

  markAsRead: (conversationId) => set((state) => ({
    conversations: state.conversations.map(conv =>
      conv.id === conversationId
        ? { ...conv, unreadCount: 0 }
        : conv
    ),
  })),

  setLoading: (isLoading) => set({ isLoading }),
}));