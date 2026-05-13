// src/components/chat/MessageBubble.tsx
import { Message } from '@/types/chat';
import { useAuthStore } from '@/store/authStore';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { Keyboard, Mic, Type } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const { user } = useAuthStore();
  const isOwn = message.senderId === user?.id;

  const getInputMethodIcon = (method: string) => {
    switch (method) {
      case 'keyboard':
        return <Keyboard size={12} />;
      case 'microphone':
        return <Mic size={12} />;
      case 'text':
        return <Type size={12} />;
      default:
        return null;
    }
  };

  const getInputMethodLabel = (method: string) => {
    switch (method) {
      case 'keyboard':
        return 'Keyboard';
      case 'microphone':
        return 'Microphone';
      case 'text':
        return 'Text';
      default:
        return '';
    }
  };

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[70%] ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
        {!isOwn && (
          <Avatar className="w-8 h-8 mr-2">
            <AvatarFallback className="bg-gray-600 text-white text-xs">
              {message.sender.avatarInitials || message.sender.username.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
        )}

        <Card className={`p-3 ${isOwn ? 'bg-green-600 text-white' : 'bg-gray-700 text-white'}`}>
          {!isOwn && (
            <div className="text-xs text-gray-300 mb-1 font-medium">
              {message.sender.username}
            </div>
          )}

          {message.morseCode && (
            <div className="text-xs font-mono text-gray-300 mb-2 p-2 bg-black/20 rounded">
              {message.morseCode}
            </div>
          )}

          <div className="text-sm leading-relaxed">
            {message.content}
          </div>

          <div className={`flex items-center justify-between mt-2 text-xs ${isOwn ? 'text-green-100' : 'text-gray-400'}`}>
            <div className="flex items-center gap-1">
              {getInputMethodIcon(message.inputMethod)}
              <span>{getInputMethodLabel(message.inputMethod)}</span>
            </div>
            <span>{formatDistanceToNow(new Date(message.createdAt), { addSuffix: true })}</span>
          </div>
        </Card>
      </div>
    </div>
  );
};