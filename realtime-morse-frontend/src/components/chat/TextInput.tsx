import * as React from 'react';
import { Textarea } from '@/components/ui/textarea';

interface TextInputProps {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export function TextInput({ value, onChange }: TextInputProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="chat-message" className="text-sm font-medium text-gray-200">
        Message
      </label>
      <Textarea
        id="chat-message"
        value={value}
        onChange={onChange}
        placeholder="Type your message here..."
        className="min-h-[120px] bg-gray-900 border-gray-700 text-white"
      />
    </div>
  );
}
