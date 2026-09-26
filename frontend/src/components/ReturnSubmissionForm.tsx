import React, { useState } from 'react';
import { AlertCircle, CheckCircle, X } from 'lucide-react';

interface ReturnSubmissionFormProps {
  onClose?: () => void;
  onSuccess?: (returnId: string) => void;
}

const RETURN_REASONS = [
  'Defective Product',
  'Wrong Size/Fit',
  'Wrong Item Received',
  'Damaged in Shipping',
  'Color Not as Expected',
  'Quality Not Acceptable',
  'Changed Mind',
  'No Longer Needed',
  'Other'
];

const PRODUCT_CONDITIONS = [
  'Unopened/Unworn',
  'Opened but Unused',
  'Lightly Used',
  'Well Used',
  'Damaged'
];

export const ReturnSubmissionForm: React.FC<ReturnSubmissionFormProps> = ({
  onClose,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    customer_id: '',
    product_id: '',
    order_date: '',
    return_reason: 'Defective Product',
    customer_comments: '',
    product_condition: 'Unopened/Unworn',
    refund_amount: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [returnId, setReturnId] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.customer_id.trim()) {
      setError('Customer ID is required');
      return false;
    }
    if (!formData.product_id.trim()) {
      setError('Product ID is required');
      return false;
    }
    if (!formData.order_date) {
      setError('Order date is required');
      return false;
    }
    if (!formData.customer_comments.trim()) {
      setError('Customer comments are required');
      return false;
    }
    if (!formData.refund_amount || parseFloat(formData.refund_amount) <= 0) {
      setError('Valid refund amount is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      const authToken = localStorage.getItem('auth_token');
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/returns`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...formData,
          refund_amount: parseFloat(formData.refund_amount)
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to submit return' }));
        throw new Error(errorData.detail || 'Failed to submit return');
      }

      const data = await response.json();
      setSuccess(true);
      setReturnId(data.return_id);

      if (onSuccess) {
        onSuccess(data.return_id);
      }

      // Reset form after 2 seconds
      setTimeout(() => {
        setFormData({
          customer_id: '',
          product_id: '',
          order_date: '',
          return_reason: 'Defective Product',
          customer_comments: '',
          product_condition: 'Unopened/Unworn',
          refund_amount: ''
        });
        setSuccess(false);
      }, 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-700">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">Submit Return</h2>
            <p className="text-slate-400 text-sm mt-1">Enter customer return information for AI analysis</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition"
            >
              <X size={24} />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          {success ? (
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-6 text-center">
              <CheckCircle className="text-green-500 mx-auto mb-3" size={40} />
              <h3 className="text-xl font-semibold text-green-400 mb-2">Return Submitted Successfully!</h3>
              <p className="text-slate-300 mb-4">
                Return ID: <span className="font-mono text-green-300">{returnId}</span>
              </p>
              <p className="text-slate-400 text-sm">
                Our AI agents are analyzing this return. Check the dashboard in a few moments to see results.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error Alert */}
              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex gap-3">
                  <AlertCircle className="text-red-400 flex-shrink-0" size={20} />
                  <p className="text-red-300">{error}</p>
                </div>
              )}

              {/* Customer Information */}
              <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">Customer Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Customer ID <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      name="customer_id"
                      value={formData.customer_id}
                      onChange={handleInputChange}
                      placeholder="e.g., CUST001"
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Product ID <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      name="product_id"
                      value={formData.product_id}
                      onChange={handleInputChange}
                      placeholder="e.g., PROD123"
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Order Date <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="date"
                      name="order_date"
                      value={formData.order_date}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Refund Amount <span className="text-red-400">*</span>
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-2 text-slate-400">$</span>
                      <input
                        type="number"
                        name="refund_amount"
                        value={formData.refund_amount}
                        onChange={handleInputChange}
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                        className="w-full pl-8 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Return Details */}
              <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">Return Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Return Reason <span className="text-red-400">*</span>
                    </label>
                    <select
                      name="return_reason"
                      value={formData.return_reason}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      {RETURN_REASONS.map(reason => (
                        <option key={reason} value={reason}>{reason}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Product Condition <span className="text-red-400">*</span>
                    </label>
                    <select
                      name="product_condition"
                      value={formData.product_condition}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      {PRODUCT_CONDITIONS.map(condition => (
                        <option key={condition} value={condition}>{condition}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Customer Comments */}
              <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700/50">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Customer Comments <span className="text-red-400">*</span>
                </label>
                <textarea
                  name="customer_comments"
                  value={formData.customer_comments}
                  onChange={handleInputChange}
                  placeholder="What is the customer's reason for return? Any issues they mentioned?"
                  rows={4}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition resize-none"
                />
                <p className="text-xs text-slate-400 mt-2">
                  💡 Tip: Include specific details about the issue - this helps our AI classify the return accurately
                </p>
              </div>

              {/* Submit Button */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-cyan-300 border-t-transparent rounded-full animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    'Submit Return for Analysis'
                  )}
                </button>
                {onClose && (
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-6 bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 rounded-lg transition"
                  >
                    Cancel
                  </button>
                )}
              </div>

              {/* Info Box */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <p className="text-blue-300 text-sm">
                  <strong>What happens next?</strong> Our AI agents will analyze this return within 2-5 seconds and provide:
                  <br />• Classification (defective, wrong size, etc.)
                  <br />• Sentiment analysis & churn risk
                  <br />• Root cause identification
                </p>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
