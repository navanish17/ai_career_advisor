import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import ModelSelector, { ModelType } from './model-selector';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  selectedModel: ModelType;
  onModelSelect: (model: ModelType) => void;
}

const ChatInput = ({
  onSend,
  isLoading,
  placeholder = 'What can I help you build?',
  selectedModel,
  onModelSelect
}: ChatInputProps) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  return (
    <div className="relative group">
      <div className={cn(
        "flex flex-col w-full rounded-2xl border bg-muted/30 transition-all duration-200 shadow-sm",
        "border-border group-focus-within:border-primary/50 group-focus-within:ring-1 group-focus-within:ring-primary/20",
        isLoading && "opacity-70 pointer-events-none"
      )}>
        {/* Model/Context Selector */}
        {/* Model/Context Selector */}
        <div className="flex items-center gap-2 px-4 pt-3 pb-1">
          <ModelSelector
            selectedModel={selectedModel}
            onSelect={onModelSelect}
            isLoading={isLoading}
          />
        </div>

        <div className="flex items-end gap-2 px-4 pb-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className={cn(
              "flex-1 bg-transparent border-none focus:ring-0 text-foreground placeholder:text-muted-foreground py-3 px-0 resize-none text-[15px] leading-relaxed min-h-[48px]",
              "scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
            )}
            rows={1}
          />

          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className={cn(
              "h-9 w-9 shrink-0 rounded-xl transition-all duration-300 mb-1",
              input.trim() && !isLoading
                ? "bg-primary text-primary-foreground scale-100"
                : "bg-transparent text-muted-foreground scale-90"
            )}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
