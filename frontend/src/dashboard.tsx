import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, TrendingUp, Users, DollarSign, Zap, Shield, MessageCircle, Activity, Layers, Eye, BarChart3 } from 'lucide-react';
import { ChatAgent } from './components/ChatAgent';
import { AgentAnalysisInspector } from './components/AgentAnalysisInspector';
import { RecommendationDetailPanel } from './components/RecommendationDetailPanel';
import { AtRiskCustomerHub } from './components/AtRiskCustomerHub';
import { ReturnSearchFilter } from './components/ReturnSearchFilter';
import { ManagerDashboard } from './components/ManagerDashboard';
import { ReturnDetailModal } from './components/ReturnDetailModal';

// Main Dashboard Component
export const ReturnIQDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [currentCustomerId, setCurrentCustomerId] = useState('CUST_001');
  const [activeView, setActiveView] = useState<'overview' | 'returns' | 'churn' | 'manager'>('overview');
  const [returnDetailOpen, setReturnDetailOpen] = useState(false);
  const [selectedReturnId, setSelectedReturnId] = useState<string | null>(null);

  // Demo data for fallback
  const DEMO_METRICS = {
    classification: { accuracy: 96.2, confidence: 94.8, total_classified: 12450 },
    returns: { total_processed: 12450, processing_rate: 847, avg_latency_ms: 1200 },
    trends: { detected: 15, anomalies: 3, avg_z_score: 2.8 },
    recommendations: { generated: 328, approval_rate: 92.3, implementation_rate: 78.5 },
    llm: { tokens_used: 2847000, avg_latency_ms: 1450, error_rate: 0.2, hallucination_rate: 0.87 },
    churn: { at_risk_customers: 12, prevention_rate: 89.5 },
    guardrails: { pii_masked: 847, hallucinations_detected: 5, bias_alerts: 0, harmful_content: 0 },
    business_impact: { returns_prevented: 847, estimated_savings_usd: 4200000, time_saved_hours: 340 }
  };

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const response = await fetch('/api/metrics/dashboard', { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setMetrics(data);
        setIsDemoMode(false);
      } catch (error) {
        console.warn('API unavailable, using demo data:', error);
        setMetrics(DEMO_METRICS);
        setIsDemoMode(true);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();

    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 300000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-6">
            <div className="inline-block relative w-16 h-16">
              <div className="absolute inset-0 rounded-full animate-spin border-2 border-transparent border-t-blue-500 border-r-purple-500"></div>
              <div className="absolute inset-2 rounded-full animate-pulse bg-gradient-to-r from-blue-500/20 to-purple-500/20"></div>
            </div>
          </div>
          <p className="text-lg text-blue-600 font-semibold">Loading ReturnIQ Dashboard</p>
          <p className="text-sm text-gray-500 mt-2">Initializing AI engines...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50 text-gray-900 overflow-hidden">
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .header-anim {
          animation: slideDown 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .kpi-card {
          animation: fadeInUp 0.5s ease-out forwards;
          opacity: 0;
        }
        .kpi-card:nth-child(1) { animation-delay: 0.1s; }
        .kpi-card:nth-child(2) { animation-delay: 0.2s; }
        .kpi-card:nth-child(3) { animation-delay: 0.3s; }
        .kpi-card:nth-child(4) { animation-delay: 0.4s; }
        .chart-card {
          animation: scaleIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
          opacity: 0;
        }
        .chart-row-1 > div:nth-child(1) { animation-delay: 0.5s; }
        .chart-row-1 > div:nth-child(2) { animation-delay: 0.6s; }
        .chart-row-2 > div:nth-child(1) { animation-delay: 0.7s; }
        .chart-row-2 > div:nth-child(2) { animation-delay: 0.8s; }
        .card-row-3 > div:nth-child(1) { animation-delay: 0.9s; }
        .card-row-3 > div:nth-child(2) { animation-delay: 1s; }
        .card-row-3 > div:nth-child(3) { animation-delay: 1.1s; }
      `}</style>
      {/* Header */}
      <div className="header-anim relative overflow-hidden border-b border-gray-200 bg-white shadow-sm">
        <div className="relative px-8 py-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="w-8 h-8 text-blue-600" />
                  <h1 className="text-4xl font-bold text-gray-900">ReturnIQ</h1>
                </div>
                <p className="text-sm text-gray-500">AI-Powered Return Intelligence Platform</p>
              </div>
              {isDemoMode && (
                <div className="ml-4 px-4 py-2 rounded-lg border border-amber-200 bg-amber-50">
                  <p className="text-xs font-semibold text-amber-700">📊 Demo Mode</p>
                </div>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all border ${
                  autoRefresh
                    ? 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100'
                    : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {autoRefresh ? '● Auto-Refresh' : '○ Paused'}
              </button>
              <button
                onClick={() => setChatOpen(true)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white border border-blue-700 flex items-center gap-2 font-medium text-sm transition-all shadow-sm"
              >
                <MessageCircle size={18} />
                Chat Support
              </button>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex gap-2 border-t border-gray-200 pt-4 -mx-8 px-8 -mb-6">
            {[
              { id: 'overview', label: '📊 Overview', icon: Activity },
              { id: 'returns', label: '🔍 Returns & Approvals', icon: Eye },
              { id: 'churn', label: '⚠️ At-Risk Customers', icon: AlertCircle },
              { id: 'manager', label: '👨‍💼 Manager Dashboard', icon: BarChart3 },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as any)}
                className={`px-4 py-3 rounded-t-lg font-medium text-sm transition-all border-b-2 ${
                  activeView === tab.id
                    ? 'border-blue-600 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content - View-Based */}
      <div className="px-8 py-8">
        {activeView === 'overview' && <OverviewView metrics={metrics} />}
        {activeView === 'returns' && (
          <ReturnsView
            onReturnClick={(id) => {
              setSelectedReturnId(id);
              setReturnDetailOpen(true);
            }}
          />
        )}
        {activeView === 'churn' && <ChurnView />}
        {activeView === 'manager' && <ManagerView />}
      </div>

      {/* Return Detail Modal */}
      <ReturnDetailModal
        returnId={selectedReturnId || ''}
        isOpen={returnDetailOpen}
        onClose={() => {
          setReturnDetailOpen(false);
          setSelectedReturnId(null);
        }}
        returnData={getMockReturnData(selectedReturnId || '')}
      />

      {/* Chat Agent */}
      <ChatAgent
        customerId={currentCustomerId}
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
      />
    </div>
  );
};

// View Components
const OverviewView: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div>
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <div className="kpi-card">
            <KPICard
              title="Classification Accuracy"
              value={`${(metrics?.classification?.accuracy * 100).toFixed(1)}%`}
              target="96%"
              icon={<TrendingUp className="w-6 h-6" />}
              trend="up"
              color="cyan"
            />
          </div>
          <div className="kpi-card">
            <KPICard
              title="Returns Processed"
              value={metrics?.returns?.total_processed?.toLocaleString() || '0'}
              target="1,000+"
              icon={<Zap className="w-6 h-6" />}
              trend="up"
              color="purple"
            />
          </div>
          <div className="kpi-card">
            <KPICard
              title="Hallucination Rate"
              value={`${(metrics?.llm?.hallucination_rate * 100).toFixed(2)}%`}
              target="<1%"
              icon={<Shield className="w-6 h-6" />}
              trend={parseFloat(metrics?.llm?.hallucination_rate) < 0.01 ? 'up' : 'down'}
              color="green"
            />
          </div>
          <div className="kpi-card">
            <KPICard
              title="Estimated Savings"
              value={`$${(metrics?.business_impact?.estimated_savings_usd / 1000000).toFixed(1)}M`}
              target="$2-5M"
              icon={<DollarSign className="w-6 h-6" />}
              trend="up"
              color="pink"
            />
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="chart-row-1 grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          {/* Classification Accuracy Trend */}
          <div className="chart-card">
          <ChartCard title="Classification Accuracy Trend" accent="cyan">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateTrendData('classification_accuracy', 7)} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="day" stroke="#6b7280" />
                <YAxis stroke="#6b7280" domain={[85, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value) => `${(value as number).toFixed(1)}%`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={{ fill: '#2563eb', r: 4 }}
                  fillOpacity={1}
                  fill="url(#colorAccuracy)"
                  name="Accuracy"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          </div>

          {/* Return Categories Distribution */}
          <div className="chart-card">
          <ReturnCategoriesChart />
          </div>

        </div>

        {/* Charts Row 2 */}
        <div className="chart-row-2 grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          {/* Returns Processing Rate */}
          <div className="chart-card">
          <ChartCard title="Returns Processing Rate (per hour)" accent="green">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={generateProcessingData()} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16a34a" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#16a34a" stopOpacity={0.4} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="hour" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Legend />
                <Bar dataKey="count" fill="url(#colorBar)" radius={[6, 6, 0, 0]} name="Returns" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
          </div>

          {/* LLM Latency */}
          <div className="chart-card">
          <ChartCard title="API Latency (p95) - Target: <5s" accent="pink">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateLatencyData()} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#dc2626" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#dc2626" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="time" stroke="#6b7280" />
                <YAxis stroke="#6b7280" domain={[0, 6]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value) => `${(value as number).toFixed(2)}s`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke="#dc2626"
                  strokeWidth={2}
                  dot={{ fill: '#dc2626', r: 4 }}
                  fillOpacity={1}
                  fill="url(#colorLatency)"
                  name="Latency"
                />
                <Line type="monotone" dataKey="target" stroke="#9333ea" strokeDasharray="5 5" strokeWidth={2} name="Target" />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          </div>
        </div>

        {/* Top Trends */}
        <div className="card-row-3 grid grid-cols-1 lg:grid-cols-3 gap-5 mb-8">
          <div className="chart-card">
            <TrendsCard title="Top Trends (This Week)" />
          </div>
          <div className="chart-card">
            <ChurnRiskCard title="At-Risk Customers" />
          </div>
          <div className="chart-card">
            <RecommendationsCard title="Pending Recommendations" />
          </div>
        </div>

        {/* Agents Status */}
        <AgentsStatusCard title="8-Agent System Status" metrics={metrics} />

        {/* Guardrails & Safety */}
        <GuardrailsStatusCard title="Safety Guardrails Status" metrics={metrics} />
      </div>
);

