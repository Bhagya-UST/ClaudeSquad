import React, { useState } from 'react';
import { AlertCircle, MessageSquare, Phone, Gift, TrendingDown } from 'lucide-react';

interface AtRiskCustomer {
  customerId: string;
  name: string;
  email: string;
  phone?: string;
  ltv: number;
  eqScore: number;
  churnRisk: number;
  emotionalState: string;
  returnsLast30Days: number;
  primarySentiment: string;
  sentiment: string[];
  lastReturn: string;
  interventioneRecommended: string;
  successProbability: number;
  suggestedOffer?: string;
  suggestedMessage?: string;
}

interface AtRiskCustomerHubProps {
  customers: AtRiskCustomer[];
  onIntervention?: (customerId: string, action: string) => void;
}

export const AtRiskCustomerHub: React.FC<AtRiskCustomerHubProps> = ({
  customers,
  onIntervention,
}) => {
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(
    customers[0]?.customerId || null
  );
  const [activeAction, setActiveAction] = useState<string | null>(null);

  const selectedCustomer = customers.find(c => c.customerId === selectedCustomerId);

  const getRiskColor = (risk: number) => {
    if (risk >= 0.8) return 'text-red-600';
    if (risk >= 0.6) return 'text-orange-600';
    return 'text-yellow-600';
  };

  const getRiskBg = (risk: number) => {
    if (risk >= 0.8) return 'bg-red-50 border-red-200';
    if (risk >= 0.6) return 'bg-orange-50 border-orange-200';
    return 'bg-yellow-50 border-yellow-200';
  };

  const getEQColor = (score: number) => {
    if (score <= -4) return 'text-red-600';
    if (score <= -2) return 'text-orange-600';
    if (score <= 0) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Customer List */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-4 py-4 border-b border-gray-200 bg-gradient-to-r from-red-50 to-orange-50">
            <h3 className="text-lg font-bold text-gray-900">At-Risk Customers</h3>
            <p className="text-xs text-gray-600 mt-1">{customers.length} customers flagged</p>
          </div>

          <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
            {customers.map(customer => (
              <button
                key={customer.customerId}
                onClick={() => setSelectedCustomerId(customer.customerId)}
                className={`w-full text-left px-4 py-4 transition-colors ${
                  selectedCustomerId === customer.customerId
                    ? 'bg-blue-50 border-l-4 border-blue-600'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-semibold text-sm text-gray-900">{customer.name}</p>
                    <p className="text-xs text-gray-600">{customer.customerId}</p>
                  </div>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${
                    customer.churnRisk >= 0.8 ? 'bg-red-600 text-white' :
                    customer.churnRisk >= 0.6 ? 'bg-orange-600 text-white' :
                    'bg-yellow-600 text-white'
                  }`}>
                    {(customer.churnRisk * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex gap-4 text-xs">
                  <span className="text-gray-600">LTV: <span className="font-bold text-gray-900">${customer.ltv}</span></span>
                  <span className={`font-bold ${getEQColor(customer.eqScore)}`}>
                    EQ: {customer.eqScore.toFixed(1)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Customer Details & Actions */}
      <div className="lg:col-span-2">
        {selectedCustomer ? (
          <div className="space-y-4">
            {/* Overview Card */}
            <div className={`bg-white rounded-xl border ${getRiskBg(selectedCustomer.churnRisk)} p-6`}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedCustomer.name}</h2>
                  <p className="text-sm text-gray-600 mt-1">{selectedCustomer.email}</p>
                  {selectedCustomer.phone && (
                    <p className="text-sm text-gray-600">{selectedCustomer.phone}</p>
                  )}
                </div>
                <div className={`text-center p-4 rounded-lg ${
                  selectedCustomer.churnRisk >= 0.8 ? 'bg-red-100' :
                  selectedCustomer.churnRisk >= 0.6 ? 'bg-orange-100' :
                  'bg-yellow-100'
                }`}>
                  <p className="text-xs font-bold text-gray-600 mb-1">Churn Risk</p>
                  <p className={`text-3xl font-bold ${getRiskColor(selectedCustomer.churnRisk)}`}>
                    {(selectedCustomer.churnRisk * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-4 border-t border-gray-300">
                <div>
                  <p className="text-xs text-gray-600 font-medium mb-1">Lifetime Value</p>
                  <p className="text-lg font-bold text-gray-900">${selectedCustomer.ltv.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 font-medium mb-1">EQ Score</p>
                  <p className={`text-lg font-bold ${getEQColor(selectedCustomer.eqScore)}`}>
                    {selectedCustomer.eqScore.toFixed(1)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 font-medium mb-1">Returns (30d)</p>
                  <p className="text-lg font-bold text-gray-900">{selectedCustomer.returnsLast30Days}</p>
                </div>
              </div>
            </div>

            {/* Emotional Analysis */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <AlertCircle size={20} className="text-purple-600" />
                Emotional Analysis
              </h3>

              <div className="space-y-4">
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-bold text-gray-900">Primary Sentiment</p>
                    <span className="text-xs font-bold bg-purple-600 text-white px-2 py-1 rounded">
                      {selectedCustomer.emotionalState.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{selectedCustomer.primarySentiment}</p>
                </div>

                <div>
                  <p className="text-xs font-bold text-gray-600 mb-2">DETECTED EMOTIONS</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedCustomer.sentiment.map((emotion, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full border border-gray-300"
                      >
                        {emotion}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs font-medium text-gray-600 mb-1">Why Churn Risk is High?</p>
                  <p className="text-sm text-gray-700">
                    Customer has shown repeated dissatisfaction ({selectedCustomer.returnsLast30Days} returns in 30 days) with increasingly negative sentiment. Without intervention, estimated retention probability: <span className="font-bold">{((1 - selectedCustomer.churnRisk) * 100).toFixed(0)}%</span>
                  </p>
                </div>
              </div>
            </div>

            {/* Intervention Recommendations */}
            <div className="bg-white rounded-xl border border-green-200 bg-green-50 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Gift size={20} className="text-green-600" />
                Recommended Intervention
              </h3>

              <div className="space-y-4">
                <div className="bg-white border border-green-300 rounded-lg p-4">
                  <p className="text-sm font-bold text-gray-900 mb-2">{selectedCustomer.interventioneRecommended}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <TrendingDown size={16} className="text-green-600" />
                    <span className="text-sm text-gray-700">
                      <span className="font-bold">{(selectedCustomer.successProbability * 100).toFixed(0)}%</span> success probability
                    </span>
                  </div>
                </div>

                {selectedCustomer.suggestedOffer && (
                  <div className="bg-white border border-amber-300 rounded-lg p-4">
                    <p className="text-xs font-bold text-gray-600 mb-2">SUGGESTED OFFER</p>
                    <p className="text-sm text-gray-900 font-medium">{selectedCustomer.suggestedOffer}</p>
                  </div>
                )}

                {selectedCustomer.suggestedMessage && (
                  <div className="bg-white border border-blue-300 rounded-lg p-4">
                    <p className="text-xs font-bold text-gray-600 mb-2">MESSAGE TEMPLATE</p>
                    <p className="text-sm text-gray-700 italic">"{selectedCustomer.suggestedMessage}"</p>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Take Action</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button
                  onClick={() => {
                    setActiveAction('call');
                    onIntervention?.(selectedCustomer.customerId, 'call');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    activeAction === 'call'
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white border-blue-200 text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  <Phone size={20} className="mb-2" />
                  <p className="font-semibold text-sm">Call Customer</p>
                  <p className="text-xs opacity-75">Executive outreach</p>
                </button>

                <button
                  onClick={() => {
                    setActiveAction('email');
                    onIntervention?.(selectedCustomer.customerId, 'email');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    activeAction === 'email'
                      ? 'bg-purple-600 border-purple-600 text-white'
                      : 'bg-white border-purple-200 text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <MessageSquare size={20} className="mb-2" />
                  <p className="font-semibold text-sm">Send Email</p>
                  <p className="text-xs opacity-75">Personalized message</p>
                </button>

                <button
                  onClick={() => {
                    setActiveAction('offer');
                    onIntervention?.(selectedCustomer.customerId, 'offer');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    activeAction === 'offer'
                      ? 'bg-green-600 border-green-600 text-white'
                      : 'bg-white border-green-200 text-green-600 hover:bg-green-50'
                  }`}
                >
                  <Gift size={20} className="mb-2" />
                  <p className="font-semibold text-sm">Send Offer</p>
                  <p className="text-xs opacity-75">Loyalty incentive</p>
                </button>

                <button
                  onClick={() => {
                    setActiveAction('escalate');
                    onIntervention?.(selectedCustomer.customerId, 'escalate');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    activeAction === 'escalate'
                      ? 'bg-red-600 border-red-600 text-white'
                      : 'bg-white border-red-200 text-red-600 hover:bg-red-50'
                  }`}
                >
                  <AlertCircle size={20} className="mb-2" />
                  <p className="font-semibold text-sm">Escalate</p>
                  <p className="text-xs opacity-75">Management review</p>
                </button>
              </div>

              {activeAction && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-700 font-medium">
                    ✓ Action "{activeAction.toUpperCase()}" recorded. Follow-up scheduled.
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <p className="text-gray-600">Select a customer to view details</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AtRiskCustomerHub;
