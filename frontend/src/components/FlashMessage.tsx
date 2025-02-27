// FlashMessage.tsx
import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

export interface FlashMessageProps {
  message: string;
  type?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark';
  duration?: number;
  onDismiss?: () => void;
}

const FlashMessage: React.FC<FlashMessageProps> = ({
  message,
  duration = 3000,
  onDismiss,
}) => {
  const [visible, setVisible] = useState<boolean>(true);
  const [fadeOut, setFadeOut] = useState<boolean>(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFadeOut(true);
      setTimeout(() => {
        setVisible(false);
        if (onDismiss) onDismiss();
      }, 1000);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onDismiss]);

  if (!visible) return null;

  return (
    <div
      role="alert"
      style={{
        position: 'fixed',
        top: '1rem',
        right: '1rem',
        minWidth: '250px',
        zIndex: 9999,
        backgroundColor: '#00008B', // 深い青色に設定
        color: 'white',            // 白色の文字に設定
        padding: '1rem',
        borderRadius: '4px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        textAlign: 'center',
        opacity: fadeOut ? 0 : 1,
        transition: 'opacity 1s ease-out',
      }}
    >
      <div className="toast-body">{message}</div>
    </div>
  );
};

export default FlashMessage;