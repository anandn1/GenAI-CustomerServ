import React from 'react';
import { BarChart3, Users, MessageSquare, TrendingUp, AlertTriangle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DashboardStats {
  totalChats: number;
  activeUsers: number;
  avgResponseTime: string;
  satisfactionRate: number;
  escalations: number;
  topLanguages: { lang: string; count: number }[];
}

interface AdminDashboardProps {
  isVisible: boolean;
  onClose: () => void;
  stats: DashboardStats;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({
  isVisible,
  onClose,
  stats,
}) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800">Admin Dashboard</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl"
              aria-label="Close dashboard"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-8 h-8 text-[#0071CE]" />
                <div>
                  <p className="text-sm text-gray-600">Total Chats</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.totalChats}</p>
                </div>
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <Users className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Active Users</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.activeUsers}</p>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <Clock className="w-8 h-8 text-[#FFC220]" />
                <div>
                  <p className="text-sm text-gray-600">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.avgResponseTime}</p>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Satisfaction Rate</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.satisfactionRate}%</p>
                </div>
              </div>
            </div>

            <div className="bg-red-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-8 h-8 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600">Escalations</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.escalations}</p>
                </div>
              </div>
            </div>

            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <BarChart3 className="w-8 h-8 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-600">Top Language</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {stats.topLanguages[0]?.lang || 'English'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-800 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">User started chat in Spanish - 2 min ago</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-gray-600">Escalation triggered for order issue - 5 min ago</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600">Voice query processed successfully - 8 min ago</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">Positive feedback received - 12 min ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};