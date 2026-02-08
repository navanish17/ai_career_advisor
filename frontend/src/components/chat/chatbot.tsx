import { useState, useRef, useEffect } from 'react';
import { Sparkles, X, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/usechat';
import ChatMessageList from './chatmsglist';
import { ModelType } from './model-selector';
import ChatInput from './chatinput';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState<ModelType>("auto");
  const { messages, isLoading, sendMessage } = useChat();

  // Close on escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 pointer-events-none flex flex-col items-center pb-4">
      {/* Centered Trigger Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className={cn(
            "pointer-events-auto h-12 w-12 rounded-full shadow-2xl z-50",
            "bg-gradient-to-tr from-primary to-purple-600 hover:opacity-90",
            "transition-all duration-300 hover:scale-110 active:scale-95 group"
          )}
          size="icon"
        >
          <Sparkles className="h-6 w-6 text-white group-hover:animate-pulse" />
        </Button>
      )}

      {/* Colab-style Chat Overlay - Theme Responsive */}
      <Card
        className={cn(
          'pointer-events-auto w-[95vw] sm:w-[600px] md:w-[700px] flex flex-col shadow-2xl transition-all duration-500 ease-in-out origin-bottom bg-background border-border text-foreground overflow-hidden',
          isOpen
            ? 'h-[80vh] max-h-[700px] opacity-100 translate-y-0 scale-100'
            : 'h-0 opacity-0 translate-y-10 scale-95 pointer-events-none'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-muted/50">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-medium text-muted-foreground tracking-wider uppercase">Career Pilot AI</span>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-foreground"
              onClick={() => setIsOpen(false)}
            >
              <ChevronDown className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-foreground"
              onClick={() => setIsOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Scrollable Message Area */}
        <div className="flex-1 overflow-hidden">
          <ChatMessageList messages={messages} isLoading={isLoading} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-background">
          <ChatInput
            onSend={(text) => sendMessage(text, selectedModel)}
            isLoading={isLoading}
            selectedModel={selectedModel}
            onModelSelect={setSelectedModel}
          />
        </div>
      </Card>
    </div>
  );
};

export default ChatBot;
