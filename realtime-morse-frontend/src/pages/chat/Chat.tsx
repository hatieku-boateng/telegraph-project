// src/pages/chat/Chat.tsx
import { useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useChatStore } from '../../store/chatStore';
import { useSocket } from '../../hooks/useSocket';
import { useMessages } from '../../hooks/chat/useMessages';
import { usePresence } from '../../hooks/chat/usePresence';
import { useConversations } from '../../hooks/chat/useConversations';
import { apiClient } from '../../services/api/client';
import { ChatWindow } from '../../components/chat/ChatWindow';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Users, MessageSquare, Plus } from 'lucide-react';

const Chat = () => {
  const { user } = useAuthStore();
  const { conversations, setActiveConversation, activeConversation } = useChatStore();
  const { isConnected, emit } = useSocket();

  // Initialize chat hooks
  useMessages();
  usePresence();
  useConversations();

  const handleJoinConversation = (conversationId: string | number) => {
    const conversationIdString = String(conversationId);
    setActiveConversation(conversationIdString);
    emit('join_conversation', { conversation_id: Number(conversationIdString) });
  };

  const handleCreateConversation = async () => {
    try {
      const response = await apiClient.post('/conversations', {
        participant_ids: [user!.id],
        name: 'My Chat',
      });
      const newConversation = response.data;
      // Refresh conversations
      useConversations().fetchConversations();
      // Join the new conversation
      handleJoinConversation(newConversation.id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-green-400 flex items-center gap-2">
            <MessageSquare size={20} />
            Telegraph Chat
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Connection: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
              <Users size={16} />
              Conversations
            </h3>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <Users size={16} />
                Conversations
              </h3>
              <Button
                onClick={handleCreateConversation}
                size="sm"
                className="bg-green-600 hover:bg-green-700"
              >
                <Plus size={14} />
              </Button>
            </div>
            <div className="space-y-2">
              {conversations.length === 0 ? (
                <Card className="p-4 bg-gray-700 border-gray-600">
                  <p className="text-sm text-gray-400 text-center">
                    No conversations yet. Create one to start chatting!
                  </p>
                </Card>
              ) : (
                conversations.map((conversation) => (
                  <Card
                    key={conversation.id}
                    className={`p-3 cursor-pointer transition-colors ${
                      activeConversation === conversation.id
                        ? 'bg-green-600 border-green-500'
                        : 'bg-gray-700 border-gray-600 hover:bg-gray-650'
                    }`}
                    onClick={() => handleJoinConversation(conversation.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{conversation.name || 'Chat'}</p>
                        <p className="text-xs text-gray-400">
                          {conversation.participants.length} participants
                        </p>
                        {conversation.lastMessage && (
                          <p className="text-xs text-gray-500 truncate mt-1">
                            {conversation.lastMessage.content}
                          </p>
                        )}
                      </div>
                      {conversation.unreadCount > 0 && (
                        <div className="bg-green-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                          {conversation.unreadCount}
                        </div>
                      )}
                    </div>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatWindow />
      </div>
    </div>
  );
};

export default Chat;