import React, { useState } from 'react';
import { TrendingUp, Target, CheckCircle } from 'lucide-react';

interface RecommendationDetailPanelProps {
  title: string;
  description: string;
  type: 'PRODUCT' | 'SUPPLIER' | 'LOGISTICS' | 'PROCESS' | 'OTHER';
  impactMetrics: {
    returnsPreventable: number;
    estimatedSavings: number;
    implementationCost: number;
    roi: number;
    confidence: number;
  };
  calculation: {
    currentReturnRate: number;
    baselineReturnRate: number;
    effectivenessPercentage: number;
    affectedUnits: number;
    perReturnCost: number;
  };
  timeline: {
    implementation: string;
    testing: string;
    rollout: string;
    roiRealization: string;
  };
  risks: { risk: string; impact: 'high' | 'medium' | 'low'; mitigation: string }[];
  onApprove?: () => void;
  onReject?: () => void;
  onModify?: () => void;
  status?: 'pending' | 'approved' | 'rejected' | 'implemented';
}

export const RecommendationDetailPanel: React.FC<RecommendationDetailPanelProps> = ({
  title,
  description,
  type,
  impactMetrics,
  calculation,
  timeline,
  risks,
  onApprove,
  onReject,
  onModify,
  status = 'pending',
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'calculation' | 'timeline' | 'risks'>('overview');
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);

  const typeColors = {
    PRODUCT: 'bg-blue-50 border-blue-200 text-blue-700',
    SUPPLIER: 'bg-purple-50 border-purple-200 text-purple-700',
    LOGISTICS: 'bg-orange-50 border-orange-200 text-orange-700',
    PROCESS: 'bg-green-50 border-green-200 text-green-700',
    OTHER: 'bg-gray-50 border-gray-200 text-gray-700',
  };

  const statusColors = {
    pending: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    approved: 'bg-green-50 border-green-200 text-green-700',
    rejected: 'bg-red-50 border-red-200 text-red-700',
    implemented: 'bg-blue-50 border-blue-200 text-blue-700',
  };

  const statusIcons = {
    pending: '⏳',
    approved: '✓',
    rejected: '✗',
    implemented: '✓✓',
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-5 border-b border-gray-200">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-2">{title}</h2>
            <p className="text-sm text-gray-700">{description}</p>
          </div>
          <div className="flex gap-2 ml-4">
            <span className={`px-3 py-1 rounded-lg text-xs font-bold border ${typeColors[type]}`}>
              {type}
            </span>
            <span className={`px-3 py-1 rounded-lg text-xs font-bold border ${statusColors[status]}`}>
              {statusIcons[status]} {status.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-600 font-medium">Returns Prevented</p>
            <p className="text-lg font-bold text-gray-900">{impactMetrics.returnsPreventable.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-600 font-medium">Estimated Savings</p>
            <p className="text-lg font-bold text-green-600">${(impactMetrics.estimatedSavings / 1000).toFixed(0)}K</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-600 font-medium">ROI</p>
            <p className="text-lg font-bold text-blue-600">{impactMetrics.roi.toFixed(2)}x</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-600 font-medium">Confidence</p>
            <p className="text-lg font-bold text-purple-600">{(impactMetrics.confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50 px-6">
        {(['overview', 'calculation', 'timeline', 'risks'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 text-sm font-semibold transition-colors border-b-2 ${
              activeTab === tab
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="px-6 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                <Target size={18} className="text-blue-600" />
                Recommendation Summary
              </h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {description}
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                <TrendingUp size={18} className="text-green-600" />
                Expected Impact
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-xs text-gray-600 font-medium mb-1">Impact on Returns</p>
                  <p className="text-2xl font-bold text-green-600">
                    -{((calculation.currentReturnRate - calculation.baselineReturnRate) *
                       calculation.effectivenessPercentage / 100 * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-600 mt-2">
                    From {calculation.currentReturnRate.toFixed(1)}% → {
                      (calculation.currentReturnRate -
                       (calculation.currentReturnRate - calculation.baselineReturnRate) *
                       calculation.effectivenessPercentage / 100).toFixed(1)
                    }%
                  </p>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-xs text-gray-600 font-medium mb-1">Financial Impact</p>
                  <p className="text-2xl font-bold text-blue-600">${(impactMetrics.estimatedSavings / 1000).toFixed(0)}K</p>
                  <p className="text-xs text-gray-600 mt-2">
                    ROI: {impactMetrics.roi.toFixed(2)}x after {impactMetrics.implementationCost / 1000 | 0}K investment
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'calculation' && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 className="text-sm font-bold text-gray-900 mb-4">Impact Calculation Breakdown</h4>

              <div className="space-y-3">
                <CalculationStep
                  label="Current Return Rate"
                  value={`${calculation.currentReturnRate.toFixed(1)}%`}
                  description={`${(calculation.affectedUnits * calculation.currentReturnRate / 100).toFixed(0)} returns out of ${calculation.affectedUnits.toLocaleString()} units`}
                />
                <CalculationStep
                  label="Baseline Return Rate (Industry)"
                  value={`${calculation.baselineReturnRate.toFixed(1)}%`}
                  description="Standard industry average"
                />
                <div className="border-t border-gray-300 pt-3">
                  <CalculationStep
                    label="Preventable Returns (Gap)"
                    value={`${(calculation.currentReturnRate - calculation.baselineReturnRate).toFixed(1)}%`}
                    description={`${((calculation.affectedUnits * (calculation.currentReturnRate - calculation.baselineReturnRate) / 100)).toFixed(0)} returns preventable`}
                  />
                </div>
                <CalculationStep
                  label="Implementation Effectiveness"
                  value={`${calculation.effectivenessPercentage.toFixed(0)}%`}
                  description="Conservative estimate of recommendation success"
                />
                <div className="border-t border-gray-300 pt-3 bg-green-50 rounded p-3">
                  <CalculationStep
                    label="Final Impact"
                    value={`${impactMetrics.returnsPreventable.toLocaleString()} returns`}
                    description={`${((impactMetrics.returnsPreventable / calculation.affectedUnits * 100)).toFixed(1)}% reduction`}
                  />
                </div>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 className="text-sm font-bold text-gray-900 mb-4">ROI Calculation</h4>

              <div className="space-y-3">
                <ROIStep
                  label="Per-Return Cost"
                  value={`$${calculation.perReturnCost.toFixed(0)}`}
                  description="Includes logistics, restocking, replacement"
                />
                <ROIStep
                  label="Returns Prevented"
                  value={impactMetrics.returnsPreventable.toLocaleString()}
                  description="From calculation above"
                />
                <div className="border-t border-blue-300 pt-3">
                  <ROIStep
                    label="Total Savings"
                    value={`$${impactMetrics.estimatedSavings.toLocaleString()}`}
                    description={`${impactMetrics.returnsPreventable} × $${calculation.perReturnCost}`}
                  />
                </div>
                <ROIStep
                  label="Implementation Cost"
                  value={`$${impactMetrics.implementationCost.toLocaleString()}`}
                  description="Designer, QA, testing, communication"
                />
                <div className="border-t border-blue-300 pt-3 bg-white rounded p-3 border">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-gray-900">ROI (Savings / Cost)</span>
                    <span className="text-2xl font-bold text-green-600">{impactMetrics.roi.toFixed(2)}x</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-4">
            <TimelineItem
              phase="Implementation"
              duration={timeline.implementation}
              icon="⚙️"
            />
            <TimelineItem
              phase="Testing"
              duration={timeline.testing}
              icon="🧪"
            />
            <TimelineItem
              phase="Rollout"
              duration={timeline.rollout}
              icon="🚀"
            />
            <TimelineItem
              phase="ROI Realization"
              duration={timeline.roiRealization}
              icon="💰"
              highlighted
            />
          </div>
        )}

        {activeTab === 'risks' && (
          <div className="space-y-3">
            {risks.map((risk, idx) => (
              <div key={idx} className={`rounded-lg p-4 border ${
                risk.impact === 'high' ? 'bg-red-50 border-red-200' :
                risk.impact === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-sm text-gray-900">{risk.risk}</h4>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${
                    risk.impact === 'high' ? 'bg-red-600 text-white' :
                    risk.impact === 'medium' ? 'bg-yellow-600 text-white' :
                    'bg-blue-600 text-white'
                  }`}>
                    {risk.impact.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">
                  <span className="font-medium">Mitigation:</span> {risk.mitigation}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {status === 'pending' && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            onClick={() => setIsApprovalOpen(!isApprovalOpen)}
            className="flex-1 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold text-sm transition-colors"
          >
            ✓ Approve & Implement
          </button>
          <button
            onClick={onReject}
            className="flex-1 px-4 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 font-semibold text-sm border border-red-200 transition-colors"
          >
            ✗ Reject
          </button>
          <button
            onClick={onModify}
            className="flex-1 px-4 py-2 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 font-semibold text-sm border border-blue-200 transition-colors"
          >
            ⚙ Modify
          </button>
        </div>
      )}

      {/* Approval Confirmation */}
      {isApprovalOpen && (
        <div className="px-6 py-4 bg-green-50 border-t border-green-200">
          <div className="flex items-start gap-3 mb-3">
            <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="font-bold text-gray-900 text-sm mb-1">Confirm Implementation</p>
              <p className="text-sm text-gray-700">
                This will schedule the recommendation for implementation with estimated ROI of <span className="font-bold">{impactMetrics.roi.toFixed(2)}x</span>
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setIsApprovalOpen(false);
                onApprove?.();
              }}
              className="flex-1 px-3 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold text-sm transition-colors"
            >
              ✓ Confirm
            </button>
            <button
              onClick={() => setIsApprovalOpen(false)}
              className="flex-1 px-3 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const CalculationStep: React.FC<{ label: string; value: string; description: string }> = ({
  label,
  value,
  description,
}) => (
  <div className="flex justify-between items-start">
    <div>
      <p className="text-xs font-medium text-gray-600">{label}</p>
      <p className="text-xs text-gray-500 mt-1">{description}</p>
    </div>
    <span className="text-sm font-bold text-gray-900 whitespace-nowrap ml-4">{value}</span>
  </div>
);

const ROIStep: React.FC<{ label: string; value: string; description: string }> = ({
  label,
  value,
  description,
}) => (
  <div className="flex justify-between items-start">
    <div>
      <p className="text-xs font-medium text-gray-700">{label}</p>
      <p className="text-xs text-gray-600 mt-1">{description}</p>
    </div>
    <span className="text-sm font-bold text-gray-900 whitespace-nowrap ml-4">{value}</span>
  </div>
);

const TimelineItem: React.FC<{ phase: string; duration: string; icon: string; highlighted?: boolean }> = ({
  phase,
  duration,
  icon,
  highlighted,
}) => (
  <div className={`rounded-lg p-4 border flex items-center gap-4 ${
    highlighted
      ? 'bg-green-50 border-green-200'
      : 'bg-gray-50 border-gray-200'
  }`}>
    <div className="text-2xl">{icon}</div>
    <div className="flex-1">
      <p className="font-semibold text-gray-900">{phase}</p>
      <p className="text-sm text-gray-600">{duration}</p>
    </div>
  </div>
);

export default RecommendationDetailPanel;