// Returns & Approvals View
const ReturnsView: React.FC<{ onReturnClick: (id: string) => void }> = ({ onReturnClick }) => {
  const demoReturns = [
    {
      id: 'RET_001',
      customerId: 'CUST_001',
      customerName: 'John Smith',
      productName: 'Blue T-Shirt Size M',
      category: 'SIZING',
      amount: 45.99,
      classification: 'SIZING',
      confidence: 0.96,
      roiPotential: 3.77,
      churnRisk: 0.15,
      fraudScore: 0.02,
      status: 'pending' as const,
      returnDate: new Date().toISOString(),
    },
    {
      id: 'RET_002',
      customerId: 'CUST_002',
      customerName: 'Jane Doe',
      productName: 'Red Jeans',
      category: 'QUALITY',
      amount: 89.99,
      classification: 'QUALITY',
      confidence: 0.92,
      roiPotential: 2.45,
      churnRisk: 0.68,
      fraudScore: 0.05,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 86400000).toISOString(),
    },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Returns & Approvals</h2>
      <ReturnSearchFilter
        returns={demoReturns}
        onReturnClick={onReturnClick}
      />
    </div>
  );
};

// Churn Risk View
const ChurnView: React.FC = () => {
  const atRiskCustomers = [
    {
      customerId: 'CUST_12345',
      name: 'Maria Garcia',
      email: 'maria@example.com',
      phone: '(555) 123-4567',
      ltv: 2500,
      eqScore: -4.2,
      churnRisk: 0.92,
      emotionalState: 'VERY FRUSTRATED',
      returnsLast30Days: 3,
      primarySentiment: 'Customer expressed extreme frustration with multiple returns',
      sentiment: ['Anger', 'Frustration', 'Disappointment', 'Resignation'],
      lastReturn: '2 days ago',
      interventioneRecommended: 'Executive Outreach Call',
      successProbability: 0.70,
      suggestedOffer: '$50 Account Credit + Priority Support',
      suggestedMessage: 'We sincerely apologize for your experience. We\'ve reviewed your returns and want to make this right.',
    },
    {
      customerId: 'CUST_67890',
      name: 'Robert Johnson',
      email: 'robert@example.com',
      phone: '(555) 987-6543',
      ltv: 1800,
      eqScore: -3.8,
      churnRisk: 0.85,
      emotionalState: 'FRUSTRATED',
      returnsLast30Days: 2,
      primarySentiment: 'Moderate dissatisfaction, considering alternatives',
      sentiment: ['Frustration', 'Skepticism', 'Disappointment'],
      lastReturn: '5 days ago',
      interventioneRecommended: 'Personalized Email + Loyalty Offer',
      successProbability: 0.65,
      suggestedOffer: '20% off next purchase + Free Shipping',
      suggestedMessage: 'We want to earn back your trust. Here\'s a special offer just for you.',
    },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">At-Risk Customers & Interventions</h2>
      <AtRiskCustomerHub
        customers={atRiskCustomers}
        onIntervention={(customerId, action) => {
          console.log(`Intervention: ${action} for ${customerId}`);
        }}
      />
    </div>
  );
};

