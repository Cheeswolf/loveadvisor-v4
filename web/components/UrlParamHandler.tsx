'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

interface UrlParamHandlerProps {
  setConfirmationText: (text: string) => void;
  setTextContent: (text: string) => void;
  setUserQuestion: (question: string) => void;
  setInputMode: (mode: 'text' | 'screenshot') => void;
  setShowHistoryLoadedMessage: (show: boolean) => void;
}

export default function UrlParamHandler({
  setConfirmationText,
  setTextContent,
  setUserQuestion,
  setInputMode,
  setShowHistoryLoadedMessage
}: UrlParamHandlerProps) {
  const searchParams = useSearchParams();

  useEffect(() => {
    const chatTextParam = searchParams.get('chat_text');
    const userQuestionParam = searchParams.get('user_question');

    if (chatTextParam) {
      setConfirmationText(chatTextParam);
      setTextContent(chatTextParam);
      setInputMode('text'); // 切换到文本输入模式
      setShowHistoryLoadedMessage(true);

      // 5秒后自动隐藏提示
      const timer = setTimeout(() => {
        setShowHistoryLoadedMessage(false);
      }, 5000);

      return () => clearTimeout(timer);
    }

    if (userQuestionParam) {
      setUserQuestion(userQuestionParam);
    }
  }, [searchParams, setConfirmationText, setTextContent, setUserQuestion, setInputMode, setShowHistoryLoadedMessage]);

  // 此组件不渲染任何可见内容
  return null;
}