import React from 'react';
import { AlertTriangle, User } from 'lucide-react';

interface EscalationBannerProps {
  isVisible: boolean;
  onClose: () => void;
}

export const EscalationBanner: React.FC<EscalationBannerProps> = ({
  isVisible,
  onClose,
}) => {
  if (!isVisible) return null;

  return (
    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-[#FFC220] p-4 mx-4 mt-4 rounded-lg shadow-sm animate-in slide-in-from-top-2 duration-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#FFC220] rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-800" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              <p className="text-sm font-medium text-gray-800">
                Escalating to Live Agent
              </p>
            </div>
            <p className="text-xs text-gray-600 mt-1">
              A Walmart associate will be with you shortly...
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-[#FFC220] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-[#FFC220] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-[#FFC220] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-sm"
            aria-label="Close escalation banner"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};