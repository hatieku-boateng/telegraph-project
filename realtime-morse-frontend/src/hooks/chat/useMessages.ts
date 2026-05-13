// src/hooks/chat/useMessages.ts
import { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useSocket } from '@/hooks/useSocket';
import { apiClient } from '@/services/api/client';
import { Message } from '@/types/chat';

export const useMessages = () => {
  const { addMessage, setMessages, activeConversation } = useChatStore();
  const { on, off, emit } = useSocket();

  useEffect(() => {
    // Listen for new messages
    const handleMessageReceived = (messageData: any) => {
      const message: Message = {
        id: messageData.id,
        conversationId: messageData.conversation_id,
        senderId: messageData.sender_id,
        sender: messageData.sender,
        content: messageData.content,
        morseCode: messageData.morse_code,
        messageType: messageData.message_type,
        inputMethod: messageData.input_method,
        createdAt: new Date(messageData.created_at),
        isRead: messageData.is_read,
      };

      addMessage(message);
    };

    on('message_received', handleMessageReceived);

    return () => {
      off('message_received', handleMessageReceived);
    };
  }, [on, off, addMessage]);

  useEffect(() => {
    if (!activeConversation) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      try {
        const response = await apiClient.get(`/conversations/${activeConversation}/messages`);
        const messages: Message[] = response.data.messages.map((messageData: any) => ({
          id: String(messageData.id),
          conversationId: String(messageData.conversation_id),
          senderId: String(messageData.sender_id),
          sender: messageData.sender,
          content: messageData.content,
          morseCode: messageData.morse_code,
          messageType: messageData.message_type,
          inputMethod: messageData.input_method,
          createdAt: new Date(messageData.created_at),
          isRead: messageData.is_read,
        }));

        setMessages(messages);
      } catch (error) {
        console.error('Failed to fetch messages:', error);
        setMessages([]);
      }
    };

    fetchMessages();
  }, [activeConversation, setMessages]);

  const sendMessage = (content: string, morseCode?: string, type: 'text' | 'morse' | 'mixed' = 'text', method: 'keyboard' | 'microphone' | 'text' = 'text') => {
    if (!activeConversation) return;

    const messageData = {
      conversation_id: Number(activeConversation),
      content,
      morse_code: morseCode,
      message_type: type,
      input_method: method,
    };

    emit('send_message', messageData);
  };

  return {
    sendMessage,
  };
};