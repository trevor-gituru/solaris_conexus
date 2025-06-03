// components/ui/Toat.tx
'use client';

import { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: number;
  type: ToastType;
  message: string;
}

export default function Toast({
  toasts,
  removeToast,
}: {
  toasts: ToastMessage[];
  removeToast: (id: number) => void;
}) {
  useEffect(() => {
    const timers = toasts.map((toast) =>
      setTimeout(() => removeToast(toast.id), 3000)
    );
    return () => {
      timers.forEach(clearTimeout);
    };
  }, [toasts, removeToast]);

  return (
    <div className="fixed top-4 inset-x-4 sm:inset-x-auto sm:left-1/2 sm:-translate-x-1/2 z-50 space-y-4 sm:max-w-md w-auto max-w-full mx-auto">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            relative w-full px-4 py-3 rounded shadow-lg text-sm font-medium border-l-4 overflow-hidden
            ${
              toast.type === 'success'
                ? 'bg-green-100 text-green-800 border-green-500'
                : toast.type === 'error'
                ? 'bg-red-100 text-red-800 border-red-500'
                : 'bg-blue-100 text-blue-800 border-blue-500'
            }
          `}
        >
          <span>{toast.message}</span>

          {/* Animated shrinking progress bar */}
          <div
            className={`
              absolute bottom-0 left-0 h-1
              ${
                toast.type === 'success'
                  ? 'bg-green-500'
                  : toast.type === 'error'
                  ? 'bg-red-500'
                  : 'bg-blue-500'
              }
              animate-shrink
            `}
          />
        </div>
      ))}

      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
        .animate-shrink {
          animation: shrink 3s linear forwards;
        }
      `}</style>
    </div>
  );
}
