// src/components/chat/MessageInput.tsx
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useChatStore } from '@/store/chatStore';
import { useSocket } from '@/hooks/useSocket';
import { useIsMobile } from '@/hooks/use-mobile';
import { useTelegraph } from '@/hooks/useTelegraph';
import { TelegraphKey } from '@/components/TelegraphKey';
import { AudioDecoder } from '@/components/AudioDecoder';
import { TextInput } from './TextInput';
import { TransmissionPreview } from '@/components/morse/TransmissionPreview';
import { Keyboard, Mic, Type } from 'lucide-react';

export const MessageInput = () => {
  const { activeConversation } = useChatStore();
  const { emit } = useSocket();
  const telegraph = useTelegraph();
  const isMobile = useIsMobile();
  const [activeTab, setActiveTab] = useState<'text' | 'keyboard' | 'microphone'>('text');
  const [inputMode, setInputMode] = useState<'keyboard' | 'button'>(isMobile ? 'button' : 'keyboard');
  const [textMessage, setTextMessage] = useState('');
  const [audioDecodedText, setAudioDecodedText] = useState('');
  const [audioRawSequence, setAudioRawSequence] = useState('');

  useEffect(() => {
    setInputMode(isMobile ? 'button' : 'keyboard');
  }, [isMobile]);

  const handleSend = () => {
    if (!activeConversation) return;

    let content = '';
    let morseCode: string | undefined;
    let messageType: 'text' | 'morse' | 'mixed' = 'text';
    let inputMethod: 'keyboard' | 'microphone' | 'text' = 'text';

    if (activeTab === 'text') {
      content = textMessage.trim();
      if (!content) return;
      messageType = 'text';
      inputMethod = 'text';
    } else if (activeTab === 'keyboard') {
      content = telegraph.decodedText.trim();
      if (!content) return;
      morseCode = telegraph.rawSequence || undefined;
      messageType = 'morse';
      inputMethod = 'keyboard';
    } else {
      content = audioDecodedText.trim();
      if (!content) return;
      morseCode = audioRawSequence || undefined;
      messageType = 'morse';
      inputMethod = 'microphone';
    }

    const messageData = {
      conversation_id: Number(activeConversation),
      content,
      morse_code: morseCode,
      message_type: messageType,
      input_method: inputMethod,
    };

    emit('send_message', messageData);

    if (activeTab === 'text') {
      setTextMessage('');
    }
    if (activeTab === 'keyboard') {
      telegraph.reset();
    }
    if (activeTab === 'microphone') {
      setAudioDecodedText('');
      setAudioRawSequence('');
    }
  };

  const handleTabChange = (value: string) => {
    setActiveTab(value as 'text' | 'keyboard' | 'microphone');
  };

  const previewText =
    activeTab === 'text'
      ? textMessage
      : activeTab === 'keyboard'
      ? telegraph.decodedText
      : audioDecodedText;

  const previewSequence =
    activeTab === 'keyboard'
      ? telegraph.rawSequence
      : activeTab === 'microphone'
      ? audioRawSequence
      : '';

  const isSendDisabled =
    activeTab === 'text'
      ? !textMessage.trim()
      : activeTab === 'keyboard'
      ? !telegraph.decodedText.trim()
      : !audioDecodedText.trim();

  return (
    <Card className="p-4 bg-gray-800 border-gray-700">
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <TabsList className="grid w-full grid-cols-3 bg-gray-700">
          <TabsTrigger value="text" className="flex items-center gap-2">
            <Type size={16} />
            Text
          </TabsTrigger>
          <TabsTrigger value="keyboard" className="flex items-center gap-2">
            <Keyboard size={16} />
            Keyboard
          </TabsTrigger>
          <TabsTrigger value="microphone" className="flex items-center gap-2">
            <Mic size={16} />
            Microphone
          </TabsTrigger>
        </TabsList>

        <div className="mt-4">
          <TabsContent value="text" className="mt-0">
            <TextInput value={textMessage} onChange={(event) => setTextMessage(event.target.value)} />
          </TabsContent>

          <TabsContent value="keyboard" className="mt-0">
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">
                Hold Space bar to input Morse code.
              </p>
              <TelegraphKey
                isPressing={telegraph.isPressing}
                inputMode={inputMode}
                onPressStart={telegraph.handlePressStart}
                onPressEnd={telegraph.handlePressEnd}
              />
            </div>
          </TabsContent>

          <TabsContent value="microphone" className="mt-0">
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">
                Tap the table to send Morse signals.
              </p>
              <AudioDecoder
                onDecodedTextChange={setAudioDecodedText}
                onRawSequenceChange={setAudioRawSequence}
              />
            </div>
          </TabsContent>
        </div>

        {(previewText.trim() || previewSequence) && (
          <div className="mt-4">
            <TransmissionPreview
              decodedText={previewText}
              rawSequence={previewSequence}
              source={
                activeTab === 'keyboard'
                  ? 'Keyboard'
                  : activeTab === 'microphone'
                  ? 'Microphone'
                  : 'Text'
              }
            />
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button
            onClick={handleSend}
            disabled={isSendDisabled}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            Send Message
          </Button>
        </div>
      </Tabs>
    </Card>
  );
};