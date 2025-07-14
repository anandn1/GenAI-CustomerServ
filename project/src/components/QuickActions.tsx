import React from 'react';
import { Package, RotateCcw, CreditCard, MapPin, Phone, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  query: string;
}

interface QuickActionsProps {
  onActionClick: (query: string) => void;
  isVisible: boolean;
}

const quickActions: QuickAction[] = [
  {
    id: 'track-order',
    label: 'Track Order',
    icon: <Package className="w-4 h-4" />,
    query: 'I want to track my order'
  },
  {
    id: 'return-item',
    label: 'Return Item',
    icon: <RotateCcw className="w-4 h-4" />,
    query: 'I need to return an item'
  },
  {
    id: 'payment-help',
    label: 'Payment Help',
    icon: <CreditCard className="w-4 h-4" />,
    query: 'I have a question about payment'
  },
  {
    id: 'store-locator',
    label: 'Find Store',
    icon: <MapPin className="w-4 h-4" />,
    query: 'Help me find a nearby Walmart store'
  },
  {
    id: 'contact-support',
    label: 'Contact Support',
    icon: <Phone className="w-4 h-4" />,
    query: 'I need to speak with customer support'
  },
  {
    id: 'product-search',
    label: 'Find Product',
    icon: <Search className="w-4 h-4" />,
    query: 'Help me find a product'
  }
];

export const QuickActions: React.FC<QuickActionsProps> = ({
  onActionClick,
  isVisible,
}) => {
  if (!isVisible) return null;

  return (
    <div className="px-4 py-3 bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => onActionClick(action.query)}
              className={cn(
                "flex flex-col items-center gap-2 p-3 rounded-lg transition-all duration-200",
                "bg-gray-50 dark:bg-gray-800 hover:bg-[#0071CE]/5 dark:hover:bg-[#0071CE]/10",
                "hover:border-[#0071CE]/20 dark:hover:border-[#0071CE]/30 border border-transparent dark:border-gray-700",
                "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1 dark:focus:ring-offset-gray-900",
                "text-gray-700 dark:text-gray-300 hover:text-[#0071CE] dark:hover:text-[#0071CE]"
              )}
            >
              <div className="w-8 h-8 flex items-center justify-center">
                {action.icon}
              </div>
              <span className="text-xs font-medium text-center leading-tight">
                {action.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};