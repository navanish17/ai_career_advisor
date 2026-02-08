import { useState, useCallback, useEffect } from 'react';
import { api } from '@/lib/api';
import type { ChatMessage, ChatResponse } from '@/types/chat';

const STORAGE_KEY = 'chat_messages';
const SESSION_KEY = 'chat_session_id';

// Generate or retrieve session ID
const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
};

// Load messages from localStorage
const loadMessages = (): ChatMessage[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert date strings back to Date objects
      return parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    }
  } catch (e) {
    console.error('Failed to load chat history:', e);
  }
  return [];
};

// Save messages to localStorage (keep last 20 messages = 10 conversations)
const saveMessages = (messages: ChatMessage[]) => {
  try {
    const toSave = messages.slice(-20); // Keep only last 20 messages
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch (e) {
    console.error('Failed to save chat history:', e);
  }
};

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState<string>(getSessionId);

  // Load messages from localStorage on mount
  useEffect(() => {
    const storedMessages = loadMessages();
    if (storedMessages.length > 0) {
      setMessages(storedMessages);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      saveMessages(messages);
    }
  }, [messages]);

  const sendMessage = useCallback(async (content: string, model: string = "auto") => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.post<ChatResponse>('/chatbot/ask', {
        query: content.trim(),
        sessionid: sessionId, // Include session ID for backend tracking
        model: model
      });

      if (response.data) {
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else if (response.error) {
        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again later.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    // Generate new session on clear
    const newSessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, newSessionId);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    sessionId,
  };
};
