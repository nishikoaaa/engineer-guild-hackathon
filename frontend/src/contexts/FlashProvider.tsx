// FlashProvider.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import FlashMessage from '../components/FlashMessage';
import { FlashMessageProps } from '../components/FlashMessage';

interface FlashContextType {
  showFlash: (message: string, type?: FlashMessageProps['type'], duration?: number) => void;
}

const FlashContext = createContext<FlashContextType | undefined>(undefined);

export const useFlash = (): FlashContextType => {
  const context = useContext(FlashContext);
  if (!context) {
    throw new Error('useFlashはFlashProvider内で使用してください');
  }
  return context;
};

interface FlashProviderProps {
  children: ReactNode;
}

export const FlashProvider: React.FC<FlashProviderProps> = ({ children }) => {
  const [flash, setFlash] = useState<{
    message: string;
    type: FlashMessageProps['type'];
    duration: number;
  } | null>(null);

  const showFlash = (
    message: string,
    type: FlashMessageProps['type'] = 'info',
    duration: number = 3000
  ) => {
    setFlash({ message, type, duration });
  };

  const dismissFlash = () => {
    setFlash(null);
  };

  return (
    <FlashContext.Provider value={{ showFlash }}>
      {children}
      {flash && (
        <FlashMessage
          message={flash.message}
          type={flash.type}
          duration={flash.duration}
          onDismiss={dismissFlash}
        />
      )}
    </FlashContext.Provider>
  );
};