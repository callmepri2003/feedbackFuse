import { useState, useEffect } from 'react';
import { Send, MessageCircle, Clock, AlertCircle, CheckCircle } from 'lucide-react';

export default function FeedbackApp() {
  const [feedback, setFeedback] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [apiUrl, setApiUrl] = useState('http://192.168.110.155:8000/api');

  // Load feedback on component mount
  useEffect(() => {
    fetchFeedback();
  }, []);

  const fetchFeedback = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${apiUrl}/feedback/`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setFeedback(data.results || []);
    } catch (err) {
      setError(`Failed to load feedback: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) {
      setError('Message cannot be empty');
      return;
    }
    
    if (message.length > 250) {
      setError('Message must be 250 characters or less');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${apiUrl}/feedback/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const newFeedback = await response.json();
      setFeedback(prev => [newFeedback, ...prev]);
      setMessage('');
      setSuccess('Feedback submitted successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '1rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    },
    card: {
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      padding: '1.5rem',
      marginBottom: '1.5rem'
    },
    title: {
      fontSize: '2rem',
      fontWeight: 'bold',
      color: '#1f2937',
      marginBottom: '0.5rem',
      textAlign: 'center'
    },
    subtitle: {
      color: '#6b7280',
      textAlign: 'center',
      marginBottom: '2rem'
    },
    sectionTitle: {
      fontSize: '1.25rem',
      fontWeight: '600',
      color: '#1f2937',
      marginBottom: '1rem',
      display: 'flex',
      alignItems: 'center'
    },
    input: {
      width: '100%',
      padding: '0.75rem',
      border: '1px solid #d1d5db',
      borderRadius: '4px',
      fontSize: '1rem',
      outline: 'none'
    },
    textarea: {
      width: '100%',
      padding: '0.75rem',
      border: '1px solid #d1d5db',
      borderRadius: '4px',
      fontSize: '1rem',
      outline: 'none',
      resize: 'vertical',
      fontFamily: 'inherit'
    },
    button: {
      backgroundColor: '#2563eb',
      color: 'white',
      padding: '0.75rem 1.5rem',
      border: 'none',
      borderRadius: '4px',
      fontSize: '1rem',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    buttonDisabled: {
      backgroundColor: '#9ca3af',
      cursor: 'not-allowed'
    },
    buttonSecondary: {
      backgroundColor: '#e5e7eb',
      color: '#374151',
      padding: '0.5rem 1rem',
      border: 'none',
      borderRadius: '4px',
      fontSize: '0.875rem',
      cursor: 'pointer'
    },
    errorMessage: {
      backgroundColor: '#fee2e2',
      color: '#dc2626',
      padding: '0.75rem',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center'
    },
    successMessage: {
      backgroundColor: '#dcfce7',
      color: '#16a34a',
      padding: '0.75rem',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center'
    },
    feedbackItem: {
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '1rem',
      marginBottom: '1rem',
      cursor: 'default'
    },
    feedbackMeta: {
      fontSize: '0.875rem',
      color: '#6b7280',
      display: 'flex',
      alignItems: 'center',
      marginTop: '0.5rem'
    },
    badge: {
      backgroundColor: '#f3f4f6',
      color: '#374151',
      padding: '0.25rem 0.5rem',
      borderRadius: '4px',
      fontSize: '0.75rem',
      marginLeft: '1rem'
    },
    spinner: {
      border: '2px solid transparent',
      borderTop: '2px solid currentColor',
      borderRadius: '50%',
      width: '1rem',
      height: '1rem',
      animation: 'spin 1s linear infinite',
      marginRight: '0.5rem'
    }
  };

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .spinner {
          animation: spin 1s linear infinite;
        }
      `}</style>
      
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div>
          <h1 style={styles.title}>Feedback Portal</h1>
          <p style={styles.subtitle}>Share your thoughts and read what others have to say</p>
        </div>

        {/* Feedback Form */}
        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>
            <MessageCircle style={{marginRight: '0.5rem'}} size={20} />
            Submit Feedback
          </h2>
          
          <div className="space-y-4">
            <div>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Share your feedback here..."
                rows={4}
                maxLength={250}
                style={styles.textarea}
              />
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem'}}>
                <span style={{fontSize: '0.875rem', color: '#6b7280'}}>
                  {message.length}/250 characters
                </span>
              </div>
            </div>

            {error && (
              <div style={styles.errorMessage}>
                <AlertCircle style={{marginRight: '0.5rem'}} size={16} />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div style={styles.successMessage}>
                <CheckCircle style={{marginRight: '0.5rem'}} size={16} />
                <span>{success}</span>
              </div>
            )}

            <button
              onClick={submitFeedback}
              disabled={submitting || !message.trim()}
              style={{
                ...styles.button,
                ...(submitting || !message.trim() ? styles.buttonDisabled : {})
              }}
            >
              {submitting ? (
                <>
                  <div className="spinner" style={styles.spinner}></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Send style={{marginRight: '0.5rem'}} size={16} />
                  Submit Feedback
                </>
              )}
            </button>
          </div>
        </div>

        {/* Feedback List */}
        <div style={styles.card}>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem'}}>
            <h2 style={styles.sectionTitle}>
              <MessageCircle style={{marginRight: '0.5rem'}} size={20} />
              All Feedback ({feedback.length})
            </h2>
            <button
              onClick={fetchFeedback}
              disabled={loading}
              style={styles.buttonSecondary}
            >
              {loading ? (
                <>
                  <div className="spinner" style={styles.spinner}></div>
                  Loading...
                </>
              ) : (
                'Refresh'
              )}
            </button>
          </div>

          {loading && feedback.length === 0 ? (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <div className="spinner" style={{...styles.spinner, width: '2rem', height: '2rem', margin: '0 auto 1rem'}}></div>
              <p style={{color: '#6b7280'}}>Loading feedback...</p>
            </div>
          ) : error && feedback.length === 0 ? (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <AlertCircle style={{width: '3rem', height: '3rem', color: '#ef4444', margin: '0 auto 1rem'}} />
              <p style={{color: '#6b7280', marginBottom: '1rem'}}>{error}</p>
              <button
                onClick={fetchFeedback}
                style={styles.button}
              >
                Try Again
              </button>
            </div>
          ) : feedback.length === 0 ? (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <MessageCircle style={{width: '3rem', height: '3rem', color: '#9ca3af', margin: '0 auto 1rem'}} />
              <p style={{color: '#6b7280'}}>No feedback messages yet.</p>
              <p style={{color: '#9ca3af', fontSize: '0.875rem'}}>Be the first to share your thoughts!</p>
            </div>
          ) : (
            <div>
              {feedback.map((item) => (
                <div
                  key={item.id}
                  style={styles.feedbackItem}
                >
                  <p style={{color: '#1f2937', marginBottom: '0.5rem'}}>{item.message}</p>
                  <div style={styles.feedbackMeta}>
                    <Clock style={{marginRight: '0.25rem'}} size={14} />
                    {formatDate(item.created_at)}
                    <span style={styles.badge}>
                      ID: {item.id}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}