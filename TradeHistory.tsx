import React, { useState, useEffect } from 'react';
import { Download, Filter, Search, TrendingUp, TrendingDown, Clock, DollarSign, ChevronLeft, ChevronRight, X, Calendar, RefreshCw } from 'lucide-react';

const TradeHistory = ({ botId }) => {
  const [trades, setTrades] = useState([]);
  const [filteredTrades, setFilteredTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    search: '',
    type: 'all', // all, buy, sell
    status: 'all', // all, profit, loss
    dateFrom: '',
    dateTo: '',
    minAmount: '',
    maxAmount: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const ITEMS_PER_PAGE = 20;

  useEffect(() => {
    loadTrades();
  }, [botId, currentPage, sortBy, sortOrder]);

  useEffect(() => {
    applyFilters();
  }, [trades, filters]);

  const loadTrades = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage,
        limit: ITEMS_PER_PAGE,
        sortBy,
        sortOrder
      });

      if (botId) {
        params.append('botId', botId);
      }

      const response = await fetch(`/api/trades?${params}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const data = await response.json();
        setTrades(data.trades || []);
        setTotalPages(Math.ceil((data.total || 0) / ITEMS_PER_PAGE));
      }
    } catch (error) {
      console.error('Failed to load trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...trades];

    // Search filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(trade => 
        trade.symbol.toLowerCase().includes(search) ||
        trade.botName.toLowerCase().includes(search) ||
        trade.id.toLowerCase().includes(search)
      );
    }

    // Type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(trade => trade.type.toLowerCase() === filters.type);
    }

    // Status filter
    if (filters.status === 'profit') {
      filtered = filtered.filter(trade => trade.pnl > 0);
    } else if (filters.status === 'loss') {
      filtered = filtered.filter(trade => trade.pnl < 0);
    }

    // Date filters
    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom).getTime();
      filtered = filtered.filter(trade => new Date(trade.timestamp).getTime() >= fromDate);
    }
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo).getTime();
      filtered = filtered.filter(trade => new Date(trade.timestamp).getTime() <= toDate);
    }

    // Amount filters
    if (filters.minAmount) {
      filtered = filtered.filter(trade => trade.amount >= parseFloat(filters.minAmount));
    }
    if (filters.maxAmount) {
      filtered = filtered.filter(trade => trade.amount <= parseFloat(filters.maxAmount));
    }

    setFilteredTrades(filtered);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      type: 'all',
      status: 'all',
      dateFrom: '',
      dateTo: '',
      minAmount: '',
      maxAmount: ''
    });
  };

  const exportToCSV = () => {
    const headers = ['Date', 'Bot', 'Symbol', 'Type', 'Amount', 'Price', 'Total', 'Fee', 'P&L', 'Status'];
    const rows = filteredTrades.map(trade => [
      new Date(trade.timestamp).toLocaleString(),
      trade.botName,
      trade.symbol,
      trade.type,
      trade.amount,
      trade.price,
      (trade.amount * trade.price).toFixed(2),
      trade.fee,
      trade.pnl?.toFixed(2) || '0.00',
      trade.pnl > 0 ? 'Profit' : trade.pnl < 0 ? 'Loss' : 'Break-even'
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trades_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const getTotalStats = () => {
    const totalPnL = filteredTrades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
    const totalVolume = filteredTrades.reduce((sum, trade) => sum + (trade.amount * trade.price), 0);
    const wins = filteredTrades.filter(t => t.pnl > 0).length;
    const losses = filteredTrades.filter(t => t.pnl < 0).length;
    const winRate = filteredTrades.length > 0 ? (wins / filteredTrades.length) * 100 : 0;

    return { totalPnL, totalVolume, wins, losses, winRate };
  };

  const stats = getTotalStats();
  const activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
    if (key === 'search') return value !== '';
    if (key === 'type' || key === 'status') return value !== 'all';
    return value !== '';
  }).length;

  if (loading && trades.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trade History</h1>
          <p className="text-gray-600 mt-1">
            {filteredTrades.length} {filteredTrades.length === 1 ? 'trade' : 'trades'}
            {activeFiltersCount > 0 && ` (${activeFiltersCount} filter${activeFiltersCount > 1 ? 's' : ''} active)`}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 border-2 rounded-lg transition flex items-center gap-2 ${
              showFilters || activeFiltersCount > 0
                ? 'border-blue-500 bg-blue-50 text-blue-600'
                : 'border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
            {activeFiltersCount > 0 && (
              <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
                {activeFiltersCount}
              </span>
            )}
          </button>
          <button
            onClick={loadTrades}
            disabled={loading}
            className="px-4 py-2 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={exportToCSV}
            disabled={filteredTrades.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Total P&L</div>
          <div className={`text-2xl font-bold ${stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(stats.totalPnL)}
          </div>
        </div>
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Total Volume</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(stats.totalVolume)}
          </div>
        </div>
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Win Rate</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.winRate.toFixed(1)}%
          </div>
        </div>
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Wins</div>
          <div className="text-2xl font-bold text-green-600">{stats.wins}</div>
        </div>
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Losses</div>
          <div className="text-2xl font-bold text-red-600">{stats.losses}</div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-lg">Filters</h3>
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:underline flex items-center gap-1"
            >
              <X className="w-4 h-4" />
              Clear All
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  placeholder="Symbol, bot, trade ID..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Type
              </label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Types</option>
                <option value="buy">Buy Only</option>
                <option value="sell">Sell Only</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All</option>
                <option value="profit">Profit Only</option>
                <option value="loss">Loss Only</option>
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                From Date
              </label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                To Date
              </label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Min Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Min Amount ($)
              </label>
              <input
                type="number"
                value={filters.minAmount}
                onChange={(e) => setFilters({ ...filters, minAmount: e.target.value })}
                placeholder="0.00"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Trades Table */}
      <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th 
                  onClick={() => handleSort('date')}
                  className="text-left py-3 px-4 font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Date/Time
                    {sortBy === 'date' && (
                      <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Bot</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Symbol</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">Type</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Amount</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Price</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Total</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Fee</th>
                <th 
                  onClick={() => handleSort('pnl')}
                  className="text-right py-3 px-4 font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center justify-end gap-2">
                    P&L
                    {sortBy === 'pnl' && (
                      <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredTrades.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-12 text-gray-500">
                    <div className="flex flex-col items-center gap-3">
                      <DollarSign className="w-12 h-12 text-gray-400" />
                      <p>No trades found</p>
                      {activeFiltersCount > 0 && (
                        <button
                          onClick={clearFilters}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          Clear filters
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                filteredTrades.map((trade) => (
                  <tr key={trade.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">
                          {new Date(trade.timestamp).toLocaleDateString()}
                        </div>
                        <div className="text-gray-500">
                          {new Date(trade.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm font-medium text-gray-900">
                        {trade.botName}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono font-bold text-gray-900">
                        {trade.symbol}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        trade.type.toLowerCase() === 'buy'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {trade.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono">
                      {trade.amount.toFixed(6)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono">
                      {formatCurrency(trade.price)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-medium">
                      {formatCurrency(trade.amount * trade.price)}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600 font-mono text-sm">
                      {formatCurrency(trade.fee)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {trade.pnl !== undefined && trade.pnl !== null ? (
                        <div className="flex items-center justify-end gap-1">
                          <span className={`font-bold ${
                            trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {trade.pnl >= 0 ? '+' : ''}{formatCurrency(trade.pnl)}
                          </span>
                          {trade.pnl >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-600" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="border-t-2 border-gray-200 px-4 py-3 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="
