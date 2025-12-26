import React, { useState, useEffect } from 'react';
import { Copy, Check, Users, DollarSign, Gift, TrendingUp, ExternalLink, Share2, Mail, Twitter, MessageCircle, Crown } from 'lucide-react';

const ReferralDashboard = () => {
  const [referralCode, setReferralCode] = useState('');
  const [stats, setStats] = useState({
    totalReferrals: 0,
    activeReferrals: 0,
    totalEarnings: 0,
    pendingEarnings: 0,
    thisMonth: 0,
    isUnlocked: false
  });
  const [recentReferrals, setRecentReferrals] = useState([]);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  const REFERRAL_REWARD = 1; // $1 per referral
  const FREE_THRESHOLD = 10; // Free after 10 referrals
  const SUBSCRIPTION_PRICE = 10; // $10/mo

  useEffect(() => {
    loadReferralData();
  }, []);

  const loadReferralData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/referrals', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const data = await response.json();
        setReferralCode(data.referralCode);
        setStats(data.stats);
        setRecentReferrals(data.recentReferrals || []);
      }
    } catch (error) {
      console.error('Failed to load referral data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getReferralLink = () => {
    return `https://cryptotradebot.pro/signup?ref=${referralCode}`;
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const shareVia = (platform) => {
    const link = getReferralLink();
    const message = `Join CryptoTradeBot Pro and automate your crypto trading! Use my referral link to get started:`;
    
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(message)}&url=${encodeURIComponent(link)}`,
      telegram: `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent(message)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(message + ' ' + link)}`,
      email: `mailto:?subject=Join CryptoTradeBot Pro&body=${encodeURIComponent(message + '\n\n' + link)}`
    };

    window.open(urls[platform], '_blank');
  };

  const progressToFree = (stats.totalReferrals / FREE_THRESHOLD) * 100;
  const remainingForFree = Math.max(0, FREE_THRESHOLD - stats.totalReferrals);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center pb-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Referral Program</h1>
        <p className="text-gray-600">
          Earn ${REFERRAL_REWARD} per referral. Get {FREE_THRESHOLD} referrals for FREE lifetime access! 🎉
        </p>
      </div>

      {/* Unlock Progress Banner */}
      {!stats.isUnlocked && (
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Crown className="w-8 h-8" />
              <div>
                <h3 className="text-xl font-bold">Path to FREE Lifetime Access</h3>
                <p className="text-blue-100 text-sm mt-1">
                  {remainingForFree} more {remainingForFree === 1 ? 'referral' : 'referrals'} needed
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{stats.totalReferrals}/{FREE_THRESHOLD}</div>
              <div className="text-sm text-blue-100">Referrals</div>
            </div>
          </div>
          
          <div className="w-full bg-white/20 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-white h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2"
              style={{ width: `${Math.min(progressToFree, 100)}%` }}
            >
              {progressToFree > 20 && (
                <span className="text-xs font-bold text-purple-600">
                  {Math.round(progressToFree)}%
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Unlocked Banner */}
      {stats.isUnlocked && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg p-6 text-white">
          <div className="flex items-center gap-4">
            <Crown className="w-12 h-12" />
            <div>
              <h3 className="text-2xl font-bold">🎉 Congratulations!</h3>
              <p className="text-green-100 mt-1">
                You've unlocked FREE lifetime access! No more monthly payments. Keep referring to earn cash!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Referrals */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <Users className="w-8 h-8 text-blue-600" />
            <span className="text-sm font-medium text-gray-600">Total</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{stats.totalReferrals}</div>
          <div className="text-sm text-gray-500 mt-1">All-time referrals</div>
        </div>

        {/* Active Referrals */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <span className="text-sm font-medium text-gray-600">Active</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{stats.activeReferrals}</div>
          <div className="text-sm text-gray-500 mt-1">Paying users</div>
        </div>

        {/* Total Earnings */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <DollarSign className="w-8 h-8 text-purple-600" />
            <span className="text-sm font-medium text-gray-600">Earned</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">
            ${stats.totalEarnings.toFixed(2)}
          </div>
          <div className="text-sm text-gray-500 mt-1">Lifetime earnings</div>
        </div>

        {/* This Month */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <Gift className="w-8 h-8 text-orange-600" />
            <span className="text-sm font-medium text-gray-600">This Month</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">
            ${stats.thisMonth.toFixed(2)}
          </div>
          <div className="text-sm text-gray-500 mt-1">Current month</div>
        </div>
      </div>

      {/* Referral Link Section */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <Share2 className="w-5 h-5 text-gray-600" />
          Your Referral Link
        </h3>

        {/* Referral Code Display */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Referral Code
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={referralCode}
              readOnly
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg bg-gray-50 font-mono text-lg font-bold"
            />
            <button
              onClick={() => copyToClipboard(referralCode)}
              className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
            >
              {copied ? (
                <>
                  <Check className="w-5 h-5" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-5 h-5" />
                  Copy
                </>
              )}
            </button>
          </div>
        </div>

        {/* Full Link */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Referral Link
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={getReferralLink()}
              readOnly
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg bg-gray-50 text-sm"
            />
            <button
              onClick={() => copyToClipboard(getReferralLink())}
              className="px-4 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
            >
              <Copy className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Share Buttons */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Share via
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button
              onClick={() => shareVia('twitter')}
              className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-blue-400 text-blue-600 rounded-lg hover:bg-blue-50 transition"
            >
              <Twitter className="w-5 h-5" />
              Twitter
            </button>
            <button
              onClick={() => shareVia('telegram')}
              className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 transition"
            >
              <MessageCircle className="w-5 h-5" />
              Telegram
            </button>
            <button
              onClick={() => shareVia('whatsapp')}
              className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 transition"
            >
              <MessageCircle className="w-5 h-5" />
              WhatsApp
            </button>
            <button
              onClick={() => shareVia('email')}
              className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-gray-400 text-gray-600 rounded-lg hover:bg-gray-50 transition"
            >
              <Mail className="w-5 h-5" />
              Email
            </button>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4 text-gray-900">How Referral Program Works</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="text-3xl mb-2">1️⃣</div>
            <h4 className="font-bold text-gray-900 mb-2">Share Your Link</h4>
            <p className="text-sm text-gray-600">
              Share your unique referral link with friends, on social media, or your community.
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-3xl mb-2">2️⃣</div>
            <h4 className="font-bold text-gray-900 mb-2">They Sign Up</h4>
            <p className="text-sm text-gray-600">
              When someone signs up using your link, they become your referral.
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-3xl mb-2">3️⃣</div>
            <h4 className="font-bold text-gray-900 mb-2">Earn Rewards</h4>
            <p className="text-sm text-gray-600">
              Earn ${REFERRAL_REWARD} per referral. Get {FREE_THRESHOLD} referrals for FREE lifetime access!
            </p>
          </div>
        </div>
      </div>

      {/* Recent Referrals */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4">Recent Referrals</h3>
        
        {recentReferrals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>No referrals yet. Start sharing your link!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-600">User</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Joined</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-600">Earned</th>
                </tr>
              </thead>
              <tbody>
                {recentReferrals.map((ref, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">
                          {ref.username.substring(0, 1).toUpperCase()}
                        </div>
                        <span className="font-medium">{ref.username}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        ref.status === 'active' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {ref.status === 'active' ? '✅ Active' : '⏳ Pending'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(ref.joinedAt).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-green-600">
                      ${ref.earned.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Withdrawal Info (if applicable) */}
      {stats.totalEarnings >= 50 && (
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 flex items-start gap-3">
          <DollarSign className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-green-900">
            <p className="font-medium">Withdrawal Available</p>
            <p className="mt-1">
              You have ${stats.totalEarnings.toFixed(2)} in earnings. Minimum withdrawal is $50.
            </p>
            <button className="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium">
              Request Withdrawal
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReferralDashboard;
