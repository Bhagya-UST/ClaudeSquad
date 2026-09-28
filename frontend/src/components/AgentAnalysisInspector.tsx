import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, Zap, Brain } from 'lucide-react';

interface AgentAnalysis {
  agent: string;
  status: 'complete' | 'pending' | 'error';
  confidence: number;
  processingTime: number;
  tokensUsed: number;
  decision: string;
  reasoning: string;
  evidence: string[];
  alternatives?: { name: string; confidence: number }[];
  metrics?: { [key: string]: number | string };
}

interface AgentAnalysisInspectorProps {
  returnId: string;
  analyses: AgentAnalysis[];
  totalTime: number;
  onFeedback?: (agentName: string, feedback: 'correct' | 'incorrect') => void;
}

export const AgentAnalysisInspector: React.FC<AgentAnalysisInspectorProps> = ({
  returnId,
  analyses,
  totalTime,
  onFeedback,
}) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(analyses[0]?.agent || null);
  const [feedbackGiven, setFeedbackGiven] = useState<{ [key: string]: string }>({});

  const handleFeedback = (agentName: string, feedback: 'correct' | 'incorrect') => {
    setFeedbackGiven(prev => ({ ...prev, [agentName]: feedback }));
    onFeedback?.(agentName, feedback);
  };

  const getStatusColor = (status: string) => {
    return status === 'complete' ? 'text-green-600' :
           status === 'pending' ? 'text-blue-600' :
           'text-red-600';
  };

  const getStatusBg = (status: string) => {
    return status === 'complete' ? 'bg-green-50 border-green-200' :
           status === 'pending' ? 'bg-blue-50 border-blue-200' :
           'bg-red-50 border-red-200';
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Agent Analysis Pipeline</h2>
        <p className="text-sm text-gray-600">Return ID: {returnId} | Total Processing Time: {totalTime.toFixed(2)}s</p>
      </div>

      {/* Timeline Overview */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-gray-900">Execution Timeline</h3>
          <span className="text-xs bg-blue-600 text-white px-3 py-1 rounded">Chain of Agents</span>
        </div>
        <div className="flex gap-1 overflow-x-auto pb-2">
          {analyses.map((analysis, idx) => (
            <div
              key={analysis.agent}
              className="flex flex-col items-center flex-shrink-0"
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xs text-white ${
                analysis.status === 'complete' ? 'bg-green-600' :
                analysis.status === 'pending' ? 'bg-blue-600' :
                'bg-red-600'
              }`}>
                {idx + 1}
              </div>
              <div className="text-xs font-medium text-gray-700 mt-2 text-center w-16 truncate">
                {analysis.agent.split(' ')[0]}
              </div>
              <div className="text-xs text-gray-600">{analysis.processingTime.toFixed(2)}s</div>
              {idx < analyses.length - 1 && (
                <div className="text-gray-400 mt-1">↓</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agent Details */}
      <div className="space-y-3">
        {analyses.map((analysis) => (
          <div
            key={analysis.agent}
            className={`rounded-lg border transition-all ${getStatusBg(analysis.status)}`}
          >
            {/* Header */}
            <button
              onClick={() => setExpandedAgent(expandedAgent === analysis.agent ? null : analysis.agent)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-black/5 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 text-left">
                <div className={`${getStatusColor(analysis.status)}`}>
                  {analysis.status === 'complete' ? (
                    <CheckCircle size={20} />
                  ) : analysis.status === 'pending' ? (
                    <Zap size={20} />
                  ) : (
                    <AlertCircle size={20} />
                  )}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{analysis.agent}</p>
                  <p className="text-xs text-gray-600">
                    Confidence: <span className="font-bold">{(analysis.confidence * 100).toFixed(1)}%</span>
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded font-mono">
                  {analysis.processingTime.toFixed(3)}s
                </span>
                <span className={`text-xs ${expandedAgent === analysis.agent ? 'text-blue-600' : 'text-gray-500'}`}>
                  {expandedAgent === analysis.agent ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </span>
              </div>
            </button>

            {/* Expanded Content */}
            {expandedAgent === analysis.agent && (
              <div className="border-t border-gray-200 px-4 py-4 space-y-4 bg-white rounded-b-lg">
                {/* Decision */}
                <div>
                  <h4 className="text-sm font-bold text-gray-900 mb-2">Decision</h4>
                  <div className="bg-gray-50 border border-gray-200 rounded p-3">
                    <p className="text-sm text-gray-900 font-medium">{analysis.decision}</p>
                  </div>
                </div>

                {/* Reasoning */}
                <div>
                  <h4 className="text-sm font-bold text-gray-900 mb-2">Agent Reasoning</h4>
                  <div className="bg-blue-50 border border-blue-200 rounded p-3">
                    <p className="text-sm text-gray-700 leading-relaxed">{analysis.reasoning}</p>
                  </div>
                </div>

                {/* Evidence */}
                {analysis.evidence.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-2">Evidence Used</h4>
                    <ul className="space-y-2">
                      {analysis.evidence.map((item, idx) => (
                        <li key={idx} className="flex gap-2 text-sm text-gray-700">
                          <span className="text-green-600 font-bold">✓</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Alternatives */}
                {analysis.alternatives && analysis.alternatives.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-2">Alternative Options Considered</h4>
                    <div className="space-y-2">
                      {analysis.alternatives.map((alt, idx) => (
                        <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="text-sm text-gray-700">{alt.name}</span>
                          <span className="text-xs font-mono text-gray-600">
                            {(alt.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metrics */}
                {analysis.metrics && Object.keys(analysis.metrics).length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-2">Performance Metrics</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(analysis.metrics).map(([key, value]) => (
                        <div key={key} className="p-2 bg-gray-50 rounded">
                          <p className="text-xs text-gray-600 capitalize">{key}</p>
                          <p className="text-sm font-bold text-gray-900">{value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Feedback */}
                <div className="border-t border-gray-200 pt-4">
                  <h4 className="text-sm font-bold text-gray-900 mb-3">Provide Feedback</h4>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleFeedback(analysis.agent, 'correct')}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                        feedbackGiven[analysis.agent] === 'correct'
                          ? 'bg-green-600 text-white'
                          : 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100'
                      }`}
                    >
                      ✓ Correct
                    </button>
                    <button
                      onClick={() => handleFeedback(analysis.agent, 'incorrect')}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                        feedbackGiven[analysis.agent] === 'incorrect'
                          ? 'bg-red-600 text-white'
                          : 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
                      }`}
                    >
                      ✗ Incorrect
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <Brain size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-bold text-gray-900 mb-1">Pipeline Summary</p>
            <p className="text-sm text-gray-700">
              All {analyses.length} agents completed analysis in {totalTime.toFixed(2)}s with {
                analyses.filter(a => a.status === 'complete').length
              } successful results. Overall confidence: {
                (analyses.reduce((sum, a) => sum + a.confidence, 0) / analyses.length * 100).toFixed(1)
              }%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentAnalysisInspector;
