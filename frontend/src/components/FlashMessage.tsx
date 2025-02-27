// FlashMessage.tsx
import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

interface FlashMessageProps {
    message: string;
    type?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark';
    duration?: number;
    onDismiss?: () => void;
}

const FlashMessage: React.FC<FlashMessageProps> = ({
    message,
    type = 'info',
    duration = 3000,
    onDismiss,
}) => {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setVisible(false);
            if (onDismiss) onDismiss();
        }, duration);
        return () => clearTimeout(timer);
    }, [duration, onDismiss]);

    if (!visible) return null;

    return (
        <div className={`alert alert-${type}} alert-dismissible fade show`} role="alert">
            {message}
            <button
                type="button"
                className="btn-close"
                onClick={() => {
                    setVisible(false);
                    if (onDismiss) onDismiss();
                }}
                aria-label="Close"
            ></button>
        </div>
    );
};