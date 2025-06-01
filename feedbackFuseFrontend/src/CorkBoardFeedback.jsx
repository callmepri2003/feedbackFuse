import React, { useState, useEffect } from 'react';
import { Plus, Send, AlertCircle, RefreshCw } from 'lucide-react';

const CorkBoardFeedback = () => {
  const [feedback, setFeedback] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Sticky note colors for variety
  const noteColors = [
    'bg-yellow-200 border-yellow-300',
    'bg-pink-200 border-pink-300',
    'bg-blue-200 border-blue-300',
    'bg-green-200 border-green-300',
    'bg-purple-200 border-purple-300',
    'bg-orange-200 border-orange-300'
  ];

  // API functions
  const fetchFeedback = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://192.168.110.155:8000/api/feedback/');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setFeedback(data.results || []);
    } catch (err) {
      console.error('Error fetching feedback:', err);
      setError('Failed to load feedback messages. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async () => {
    if (!newMessage.trim()) return;
    
    setSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch('http://192.168.110.155:8000/api/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: newMessage.trim()
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const newFeedbackItem = await response.json();
      setFeedback(prev => [newFeedbackItem, ...prev]);
      setNewMessage('');
      setShowForm(false);
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError(err.message || 'Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRandomRotation = (id) => {
    // Consistent but varied rotation based on ID
    const rotations = [-3, -1, 0, 1, 2, 3, -2];
    return rotations[id % rotations.length];
  };

  useEffect(() => {
    fetchFeedback();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-6">
      {/* Cork Board Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-amber-800 rounded-t-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-amber-50 mb-2">Feedback Board</h1>
              <p className="text-amber-200">Share your thoughts and see what others are saying</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={fetchFeedback}
                disabled={loading}
                className="bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={() => setShowForm(!showForm)}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Feedback
              </button>
            </div>
          </div>
        </div>

        {/* Cork Board Surface */}
        <div 
          className="bg-amber-700 min-h-[600px] p-8 rounded-b-lg shadow-lg relative overflow-hidden"
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 30%, rgba(139, 69, 19, 0.3) 1px, transparent 1px),
              radial-gradient(circle at 80% 70%, rgba(139, 69, 19, 0.3) 1px, transparent 1px),
              radial-gradient(circle at 40% 80%, rgba(139, 69, 19, 0.3) 1px, transparent 1px),
              radial-gradient(circle at 90% 20%, rgba(139, 69, 19, 0.3) 1px, transparent 1px),
              radial-gradient(circle at 60% 50%, rgba(139, 69, 19, 0.3) 1px, transparent 1px)
            `,
            backgroundSize: '100px 100px, 120px 120px, 80px 80px, 150px 150px, 90px 90px'
          }}
        >
          {/* Error Display */}
          {error && (
            <div className="mb-6 bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}

          {/* New Feedback Form */}
          {showForm && (
            <div 
              className="bg-yellow-100 border-2 border-yellow-300 p-4 rounded-lg shadow-lg mb-6 transform -rotate-1"
              style={{ 
                boxShadow: '0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.7)' 
              }}
            >
              <div className="flex items-start gap-3">
                <div className="w-3 h-3 bg-red-500 rounded-full shadow-sm"></div>
                <div className="flex-1">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Share your feedback... (max 250 characters)"
                    maxLength={250}
                    rows={4}
                    className="w-full bg-transparent border-none outline-none resize-none text-gray-800 placeholder-gray-500 font-handwriting text-lg"
                    style={{ fontFamily: 'cursive' }}
                  />
                  <div className="flex justify-between items-center mt-3">
                    <span className="text-sm text-gray-600">
                      {newMessage.length}/250
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setShowForm(false)}
                        className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={submitFeedback}
                        disabled={!newMessage.trim() || submitting}
                        className="bg-green-500 hover:bg-green-600 text-white px-4 py-1 rounded flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send className="w-4 h-4" />
                        {submitting ? 'Posting...' : 'Post'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && feedback.length === 0 && (
            <div className="flex justify-center items-center h-64">
              <div className="text-amber-200 text-lg flex items-center gap-3">
                <RefreshCw className="w-6 h-6 animate-spin" />
                Loading feedback...
              </div>
            </div>
          )}

          {/* Feedback Notes Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {feedback.map((item, index) => {
              const colorClass = noteColors[index % noteColors.length];
              const rotation = getRandomRotation(item.id);
              
              return (
                <div
                  key={item.id}
                  className={`${colorClass} p-4 rounded-lg shadow-lg transform transition-transform hover:scale-105 hover:z-10 relative`}
                  style={{ 
                    transform: `rotate(${rotation}deg)`,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.7)'
                  }}
                >
                  {/* Push Pin */}
                  <div 
                    className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-red-500 rounded-full shadow-md border-2 border-red-600"
                    style={{
                      background: 'radial-gradient(circle at 30% 30%, #ef4444, #dc2626)',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.3)'
                    }}
                  ></div>
                  
                  <div className="mt-2">
                    <p 
                      className="text-gray-800 text-base leading-relaxed mb-3 break-words"
                      style={{ fontFamily: 'cursive' }}
                    >
                      {item.message}
                    </p>
                    <div className="text-xs text-gray-600 text-right">
                      {formatDate(item.created_at)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Empty State */}
          {!loading && feedback.length === 0 && (
            <div className="text-center text-amber-200 py-12">
              <p className="text-xl mb-4">No feedback messages yet</p>
              <p className="text-amber-300">Be the first to share your thoughts!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CorkBoardFeedback;