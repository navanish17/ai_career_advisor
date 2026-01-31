import { useRef, useEffect } from 'react';
import { User, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ChatMessage } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';

interface ChatMessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

const ChatMessageList = ({ messages, isLoading }: ChatMessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages, isLoading]);

  const handleLinkClick = (href: string) => {
    if (href.startsWith('/')) {
      navigate(href);
    } else {
      window.open(href, '_blank');
    }
  };

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <div className="h-16 w-16 rounded-3xl bg-muted flex items-center justify-center mb-6 shadow-inner border border-border">
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <h3 className="font-semibold text-xl mb-3 text-foreground">Career Pilot AI</h3>
        <p className="text-muted-foreground max-w-[280px] leading-relaxed">
          I'm your personal education & career growth partner. How can I help you today?
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full scrollbar-none" ref={scrollRef}>
      <div className="flex flex-col gap-6 p-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-4 group transition-opacity duration-300',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.role !== 'user' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
            )}

            <div
              className={cn(
                'rounded-2xl px-5 py-3 text-[15px] leading-relaxed shadow-sm max-w-[85%]',
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground font-medium rounded-tr-sm'
                  : 'bg-muted text-foreground border border-border rounded-tl-sm'
              )}
            >
              {message.role === 'user' ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    components={{
                      a: ({ href, children }) => (
                        <button
                          onClick={() => handleLinkClick(href || '#')}
                          className="text-primary underline hover:opacity-80 transition-colors font-medium decoration-primary/30"
                        >
                          {children}
                        </button>
                      ),
                      p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="font-bold text-foreground">{children}</strong>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1.5 text-muted-foreground">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1.5 text-muted-foreground">{children}</ol>,
                      code: ({ children }) => (
                        <code className="px-1.5 py-0.5 rounded bg-muted-foreground/10 text-primary text-[13px] font-mono border border-border">
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted border border-border">
                <User className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4 justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
              <Sparkles className="h-4 w-4 text-primary animate-pulse" />
            </div>
            <div className="rounded-2xl bg-muted border border-border px-5 py-3">
              <div className="flex gap-1.5 items-center h-5">
                <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

export default ChatMessageList;
