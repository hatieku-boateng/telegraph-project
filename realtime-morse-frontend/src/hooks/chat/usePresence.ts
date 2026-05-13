// src/hooks/chat/usePresence.ts
import { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useSocket } from '@/hooks/useSocket';

export const usePresence = () => {
  const { updateOnlineUsers } = useChatStore();
  const { on, off } = useSocket();

  useEffect(() => {
    const handleUserOnline = (data: any) => {
      console.log('User online:', data);
      updateOnlineUsers((prev) => [...prev.filter((id) => id !== String(data.user_id)), String(data.user_id)]);
    };

    const handleUserOffline = (data: any) => {
      console.log('User offline:', data);
      updateOnlineUsers((prev) => prev.filter((id) => id !== String(data.user_id)));
    };

    on('user_online', handleUserOnline);
    on('user_offline', handleUserOffline);

    return () => {
      off('user_online', handleUserOnline);
      off('user_offline', handleUserOffline);
    };
  }, [on, off, updateOnlineUsers]);

  return {};
};