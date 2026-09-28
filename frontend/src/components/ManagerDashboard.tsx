import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, TrendingUp, BarChart3 } from 'lucide-react';

interface ActionItem {
  id: string;
  type: 'recommendation' | 'churn' | 'trend' | 'risk';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  priority: 'critical' | 'high' | 'medium' | 'low';
  dueDate: string;
  owner?: string;
  action: string;
  metrics?: { label: string; value: number | string }[];
}

interface ManagerDashboardProps {
  actionItems: ActionItem[];
  onActionClick?: (item: ActionItem) => void;
  onApprove?: (id: string) => void;
  onDelegate?: (id: string, owner: string) => void;
}

export const ManagerDashboard: React.FC<ManagerDashboardProps> = ({
  actionItems,
  onActionClick,
  onApprove,
  onDelegate,
}) => {
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'completed'>('all');
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  const filteredItems = actionItems.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'critical') return item.priority === 'critical';
    if (filter === 'high') return item.priority === 'high';
    return false;
  });

  const stats = {
    total: actionItems.length,
    critical: actionItems.filter(a => a.priority === 'critical').length,
    pending: actionItems.filter(a => a.priority === 'high' || a.priority === 'critical').length,
    potentialSavings: actionItems.reduce((sum, a) => {
      if (a.metrics) {
        const savingsMetric = a.metrics.find(m => m.label.includes('Savings'));
        if (savingsMetric && typeof savingsMetric.value === 'number') {
          return sum + savingsMetric.value;
        }
      }
      return sum;
    }, 0),
  };


  const getPriorityBg = (priority: string) => {
    return priority === 'critical' ? 'bg-red-50 border-red-200' :
           priority === 'high' ? 'bg-orange-50 border-orange-200' :
           priority === 'medium' ? 'bg-yellow-50 border-yellow-200' :
           'bg-blue-50 border-blue-200';
  };

  const getTypeIcon = (type: string) => {
    return type === 'recommendation' ? '💡' :
           type === 'churn' ? '⚠' :
           type === 'trend' ? '📈' :
           '🚩';
  };

  const getDueStatus = (dueDate: string) => {
    const days = Math.floor((new Date(dueDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'overdue';
    if (days === 0) return 'today';
    if (days <= 2) return 'urgent';
    return 'normal';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar Stats */}
      <div className="lg:col-span-1">
        <div className="space-y-4">
          <StatCard
            label="Total Actions"
            value={stats.total}
            icon={<BarChart3 size={24} className="text-blue-600" />}
            color="blue"
          />
          <StatCard
            label="Critical"
            value={stats.critical}
            icon={<AlertTriangle size={24} className="text-red-600" />}
            color="red"
          />
          <StatCard
            label="Pending Approval"
            value={stats.pending}
            icon={<Clock size={24} className="text-orange-600" />}
            color="orange"
          />
          <StatCard
            label="Potential Savings"
            value={`$${(stats.potentialSavings / 1000000).toFixed(1)}M`}
            icon={<TrendingUp size={24} className="text-green-600" />}
            color="green"
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:col-span-3">
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {/* Header with Filters */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Action Items Requiring Your Attention</h2>
              <span className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full font-bold">
                {filteredItems.length} items
              </span>
            </div>

            <div className="flex gap-2 flex-wrap">
              {(['all', 'critical', 'high'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    filter === f
                      ? 'bg-white border-2 border-blue-600 text-blue-600'
                      : 'bg-white border border-gray-300 text-gray-700 hover:border-gray-400'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Action Items List */}
          <div className="divide-y divide-gray-200 max-h-[800px] overflow-y-auto">
            {filteredItems.map(item => (
              <div
                key={item.id}
                className={`p-4 border-l-4 transition-colors hover:bg-gray-50 cursor-pointer ${getPriorityBg(item.priority)}`}
                onClick={() => {
                  setSelectedItem(selectedItem === item.id ? null : item.id);
                  onActionClick?.(item);
                }}
              >
                {/* Item Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3 flex-1">
                    <span className="text-2xl mt-0.5">{getTypeIcon(item.type)}</span>
                    <div className="flex-1">
                      <p className="font-bold text-gray-900 text-sm">{item.title}</p>
                      <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`text-xs font-bold px-3 py-1 rounded ${
                      item.priority === 'critical' ? 'bg-red-600 text-white' :
                      item.priority === 'high' ? 'bg-orange-600 text-white' :
                      item.priority === 'medium' ? 'bg-yellow-600 text-white' :
                      'bg-blue-600 text-white'
                    }`}>
                      {item.priority.toUpperCase()}
                    </span>
                    <span className={`text-xs font-bold px-3 py-1 rounded ${
                      item.impact === 'high' ? 'bg-purple-600 text-white' :
                      item.impact === 'medium' ? 'bg-blue-600 text-white' :
                      'bg-gray-600 text-white'
                    }`}>
                      {item.impact.toUpperCase()} IMPACT
                    </span>
                  </div>
                </div>

                {/* Item Details */}
                <div className="bg-white/50 rounded p-3 mb-3 border border-gray-300">
                  <p className="text-sm text-gray-700"><span className="font-semibold">Action Required:</span> {item.action}</p>
                </div>

                {/* Metrics */}
                {item.metrics && item.metrics.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                    {item.metrics.map((metric, idx) => (
                      <div key={idx} className="bg-white/50 p-2 rounded border border-gray-300">
                        <p className="text-xs text-gray-600">{metric.label}</p>
                        <p className="text-sm font-bold text-gray-900">{metric.value}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold ${
                      getDueStatus(item.dueDate) === 'overdue' ? 'text-red-600' :
                      getDueStatus(item.dueDate) === 'today' ? 'text-orange-600' :
                      getDueStatus(item.dueDate) === 'urgent' ? 'text-yellow-600' :
                      'text-gray-600'
                    }`}>
                      Due: {new Date(item.dueDate).toLocaleDateString()}
                    </span>
                    {item.owner && (
                      <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                        👤 {item.owner}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {!item.owner && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelegate?.(item.id, 'Current User');
                        }}
                        className="text-xs px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium transition-colors"
                      >
                        Assign to Me
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onApprove?.(item.id);
                      }}
                      className="text-xs px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-white font-medium transition-colors"
                    >
                      ✓ Approve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredItems.length === 0 && (
            <div className="px-6 py-12 text-center">
              <CheckCircle size={48} className="text-green-600 mx-auto mb-3" />
              <p className="text-gray-600 font-semibold">All clear!</p>
              <p className="text-sm text-gray-500 mt-1">No items matching this filter</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const StatCard: React.FC<{
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: 'blue' | 'red' | 'orange' | 'green';
}> = ({ label, value, icon, color }) => {
  const colors = {
    blue: 'bg-blue-50 border-blue-200',
    red: 'bg-red-50 border-red-200',
    orange: 'bg-orange-50 border-orange-200',
    green: 'bg-green-50 border-green-200',
  };

  return (
    <div className={`${colors[color]} border rounded-lg p-4`}>
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-semibold text-gray-600 uppercase">{label}</p>
        {icon}
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
};

export default ManagerDashboard;
