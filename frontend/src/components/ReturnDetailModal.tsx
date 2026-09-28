import React, { useState } from 'react';
import { X, Download, Share2 } from 'lucide-react';
import { AgentAnalysisInspector } from './AgentAnalysisInspector';
import { RecommendationDetailPanel } from './RecommendationDetailPanel';

interface ReturnDetailModalProps {
  returnId: string;
  isOpen: boolean;
  onClose: () => void;
  returnData: {
    id: string;
    customerId: string;
    customerName: string;
    orderDate: string;
    returnDate: string;
    sku: string;
    productName: string;
    category: string;
    quantity: number;
    amount: number;
    reason: string;
    comments: string;
    images?: string[];
    classification: {
      result: string;
      confidence: number;
    };
    rootCause: {
      result: string;
      confidence: number;
    };
    fraudScore: number;
    churnRisk: number;
    recommendation: {
      title: string;
      description: string;
      type: string;
      roi: number;
    };
    agentAnalyses: any[];
    processingTime: number;
  };
}

export const ReturnDetailModal: React.FC<ReturnDetailModalProps> = ({
  returnId,
  isOpen,
  onClose,
  returnData,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'recommendation' | 'history'>('overview');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Return #{returnData.id}</h2>
            <p className="text-sm text-gray-600 mt-1">{returnData.customerName} • {returnData.productName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <X size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50 px-6">
          {(['overview', 'agents', 'recommendation', 'history'] as const).map(tab => (
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
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Key Info Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <InfoCard label="Customer" value={returnData.customerName} />
                <InfoCard label="Order Date" value={new Date(returnData.orderDate).toLocaleDateString()} />
                <InfoCard label="Return Date" value={new Date(returnData.returnDate).toLocaleDateString()} />
                <InfoCard label="Amount" value={`$${returnData.amount.toFixed(2)}`} />
              </div>

              {/* Product Details */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-bold text-gray-900 mb-3">Product Information</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-600 font-medium">SKU</p>
                    <p className="text-sm font-mono text-gray-900 mt-1">{returnData.sku}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 font-medium">Product</p>
                    <p className="text-sm text-gray-900 mt-1">{returnData.productName}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 font-medium">Category</p>
                    <p className="text-sm text-gray-900 mt-1">{returnData.category}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 font-medium">Quantity</p>
                    <p className="text-sm text-gray-900 mt-1">{returnData.quantity}</p>
                  </div>
                </div>
              </div>

              {/* Return Reason */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="text-sm font-bold text-gray-900 mb-2">Return Reason</h3>
                <p className="text-sm text-gray-900 font-medium mb-3">{returnData.reason}</p>
                <div className="bg-white p-3 rounded border border-purple-200">
                  <p className="text-sm text-gray-700">"{returnData.comments}"</p>
                </div>
              </div>

              {/* AI Analysis Results */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-gray-900">AI Analysis Results</h3>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-xs text-gray-600 font-medium">Classification</p>
                      <p className="text-sm font-bold text-gray-900 mt-1">{returnData.classification.result}</p>
                    </div>
                    <span className="text-xs font-bold bg-green-600 text-white px-3 py-1 rounded">
                      {(returnData.classification.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                </div>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-xs text-gray-600 font-medium">Root Cause</p>
                      <p className="text-sm font-bold text-gray-900 mt-1">{returnData.rootCause.result}</p>
                    </div>
                    <span className="text-xs font-bold bg-orange-600 text-white px-3 py-1 rounded">
                      {(returnData.rootCause.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-xs text-gray-600 font-medium">Fraud Score</p>
                    <p className="text-lg font-bold text-red-600 mt-1">
                      {(returnData.fraudScore * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="text-xs text-gray-600 font-medium">Churn Risk</p>
                    <p className="text-lg font-bold text-purple-600 mt-1">
                      {(returnData.churnRisk * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'agents' && (
            <AgentAnalysisInspector
              returnId={returnData.id}
              analyses={returnData.agentAnalyses}
              totalTime={returnData.processingTime}
            />
          )}

          {activeTab === 'recommendation' && (
            <RecommendationDetailPanel
              title={returnData.recommendation.title}
              description={returnData.recommendation.description}
              type={returnData.recommendation.type as any}
              impactMetrics={{
                returnsPreventable: 496,
                estimatedSavings: 18848,
                implementationCost: 5000,
                roi: returnData.recommendation.roi,
                confidence: returnData.classification.confidence,
              }}
              calculation={{
                currentReturnRate: 24,
                baselineReturnRate: 3.5,
                effectivenessPercentage: 50,
                affectedUnits: 5200,
                perReturnCost: 38,
              }}
              timeline={{
                implementation: '2 hours',
                testing: '4 hours',
                rollout: 'Immediate',
                roiRealization: 'Within 30 days',
              }}
              risks={[
                {
                  risk: 'Supplier non-compliance',
                  impact: 'high',
                  mitigation: 'Start with internal size chart update',
                },
                {
                  risk: 'Customer adoption',
                  impact: 'medium',
                  mitigation: 'A/B test new sizing with 10% of customers',
                },
              ]}
            />
          )}

          {activeTab === 'history' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-900">Timeline & History</h3>
              <TimelineItem
                time="2:45 PM Today"
                action="Return submitted"
                status="completed"
              />
              <TimelineItem
                time="2:46 PM Today"
                action="Classification agent analyzed return"
                status="completed"
              />
              <TimelineItem
                time="2:46 PM Today"
                action="Root cause analysis performed"
                status="completed"
              />
              <TimelineItem
                time="2:47 PM Today"
                action="Recommendation generated"
                status="completed"
              />
              <TimelineItem
                time="Pending"
                action="Awaiting approval for implementation"
                status="pending"
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3 justify-end">
          <button
            className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition-colors flex items-center gap-2"
          >
            <Download size={18} />
            Export
          </button>
          <button
            className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition-colors flex items-center gap-2"
          >
            <Share2 size={18} />
            Share
          </button>
          <button
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-colors"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

const InfoCard: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
    <p className="text-xs text-gray-600 font-medium">{label}</p>
    <p className="text-sm font-bold text-gray-900 mt-1">{value}</p>
  </div>
);

const TimelineItem: React.FC<{ time: string; action: string; status: 'completed' | 'pending' }> = ({
  time,
  action,
  status,
}) => (
  <div className={`p-4 rounded-lg border ${
    status === 'completed'
      ? 'bg-green-50 border-green-200'
      : 'bg-yellow-50 border-yellow-200'
  }`}>
    <div className="flex items-start gap-3">
      <div className={`w-3 h-3 rounded-full flex-shrink-0 mt-1.5 ${
        status === 'completed' ? 'bg-green-600' : 'bg-yellow-600'
      }`}></div>
      <div className="flex-1">
        <p className="text-sm font-bold text-gray-900">{action}</p>
        <p className="text-xs text-gray-600 mt-1">{time}</p>
      </div>
    </div>
  </div>
);

export default ReturnDetailModal;
