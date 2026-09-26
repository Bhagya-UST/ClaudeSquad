import React, { useState, useMemo } from 'react';
import { Search, X, Eye } from 'lucide-react';

interface Return {
  id: string;
  customerId: string;
  customerName: string;
  productName: string;
  category: string;
  amount: number;
  classification: string;
  confidence: number;
  roiPotential: number;
  churnRisk: number;
  fraudScore: number;
  status: 'pending' | 'approved' | 'rejected' | 'implemented';
  returnDate: string;
}

interface ReturnSearchFilterProps {
  returns: Return[];
  onReturnClick?: (returnId: string) => void;
  onBulkApprove?: (ids: string[]) => void;
  onBulkReject?: (ids: string[]) => void;
}

export const ReturnSearchFilter: React.FC<ReturnSearchFilterProps> = ({
  returns,
  onReturnClick,
  onBulkApprove,
  onBulkReject,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    classification: 'all',
    status: 'all',
    roiMin: 1,
    churnRisk: 'all',
  });
  const [selectedReturns, setSelectedReturns] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'date' | 'roi' | 'churn' | 'amount'>('date');

  const filteredReturns = useMemo(() => {
    let results = returns.filter(r => {
      const matchesSearch =
        r.customerId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.id.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesClassification =
        filters.classification === 'all' || r.classification === filters.classification;

      const matchesStatus = filters.status === 'all' || r.status === filters.status;

      const matchesRoi = r.roiPotential >= filters.roiMin;

      const matchesChurnRisk =
        filters.churnRisk === 'all' ||
        (filters.churnRisk === 'high' && r.churnRisk >= 0.7) ||
        (filters.churnRisk === 'medium' && r.churnRisk >= 0.4 && r.churnRisk < 0.7) ||
        (filters.churnRisk === 'low' && r.churnRisk < 0.4);

      return (
        matchesSearch &&
        matchesClassification &&
        matchesStatus &&
        matchesRoi &&
        matchesChurnRisk
      );
    });

    // Sort
    results.sort((a, b) => {
      if (sortBy === 'roi') return b.roiPotential - a.roiPotential;
      if (sortBy === 'churn') return b.churnRisk - a.churnRisk;
      if (sortBy === 'amount') return b.amount - a.amount;
      return new Date(b.returnDate).getTime() - new Date(a.returnDate).getTime();
    });

    return results;
  }, [returns, searchTerm, filters, sortBy]);

  const toggleSelectReturn = (id: string) => {
    const newSelected = new Set(selectedReturns);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedReturns(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedReturns.size === filteredReturns.length) {
      setSelectedReturns(new Set());
    } else {
      setSelectedReturns(new Set(filteredReturns.map(r => r.id)));
    }
  };

  const handleBulkApprove = () => {
    onBulkApprove?.(Array.from(selectedReturns));
    setSelectedReturns(new Set());
  };

  const handleBulkReject = () => {
    onBulkReject?.(Array.from(selectedReturns));
    setSelectedReturns(new Set());
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Search & Filter Bar */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="mb-4">
          <div className="relative flex items-center">
            <Search className="absolute left-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by customer name, ID, product, or return #..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <select
            value={filters.classification}
            onChange={(e) => setFilters({ ...filters, classification: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Classification: All</option>
            <option value="SIZING">SIZING</option>
            <option value="QUALITY">QUALITY</option>
            <option value="DEFECTIVE">DEFECTIVE</option>
            <option value="FRAUD">FRAUD</option>
            <option value="LOGISTICS">LOGISTICS</option>
            <option value="OTHER">OTHER</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Status: All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="implemented">Implemented</option>
          </select>

          <select
            value={filters.roiMin}
            onChange={(e) => setFilters({ ...filters, roiMin: parseFloat(e.target.value) })}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={1}>ROI: All</option>
            <option value={2}>ROI: 2x+</option>
            <option value={3}>ROI: 3x+</option>
            <option value={5}>ROI: 5x+</option>
          </select>

          <select
            value={filters.churnRisk}
            onChange={(e) => setFilters({ ...filters, churnRisk: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Churn Risk: All</option>
            <option value="high">Churn: High</option>
            <option value="medium">Churn: Medium</option>
            <option value="low">Churn: Low</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">Sort by Date</option>
            <option value="roi">Sort by ROI</option>
            <option value="churn">Sort by Churn Risk</option>
            <option value="amount">Sort by Amount</option>
          </select>
        </div>

        {/* Filter Active Indicator */}
        {(searchTerm || filters.classification !== 'all' || filters.status !== 'all') && (
          <div className="mt-3 text-xs text-blue-600 font-medium">
            🔍 Filters active: {filteredReturns.length} results
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedReturns.size > 0 && (
        <div className="px-6 py-3 bg-blue-50 border-b border-blue-200 flex items-center justify-between">
          <p className="text-sm font-semibold text-blue-900">
            {selectedReturns.size} return{selectedReturns.size > 1 ? 's' : ''} selected
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleBulkApprove}
              className="px-4 py-2 text-sm font-semibold bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              ✓ Approve All
            </button>
            <button
              onClick={handleBulkReject}
              className="px-4 py-2 text-sm font-semibold bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              ✗ Reject All
            </button>
            <button
              onClick={() => setSelectedReturns(new Set())}
              className="px-4 py-2 text-sm font-semibold bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Returns Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedReturns.size === filteredReturns.length && filteredReturns.length > 0}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 cursor-pointer"
                />
              </th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Return</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Customer</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Product</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Classification</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">ROI</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Churn Risk</th>
              <th className="px-4 py-3 text-left text-xs font-bold text-gray-700">Status</th>
              <th className="px-4 py-3 text-center text-xs font-bold text-gray-700">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredReturns.map(ret => (
              <tr key={ret.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedReturns.has(ret.id)}
                    onChange={() => toggleSelectReturn(ret.id)}
                    className="w-4 h-4 cursor-pointer"
                  />
                </td>
                <td className="px-4 py-3 text-sm font-mono text-blue-600 font-semibold">
                  #{ret.id.slice(-6)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  <div className="font-semibold">{ret.customerName}</div>
                  <div className="text-xs text-gray-600">{ret.customerId}</div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-700">{ret.productName}</td>
                <td className="px-4 py-3 text-sm">
                  <span className="inline-flex items-center gap-1 font-semibold">
                    <span className={`text-xs font-bold px-2 py-1 rounded ${
                      ret.classification === 'SIZING' ? 'bg-blue-100 text-blue-700' :
                      ret.classification === 'QUALITY' ? 'bg-purple-100 text-purple-700' :
                      ret.classification === 'FRAUD' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {ret.classification}
                    </span>
                    <span className="text-xs text-gray-600">
                      {(ret.confidence * 100).toFixed(0)}%
                    </span>
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className="font-bold text-green-600">{ret.roiPotential.toFixed(2)}x</span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`font-bold ${
                    ret.churnRisk >= 0.7 ? 'text-red-600' :
                    ret.churnRisk >= 0.4 ? 'text-orange-600' :
                    'text-yellow-600'
                  }`}>
                    {(ret.churnRisk * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${
                    ret.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                    ret.status === 'approved' ? 'bg-green-100 text-green-700' :
                    ret.status === 'rejected' ? 'bg-red-100 text-red-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {ret.status.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => onReturnClick?.(ret.id)}
                    className="text-blue-600 hover:text-blue-700 font-semibold text-sm"
                  >
                    <Eye size={18} className="mx-auto" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredReturns.length === 0 && (
        <div className="px-6 py-12 text-center">
          <p className="text-gray-600 font-semibold">No returns found</p>
          <p className="text-sm text-gray-500 mt-1">Try adjusting your search or filters</p>
        </div>
      )}

      {/* Footer Stats */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
        <p>
          Showing {filteredReturns.length} of {returns.length} returns •
          Potential savings: <span className="font-bold text-green-600">
            ${filteredReturns.reduce((sum, r) => sum + r.amount, 0).toLocaleString()}
          </span>
        </p>
      </div>
    </div>
  );
};

export default ReturnSearchFilter;
