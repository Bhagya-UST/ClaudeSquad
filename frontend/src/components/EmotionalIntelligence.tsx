import React, { useEffect, useState } from 'react';
import { AlertCircle, TrendingUp, Users, Heart, BarChart3 } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AtRiskCustomer {
  customer_id: string;
  eq_score: number;
  churn_probability: number;
  ltv: number;
  recommended_intervention: string;
}

interface SentimentData {
  date: string;
  score: number;
  emotion: string;
}

export const EmotionalIntelligenceDashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [atRiskCustomers, setAtRiskCustomers] = useState<AtRiskCustomer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, customersRes] = await Promise.all([
        fetch('/api/emotional-intelligence/dashboard-summary'),
        fetch('/api/emotional-intelligence/at-risk-customers')
      ]);

      const summaryData = await summaryRes.json();
      const customersData = await customersRes.json();

      setSummary(summaryData.summary);
      setAtRiskCustomers(customersData.at_risk_customers);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching EI data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading Emotional Intelligence Dashboard...</div>;
  }

  if (!summary) {
    return <div className="p-8 text-center text-red-400">Failed to load data</div>;
  }

  return (
    <div className="bg-gray-900 text-white p-8 rounded-lg">
      <h2 className="text-3xl font-bold mb-8">💭 Emotional Intelligence & Churn Risk</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          title="High Churn Risk"
          value={summary.high_churn_risk}
          icon={<AlertCircle className="w-8 h-8 text-red-400" />}
          description="Customers at risk"
        />
        <KPICard
          title="Avg Sentiment Score"
          value={`${summary.avg_sentiment_score.toFixed(1)}/5`}
          icon={<Heart className="w-8 h-8 text-pink-400" />}
          description="Overall sentiment"
        />
        <KPICard
          title="Prevention Rate"
          value={`${(summary.prevention_rate * 100).toFixed(0)}%`}
          icon={<TrendingUp className="w-8 h-8 text-green-400" />}
          description="At-risk retained"
        />
        <KPICard
          title="Churn Rate"
          value={`${(summary.churn_rate * 100).toFixed(1)}%`}
          icon={<Users className="w-8 h-8 text-yellow-400" />}
          description="Monthly churn"
        />
      </div>

      {/* Sentiment Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                { name: 'Very Angry', count: summary.sentiment_distribution.very_angry, color: '#ef4444' },
                { name: 'Angry', count: summary.sentiment_distribution.angry, color: '#f97316' },
                { name: 'Frustrated', count: summary.sentiment_distribution.frustrated, color: '#eab308' },
                { name: 'Neutral', count: summary.sentiment_distribution.neutral, color: '#6b7280' },
                { name: 'Satisfied', count: summary.sentiment_distribution.satisfied, color: '#10b981' },
                { name: 'Delighted', count: summary.sentiment_distribution.delighted, color: '#3b82f6' }
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #444' }} />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4">Intervention Success</h3>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Interventions Completed</span>
                <span className="font-bold text-green-400">{summary.interventions_completed}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: '75%' }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">In Progress</span>
                <span className="font-bold text-blue-400">{summary.interventions_in_progress}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: '15%' }}
                ></div>
              </div>
            </div>

            <div className="border-t border-gray-600 pt-4 mt-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold">Success Rate</span>
                <span className="text-lg font-bold text-yellow-400">
                  {(summary.intervention_success_rate * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {summary.interventions_completed} of {summary.interventions_completed + summary.interventions_in_progress} interventions successful
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* At-Risk Customers */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <AlertCircle size={24} className="text-red-400" />
          Top At-Risk Customers ({atRiskCustomers.length})
        </h3>

        <div className="space-y-4">
          {atRiskCustomers.map((customer) => (
            <div
              key={customer.customer_id}
              className="bg-gray-700 rounded-lg p-4 border-l-4 border-red-500 flex justify-between items-start"
            >
              <div className="flex-1">
                <div className="font-semibold text-lg">{customer.customer_id}</div>
                <div className="text-sm text-gray-400 mt-1">
                  EQ Score: {customer.eq_score.toFixed(1)} | LTV: ${customer.ltv.toLocaleString()} | Churn Probability: {(customer.churn_probability * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-right ml-4">
                <span className="bg-yellow-600 text-white px-3 py-1 rounded text-sm font-semibold">
                  {customer.recommended_intervention}
                </span>
              </div>
            </div>
          ))}
        </div>

        <button className="mt-6 w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-semibold">
          View All At-Risk Customers
        </button>
      </div>

      {/* Risk Categories */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <RiskCategoryCard
          title="High Risk"
          count={summary.high_churn_risk}
          color="red"
          description="EQ < -3.0, immediate action needed"
        />
        <RiskCategoryCard
          title="Medium Risk"
          count={summary.medium_churn_risk}
          color="yellow"
          description="EQ -2.0 to -3.0, monitor closely"
        />
        <RiskCategoryCard
          title="Low Risk"
          count={summary.low_churn_risk}
          color="green"
          description="EQ >= -2.0, retention likely"
        />
      </div>
    </div>
  );
};

const KPICard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description: string;
}> = ({ title, value, icon, description }) => (
  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
    <div className="flex justify-between items-start mb-4">
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <p className="text-3xl font-bold mt-2">{value}</p>
      </div>
      {icon}
    </div>
    <p className="text-xs text-gray-500">{description}</p>
  </div>
);

const RiskCategoryCard: React.FC<{
  title: string;
  count: number;
  color: 'red' | 'yellow' | 'green';
  description: string;
}> = ({ title, count, color, description }) => {
  const colorMap = {
    red: 'bg-red-900/20 border-red-500 text-red-400',
    yellow: 'bg-yellow-900/20 border-yellow-500 text-yellow-400',
    green: 'bg-green-900/20 border-green-500 text-green-400'
  };

  return (
    <div className={`rounded-lg p-6 border ${colorMap[color]}`}>
      <div className="text-3xl font-bold mb-2">{count}</div>
      <h4 className="font-semibold mb-2">{title}</h4>
      <p className="text-sm opacity-90">{description}</p>
    </div>
  );
};

export default EmotionalIntelligenceDashboard;
