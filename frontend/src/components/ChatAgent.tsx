import React, { useState, useEffect, useRef } from 'react';
import { Send, X, AlertCircle } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  actions?: any;
}

interface ChatAgentProps {
  customerId: string;
  isOpen: boolean;
  onClose: () => void;
  metrics?: any;
}

export const ChatAgent: React.FC<ChatAgentProps> = ({ customerId, isOpen, onClose, metrics }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'agent',
      content: 'Hi! I\'m your ReturnIQ Insights Agent. I can help you analyze trends, understand metrics, and get actionable recommendations from your dashboard. What would you like to know?',
      timestamp: new Date().toISOString(),
    },
  ]);

  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [escalationFlag, setEscalationFlag] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Setup WebSocket connection
  useEffect(() => {
    if (isOpen && !wsRef.current) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/chat/ws/${customerId}`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'stream') {
          // Append streaming text to last agent message
          setMessages((prev) => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.role === 'agent') {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMsg,
                  content: lastMsg.content + data.data,
                },
              ];
            }
            return prev;
          });
        } else if (data.type === 'complete') {
          setLoading(false);
        } else if (data.type === 'escalation') {
          setEscalationFlag(true);
        }
      };

      return () => {
        if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
        }
      };
    }
  }, [isOpen, customerId]);

  // Call AI backend service for intelligent insights
  const generateAgentResponse = async (userQuery: string): Promise<string> => {
    try {
      const response = await fetch('/api/chat/insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: customerId,
          user_query: userQuery,
          dashboard_metrics: metrics,
        }),
      });

      if (!response.ok) throw new Error('API error');

      const data = await response.json();
      return data.insight || 'Unable to generate insight. Please try again.';
    } catch (error) {
      console.error('Insight generation error:', error);
      return 'I encountered an error analyzing your question. Please try again.';
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    const userQuery = inputValue;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userQuery,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      // Get AI-powered insight from backend
      const agentResponse = await generateAgentResponse(userQuery);

      const agentMessage: ChatMessage = {
        id: (Date.now() + Math.random()).toString(),
        role: 'agent',
        content: agentResponse,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error generating response:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + Math.random()).toString(),
        role: 'agent',
        content: 'I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleEscalate = async () => {
    try {
      const lastUserMsg = messages.filter((m) => m.role === 'user').pop()?.content || '';
      const reason = `Customer requested escalation. Last message: ${lastUserMsg}`;

      await fetch(`/api/chat/escalate/${customerId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, last_message: lastUserMsg }),
      });

      // Add system message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'agent',
          content: '✓ Your issue has been escalated to our support team. A human agent will contact you shortly.',
          timestamp: new Date().toISOString(),
        },
      ]);

      setEscalationFlag(false);
    } catch (error) {
      console.error('Escalation error:', error);
    }
  };

  const handleGetSolutions = async () => {
    try {
      const lastUserMsg = messages.filter((m) => m.role === 'user').pop()?.content || '';

      const response = await fetch('/api/chat/suggest-solutions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: customerId,
          issue_summary: lastUserMsg,
        }),
      });

      const data = await response.json();
      setSuggestions(data.solutions);
    } catch (error) {
      console.error('Solutions error:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-0 right-0 w-96 h-[600px] bg-gradient-to-br from-slate-900/60 to-slate-950/80 backdrop-blur-xl rounded-tl-2xl rounded-tr-2xl border border-cyan-500/30 flex flex-col z-50 overflow-hidden shadow-2xl" style={{ boxShadow: '0 0 40px rgba(0, 217, 255, 0.2)' }}>
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 text-white p-4 rounded-tl-2xl rounded-tr-2xl flex justify-between items-center shadow-lg border-b border-cyan-500/30">
        <div>
          <h3 className="font-bold text-lg">ReturnIQ Support</h3>
          <p className="text-xs opacity-90">AI-powered customer care</p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-lg transition-all"
        >
          <X size={20} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-slate-950 to-slate-900/80">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-xs px-4 py-3 rounded-xl backdrop-blur-xl ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-cyan-600 to-cyan-700 text-white rounded-br-none border border-cyan-500/50 shadow-lg'
                  : 'bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-cyan-500/20 text-gray-100 rounded-bl-none shadow-md'
              }`}
              style={msg.role === 'user' ? {} : { boxShadow: '0 0 20px rgba(0, 217, 255, 0.1)' }}
            >
              <p className="text-sm leading-relaxed">{msg.content}</p>
              {msg.actions && (
                <div className="mt-2 text-xs space-y-1">
                  {msg.actions.provide_refund && (
                    <div className="flex items-center gap-1 text-yellow-600">
                      <AlertCircle size={14} /> Refund may be available
                    </div>
                  )}
                  {msg.actions.quality_review && (
                    <div className="flex items-center gap-1 text-red-600">
                      <AlertCircle size={14} /> Quality concern noted
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-cyan-500/30 px-4 py-3 rounded-xl rounded-bl-none backdrop-blur" style={{ boxShadow: '0 0 20px rgba(0, 217, 255, 0.1)' }}>
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '100ms' }} />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Escalation Alert */}
      {escalationFlag && (
        <div className="bg-gradient-to-r from-amber-600/20 to-orange-600/20 border-t border-amber-500/30 p-3 flex items-center gap-2 backdrop-blur">
          <AlertCircle size={18} className="text-amber-400 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-amber-200">
              Would you like to escalate this to a human agent?
            </p>
          </div>
          <button
            onClick={handleEscalate}
            className="px-3 py-1 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-lg text-sm font-medium flex-shrink-0 transition-all"
          >
            Escalate
          </button>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="bg-gradient-to-b from-cyan-900/20 to-blue-900/20 border-t border-cyan-500/30 p-3 max-h-32 overflow-y-auto backdrop-blur">
          <p className="text-xs font-semibold text-cyan-300 mb-2 uppercase">💡 Suggested Solutions:</p>
          <div className="space-y-2">
            {suggestions.slice(0, 2).map((sol, idx) => (
              <div key={idx} className="text-xs bg-slate-900/60 p-2 rounded-lg border border-cyan-500/30 backdrop-blur">
                <p className="font-semibold text-cyan-300">{sol.title}</p>
                <p className="text-gray-400 text-xs mt-1">{sol.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSendMessage}
        className="border-t border-cyan-500/20 p-3 bg-gradient-to-b from-slate-900/50 to-slate-950 rounded-bl-2xl rounded-br-2xl flex gap-2"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 px-3 py-2 border border-cyan-500/30 rounded-lg focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/30 text-sm text-white placeholder-gray-500 bg-slate-950/50 backdrop-blur transition-all"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !inputValue.trim()}
          className="p-2 bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-cyan-500/50"
        >
          <Send size={18} />
        </button>
        <button
          type="button"
          onClick={handleGetSolutions}
          className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg transition-all shadow-lg"
          title="Get solutions"
        >
          💡
        </button>
      </form>
    </div>
  );
};

export default ChatAgent;
