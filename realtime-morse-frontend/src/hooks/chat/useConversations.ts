// src/hooks/chat/useConversations.ts
import { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { apiClient } from '@/services/api/client';
import { Conversation } from '@/types/chat';

export const useConversations = () => {
  const { setConversations, conversations } = useChatStore();

  const fetchConversations = async () => {
    try {
      const response = await apiClient.get('/conversations');
      const conversationsData: Conversation[] = response.data.map((conv: any) => ({
        id: String(conv.id),
        name: conv.name,
        participants: conv.participants,
        lastMessage: conv.last_message ? {
          id: String(conv.last_message.id),
          conversationId: String(conv.last_message.conversation_id),
          senderId: String(conv.last_message.sender_id),
          sender: conv.last_message.sender,
          content: conv.last_message.content,
          morseCode: conv.last_message.morse_code,
          messageType: conv.last_message.message_type,
          inputMethod: conv.last_message.input_method,
          createdAt: new Date(conv.last_message.created_at),
          isRead: conv.last_message.is_read,
        } : undefined,
        updatedAt: new Date(conv.updated_at),
        unreadCount: conv.unread_count || 0,
      }));
      setConversations(conversationsData);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  return {
    conversations,
    fetchConversations,
  };
};