// Manager Dashboard View
const ManagerView: React.FC = () => {
  const actionItems = [
    {
      id: 'ACT_001',
      type: 'recommendation' as const,
      title: 'Update Size Chart for SKU #456',
      description: 'Multiple sizing issues detected from Supplier ABC',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date(Date.now() + 86400000).toISOString(),
      owner: 'Sarah Chen',
      action: 'Review and approve size chart update. Expected to prevent 496 returns.',
      metrics: [
        { label: 'Returns Prevented', value: 496 },
        { label: 'Estimated Savings', value: '$18.8K' },
        { label: 'ROI', value: '3.77x' },
        { label: 'Confidence', value: '92%' },
      ],
    },
    {
      id: 'ACT_002',
      type: 'churn' as const,
      title: 'Critical Churn Risk: Maria Garcia (CUST_12345)',
      description: 'High-value customer ($2.5K LTV) at 92% churn risk',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date().toISOString(),
      owner: 'John Doe',
      action: 'Execute executive outreach call within 24 hours',
      metrics: [
        { label: 'Customer LTV', value: '$2,500' },
        { label: 'Churn Risk', value: '92%' },
        { label: 'EQ Score', value: '-4.2' },
        { label: 'Returns (30d)', value: '3' },
      ],
    },
    {
      id: 'ACT_003',
      type: 'trend' as const,
      title: 'Quality Defects from Supplier ABC',
      description: '892 returns in 1 week, 18% DOA rate',
      impact: 'high' as const,
      priority: 'high' as const,
      dueDate: new Date(Date.now() + 172800000).toISOString(),
      owner: 'Mike Wilson',
      action: 'Schedule supplier quality audit and implement corrective actions',
      metrics: [
        { label: 'Returns', value: 892 },
        { label: 'DOA Rate', value: '18%' },
        { label: 'Z-Score', value: '2.8σ' },
        { label: 'Savings Potential', value: '$33.8K' },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Executive Action Items</h2>
      <ManagerDashboard
        actionItems={actionItems}
        onActionClick={(item) => {
          console.log('Clicked item:', item.id);
        }}
        onApprove={(id) => {
          console.log('Approved:', id);
        }}
        onDelegate={(id, owner) => {
          console.log('Delegated to:', owner);
        }}
      />
    </div>
  );
};

// Mock Data Generator
function getMockReturnData(returnId: string) {
  return {
    id: returnId || 'RET_001',
    customerId: 'CUST_001',
    customerName: 'John Smith',
    orderDate: new Date(Date.now() - 30 * 86400000).toISOString(),
    returnDate: new Date().toISOString(),
    sku: 'SKU_456',
    productName: 'Blue T-Shirt Size M',
    category: 'SIZING',
    quantity: 1,
    amount: 45.99,
    reason: 'Shirt runs too small',
    comments: 'I ordered my usual size M but this shirt is significantly smaller than expected. Unworn and with tags.',
    classification: { result: 'SIZING', confidence: 0.96 },
    rootCause: { result: 'Supplier fabric change - 2% shrinkage', confidence: 0.88 },
    fraudScore: 0.02,
    churnRisk: 0.15,
    recommendation: {
      title: 'Update size chart for SKU #456',
      description: 'Adjust sizing measurements and communicate updated fit guide to customers',
      type: 'PRODUCT',
      roi: 3.77,
    },
    agentAnalyses: [
      {
        agent: 'Classifier',
        status: 'complete' as const,
        confidence: 0.96,
        processingTime: 2.3,
        tokensUsed: 334,
        decision: 'SIZING',
        reasoning: 'Customer explicitly stated sizing complaint with unworn condition',
        evidence: [
          'Customer text: "Shirt runs too small"',
          'Product condition: Unworn with tags',
          'Size ordered: M (usual size)',
        ],
        alternatives: [
          { name: 'OTHER', confidence: 0.03 },
          { name: 'QUALITY', confidence: 0.01 },
        ],
        metrics: {
          'Confidence': '96%',
          'API Tokens': 334,
          'Latency': '2.3s',
        },
      },
      {
        agent: 'Root Cause Analysis',
        status: 'complete' as const,
        confidence: 0.88,
        processingTime: 3.1,
        tokensUsed: 456,
        decision: 'Supplier fabric change causing shrinkage',
        reasoning: 'Multiple SKUs from same supplier showing 24% return rate spike',
        evidence: [
          'SKU 456, 457, 458 all from Supplier ABC',
          'Return rate increased from 5% to 24% in 1 week',
          'Supplier recently changed fabric supplier',
          '1,243 total affected returns',
        ],
        alternatives: [
          { name: 'Size chart error', confidence: 0.08 },
          { name: 'Manufacturing defect', confidence: 0.04 },
        ],
        metrics: {
          'Confidence': '88%',
          'Pattern strength': '92%',
          'Evidence count': '4',
        },
      },
    ],
    processingTime: 12.3,
  };
}

// KPI Card Component with clean styling
const KPICard: React.FC<{
  title: string;
  value: string;
  target: string;
  icon: React.ReactNode;
  trend: 'up' | 'down';
  color: 'cyan' | 'purple' | 'green' | 'pink';
}> = ({ title, value, target, icon, trend, color }) => {
  const colors = {
    cyan: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-600 bg-blue-100', text: 'text-blue-700' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', icon: 'text-purple-600 bg-purple-100', text: 'text-purple-700' },
    green: { bg: 'bg-green-50', border: 'border-green-200', icon: 'text-green-600 bg-green-100', text: 'text-green-700' },
    pink: { bg: 'bg-pink-50', border: 'border-pink-200', icon: 'text-pink-600 bg-pink-100', text: 'text-pink-700' },
  };

  const style = colors[color];

  return (
    <div className={`group relative ${style.bg} ${style.border} rounded-xl p-6 border transition-all duration-300 hover:shadow-md hover:border-opacity-50`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{title}</p>
          <p className="text-4xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${style.icon}`}>
          {icon}
        </div>
      </div>
      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <span className="text-xs text-gray-600 font-medium">Target: {target}</span>
        <span className={`font-semibold text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {trend === 'up' ? '↗ Up' : '↘ Down'}
        </span>
      </div>
    </div>
  );
};

// Chart Card Component with clean styling
const ChartCard: React.FC<{ title: string; children: React.ReactNode; accent?: 'cyan' | 'purple' | 'green' | 'pink' }> = ({ title, children, accent = 'cyan' }) => {
  const accentBorders = {
    cyan: 'border-blue-200',
    purple: 'border-purple-200',
    green: 'border-green-200',
    pink: 'border-pink-200',
  };

  return (
    <div className={`bg-white rounded-xl p-6 border ${accentBorders[accent]} transition-all duration-300 hover:shadow-md overflow-hidden`}>
      <h3 className="text-lg font-bold mb-6 text-gray-900">{title}</h3>
      {children}
    </div>
  );
};

// Trends Card
const TrendsCard: React.FC<{ title: string }> = ({ title }) => (
  <div className="bg-white rounded-xl p-6 border border-blue-200 transition-all duration-300 hover:shadow-md">
    <h3 className="text-lg font-bold mb-6 text-gray-900">{title}</h3>
    <div className="space-y-4">
      <TrendItem
        title="Sizing issues with SKU #456"
        count={1243}
        zScore={3.2}
        impact="24% return rate"
      />
      <TrendItem
        title="Quality defects from Supplier ABC"
        count={892}
        zScore={2.8}
        impact="18% DOA rate"
      />
      <TrendItem
        title="Logistics damage - Carrier XYZ"
        count={567}
        zScore={2.1}
        impact="12% damage rate"
      />
    </div>
  </div>
);

const TrendItem: React.FC<{ title: string; count: number; zScore: number; impact: string }> = ({
  title,
  count,
  zScore,
  impact,
}) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 transition-all duration-300 hover:shadow-sm group">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <p className="font-semibold text-sm text-gray-900">{title}</p>
        <div className="flex gap-4 mt-2 text-xs text-gray-600">
          <span>📊 {count.toLocaleString()} returns</span>
          <span>🔬 Z-score: {zScore.toFixed(1)}σ</span>
          <span className="text-amber-600 font-medium">📈 {impact}</span>
        </div>
      </div>
      <span className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-lg text-xs font-semibold transition-all">⚠ Alert</span>
    </div>
  </div>
);

// Churn Risk Card
const ChurnRiskCard: React.FC<{ title: string }> = ({ title }) => (
  <div className="bg-white rounded-xl p-6 border border-purple-200 transition-all duration-300 hover:shadow-md">
    <h3 className="text-lg font-bold mb-6 flex items-center gap-3 text-gray-900">
      <AlertCircle className="w-5 h-5 text-purple-600" />
      {title}
    </h3>
    <div className="space-y-3 mb-4">
      <ChurnItem customerId="CUST_12345" eqScore={-4.2} ltv={2500} intervention="Proactive outreach" />
      <ChurnItem customerId="CUST_67890" eqScore={-3.8} ltv={1800} intervention="Loyalty coupon" />
      <ChurnItem customerId="CUST_11111" eqScore={-3.5} ltv={3200} intervention="Executive call" />
    </div>
    <button className="mt-4 w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all">
      View All (15)
    </button>
  </div>
);

const ChurnItem: React.FC<{ customerId: string; eqScore: number; ltv: number; intervention: string }> = ({
  customerId,
  eqScore,
  ltv,
  intervention,
}) => (
  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 transition-all duration-300 hover:shadow-sm">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <p className="font-semibold text-sm text-gray-900">{customerId}</p>
        <p className="text-xs text-gray-600 mt-2">EQ Score: <span className="text-purple-600 font-semibold">{eqScore.toFixed(1)}</span> | LTV: <span className="text-blue-600 font-semibold">${ltv.toLocaleString()}</span></p>
      </div>
      <span className="text-xs bg-amber-600 hover:bg-amber-700 text-white px-3 py-1 rounded-lg font-semibold transition-all">{intervention}</span>
    </div>
  </div>
);

// Recommendations Card
const RecommendationsCard: React.FC<{ title: string }> = ({ title }) => (
  <div className="bg-white rounded-xl p-6 border border-green-200 transition-all duration-300 hover:shadow-md">
    <h3 className="text-lg font-bold mb-6 text-gray-900">{title}</h3>
    <div className="space-y-3 mb-4">
      <RecItem
        type="PRODUCT"
        action="Update size chart for SKU #456"
        impact="40% reduction"
        confidence={0.92}
      />
      <RecItem
        type="SUPPLIER"
        action="Audit QC with Supplier ABC"
        impact="60% reduction"
        confidence={0.88}
      />
      <RecItem
        type="LOGISTICS"
        action="Switch to Carrier XYZ"
        impact="25% reduction"
        confidence={0.81}
      />
    </div>
    <button className="mt-4 w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all">
      View All (28)
    </button>
  </div>
);

const RecItem: React.FC<{ type: string; action: string; impact: string; confidence: number }> = ({
  type,
  action,
  impact,
  confidence,
}) => (
  <div className="bg-green-50 border border-green-200 rounded-lg p-4 transition-all duration-300 hover:shadow-sm">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <span className="text-xs font-bold text-green-700 uppercase tracking-wider">{type}</span>
        <p className="text-sm mt-2 text-gray-900 font-medium">{action}</p>
        <div className="flex gap-3 mt-3 text-xs text-gray-600">
          <span>📊 {impact}</span>
          <span>🎯 <span className="text-green-600 font-semibold">{(confidence * 100).toFixed(0)}%</span> confidence</span>
        </div>
      </div>
      <button className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-lg text-xs font-semibold transition-all ml-3 flex-shrink-0">
        ✓ Approve
      </button>
    </div>
  </div>
);

// Agents Status Card
const AgentsStatusCard: React.FC<{ title: string; metrics: any }> = ({ title, metrics }) => (
  <div className="bg-white rounded-xl p-6 border border-blue-200 transition-all duration-300 hover:shadow-md mb-8">
    <h3 className="text-lg font-bold mb-6 text-gray-900">{title}</h3>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[
        { name: 'Classifier', accuracy: 96.2, status: 'healthy' },
        { name: 'Root Cause', accuracy: 92.1, status: 'healthy' },
        { name: 'Trends', accuracy: 94.5, status: 'healthy' },
        { name: 'Anomaly', accuracy: 91.8, status: 'healthy' },
        { name: 'Fraud', accuracy: 89.3, status: 'healthy' },
        { name: 'Recommendations', accuracy: 85.7, status: 'healthy' },
        { name: 'Validation', accuracy: 98.1, status: 'healthy' },
        { name: 'Human Review', accuracy: 100, status: 'healthy' },
      ].map((agent) => (
        <div key={agent.name} className="bg-green-50 rounded-lg p-4 border border-green-200 transition-all duration-300 hover:shadow-sm">
          <div className="flex justify-between items-start mb-3">
            <span className="font-semibold text-sm text-gray-900">{agent.name}</span>
            <span className="text-xs bg-green-600 text-white px-2 py-1 rounded font-bold">✓</span>
          </div>
          <div className="text-3xl font-bold text-green-600">{agent.accuracy.toFixed(1)}%</div>
          <div className="text-xs text-gray-600 mt-2 capitalize font-medium">{agent.status}</div>
        </div>
      ))}
    </div>
  </div>
);

// Guardrails Status Card
const GuardrailsStatusCard: React.FC<{ title: string; metrics: any }> = ({ title, metrics }) => (
  <div className="bg-white rounded-xl p-6 border border-pink-200 transition-all duration-300 hover:shadow-md">
    <h3 className="text-lg font-bold mb-6 text-gray-900">{title}</h3>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <GuardrailStatus
        name="PII Protection"
        status="active"
        records={metrics?.guardrails?.pii_masked_count || 0}
      />
      <GuardrailStatus
        name="Hallucination Detection"
        status={parseFloat(metrics?.llm?.hallucination_rate) < 0.01 ? 'passing' : 'warning'}
        rate={`${(metrics?.llm?.hallucination_rate * 100).toFixed(2)}%`}
      />
      <GuardrailStatus
        name="Fairness & Bias"
        status="passing"
        checks="8/8 passed"
      />
      <GuardrailStatus
        name="Content Filtering"
        status="active"
        items="0 harmful items detected"
      />
    </div>
  </div>
);

const GuardrailStatus: React.FC<{ name: string; status: string; [key: string]: any }> = ({
  name,
  status,
  ...data
}) => {
  const styles = {
    active: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      badge: 'bg-green-600 text-white hover:bg-green-700',
    },
    passing: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      badge: 'bg-blue-600 text-white hover:bg-blue-700',
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      badge: 'bg-amber-600 text-white hover:bg-amber-700',
    },
  };

  const style = styles[status as keyof typeof styles] || styles.active;

  return (
    <div className={`rounded-lg p-4 border transition-all duration-300 ${style.bg} ${style.border} hover:shadow-sm`}>
      <div className="flex justify-between items-center">
        <h4 className="font-semibold text-gray-900">{name}</h4>
        <span className={`text-xs font-bold px-3 py-1 rounded uppercase tracking-wide ${style.badge} transition-all`}>
          {status === 'active' ? '● Active' : status === 'passing' ? '✓ Passing' : '⚠ Warning'}
        </span>
      </div>
      <div className="mt-3 text-sm text-gray-600">
        {Object.entries(data).map(([key, value]) => (
          key !== 'name' && key !== 'status' && <p key={key} className="text-gray-600">{value}</p>
        ))}
      </div>
    </div>
  );
};

// Interactive Return Categories Chart Component
const ReturnCategoriesChart: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());

  const categories = [
    { name: 'Sizing', value: 35, label: 'Sizing Issues', gradId: 'gradCyan', color: '#00d9ff' },
    { name: 'Quality', value: 25, label: 'Quality Defects', gradId: 'gradPurple', color: '#b00fff' },
    { name: 'Defective', value: 15, label: 'Defective Items', gradId: 'gradPink', color: '#ff006e' },
    { name: 'Fraud', value: 10, label: 'Fraud Detected', gradId: 'gradBlue', color: '#0088ff' },
    { name: 'Logistics', value: 8, label: 'Logistics Issues', gradId: 'gradAmber', color: '#ffaa00' },
    { name: 'Other', value: 7, label: 'Other Reasons', gradId: 'gradGreen', color: '#00ff88' },
  ];

  const legendItems = [
    { name: 'Sizing', bg: 'bg-cyan-500' },
    { name: 'Quality', bg: 'bg-purple-500' },
    { name: 'Defective', bg: 'bg-pink-500' },
    { name: 'Fraud', bg: 'bg-blue-500' },
    { name: 'Logistics', bg: 'bg-amber-500' },
    { name: 'Other', bg: 'bg-green-500' },
  ];

  const toggleFilter = (name: string) => {
    const newFilters = new Set(activeFilters);
    if (newFilters.has(name)) {
      newFilters.delete(name);
    } else {
      newFilters.add(name);
    }
    setActiveFilters(newFilters);
  };

  const filteredData = activeFilters.size > 0
    ? categories.filter(cat => activeFilters.has(cat.name))
    : categories;

  const displayData = filteredData.length > 0 ? filteredData : categories;
  const totalValue = displayData.reduce((sum, cat) => sum + cat.value, 0);

  return (
    <ChartCard title="Return Categories Distribution" accent="purple">
      <div className="space-y-5">
        {/* Chart */}
        <div className="animate-in fade-in zoom-in duration-500 flex gap-8">
          <div className="flex-1">
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <defs>
                  <linearGradient id="gradCyan" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#2563eb" />
                    <stop offset="100%" stopColor="#0ea5e9" />
                  </linearGradient>
                  <linearGradient id="gradPurple" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#9333ea" />
                    <stop offset="100%" stopColor="#a78bfa" />
                  </linearGradient>
                  <linearGradient id="gradPink" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#dc2626" />
                    <stop offset="100%" stopColor="#f87171" />
                  </linearGradient>
                  <linearGradient id="gradBlue" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#06b6d4" />
                    <stop offset="100%" stopColor="#22d3ee" />
                  </linearGradient>
                  <linearGradient id="gradAmber" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#d97706" />
                    <stop offset="100%" stopColor="#fbbf24" />
                  </linearGradient>
                  <linearGradient id="gradGreen" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#16a34a" />
                    <stop offset="100%" stopColor="#4ade80" />
                  </linearGradient>
                </defs>
                <Pie
                  data={displayData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ value, percent }) => {
                    const percentage = (percent * 100).toFixed(0);
                    return `${percentage}%`;
                  }}
                  outerRadius={100}
                  innerRadius={50}
                  paddingAngle={3}
                  dataKey="value"
                  onClick={(data: any) => setSelectedCategory(selectedCategory === data.name ? null : data.name)}
                >
                  {displayData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.gradId === 'gradCyan' ? 'url(#gradCyan)'
                          : entry.gradId === 'gradPurple' ? 'url(#gradPurple)'
                          : entry.gradId === 'gradPink' ? 'url(#gradPink)'
                          : entry.gradId === 'gradBlue' ? 'url(#gradBlue)'
                          : entry.gradId === 'gradAmber' ? 'url(#gradAmber)'
                          : 'url(#gradGreen)'}
                      stroke={selectedCategory === entry.name ? '#1f2937' : '#ffffff'}
                      strokeWidth={selectedCategory === entry.name ? 4 : 2}
                      style={{
                        cursor: 'pointer',
                        opacity: activeFilters.size === 0 || activeFilters.has(entry.name) ? 1 : 0.3,
                        transition: 'all 0.3s ease',
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    padding: '8px 12px',
                  }}
                  formatter={(value: any, name: string, props: any) => {
                    const numValue = typeof value === 'number' ? value : 0;
                    const percentage = (numValue / totalValue * 100).toFixed(1);
                    return [
                      <span key="val" style={{ color: '#000', fontWeight: 'bold' }}>
                        {numValue} returns ({percentage}%)
                      </span>,
                      props.payload.name
                    ];
                  }}
                  labelStyle={{ color: '#000' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Data Table */}
          <div className="w-48 bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="text-sm font-bold text-gray-900 mb-3">Return Breakdown</h4>
            <div className="space-y-2">
              {categories.map((cat) => {
                const isVisible = activeFilters.size === 0 || activeFilters.has(cat.name);
                return (
                  <div
                    key={cat.name}
                    className={`flex items-center justify-between text-xs p-2 rounded transition-opacity ${
                      isVisible ? 'opacity-100' : 'opacity-40'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        cat.name === 'Sizing' ? 'bg-blue-500' :
                        cat.name === 'Quality' ? 'bg-purple-500' :
                        cat.name === 'Defective' ? 'bg-red-500' :
                        cat.name === 'Fraud' ? 'bg-cyan-500' :
                        cat.name === 'Logistics' ? 'bg-amber-500' :
                        'bg-green-500'
                      }`}></div>
                      <span className="font-medium text-gray-700">{cat.name}</span>
                    </div>
                    <span className="font-bold text-gray-900">{cat.value}%</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-3 border-t border-gray-300">
              <div className="flex justify-between text-xs font-bold text-gray-900">
                <span>Total</span>
                <span>100%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Legend */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wider">Filter Categories</p>
            {activeFilters.size > 0 && (
              <button
                onClick={() => setActiveFilters(new Set())}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
              >
                Show All
              </button>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {legendItems.map((item) => (
              <button
                key={item.name}
                onClick={() => toggleFilter(item.name)}
                className={`group flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-300 ${
                  activeFilters.size === 0 || activeFilters.has(item.name)
                    ? 'bg-gray-50 border-gray-300 hover:border-gray-400 hover:bg-gray-100'
                    : 'bg-gray-100 border-gray-300 opacity-50 hover:opacity-70'
                }`}
              >
                <div className={`w-3 h-3 rounded-full ${item.bg} flex-shrink-0`}></div>
                <span className="text-xs text-gray-700 font-medium">{item.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Info */}
        {selectedCategory && (
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 animate-in fade-in duration-300">
            <p className="text-sm text-gray-700">
              <span className="text-blue-600 font-bold">{selectedCategory}</span>
              <span className="mx-2">—</span>
              <span className="font-bold text-gray-900">
                {categories.find(c => c.name === selectedCategory)?.value}%
              </span>
              <span className="text-gray-600 ml-1">of all returns</span>
            </p>
          </div>
        )}
      </div>
    </ChartCard>
  );
};

// Helper functions
function generateTrendData(_metric: string, days: number) {
  const data = [];
  for (let i = 0; i < days; i++) {
    data.push({
      day: `Day ${i + 1}`,
      value: 94 + Math.random() * 3,
    });
  }
  return data;
}

function generateProcessingData() {
  return Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    count: 50 + Math.random() * 100,
  }));
}

function generateLatencyData() {
  return Array.from({ length: 20 }, (_, i) => ({
    time: `${i * 5}m`,
    latency: 3 + Math.random() * 2,
    target: 5,
  }));
}

export default ReturnIQDashboard;
