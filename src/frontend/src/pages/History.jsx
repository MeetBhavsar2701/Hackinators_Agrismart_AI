import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/history')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch history');
        return res.json();
      })
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex flex-col w-full max-w-7xl mx-auto px-gutter md:px-margin-tablet lg:px-margin-desktop py-space-lg">
      <h1 className="font-headline-lg text-primary mb-space-lg flex items-center gap-2">
        <span className="material-symbols-outlined">history</span>
        Scan History
      </h1>

      {loading ? (
        <div className="text-center py-20 text-on-surface-variant">Loading history...</div>
      ) : error ? (
        <div className="text-center py-20 text-error">{error}</div>
      ) : history.length === 0 ? (
        <div className="text-center py-20 text-on-surface-variant">
          <span className="material-symbols-outlined text-[48px] mb-4">eco</span>
          <p>No scans yet.</p>
          <button onClick={() => navigate('/')} className="mt-4 px-6 py-2 bg-primary text-on-primary rounded-lg">
            Start New Scan
          </button>
        </div>
      ) : (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-low border-b border-outline-variant font-label-md text-on-surface">
                <th className="p-4">Date & Time</th>
                <th className="p-4">Image</th>
                <th className="p-4">Diagnosis</th>
                <th className="p-4">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, idx) => (
                <tr key={idx} className="border-b border-outline-variant last:border-b-0 hover:bg-surface-container-low/50">
                  <td className="p-4 text-on-surface-variant font-body-md">
                    {new Date(item.timestamp).toLocaleString()}
                  </td>
                  <td className="p-4 text-on-surface-variant font-body-md truncate max-w-[150px]">
                    {item.image_filename}
                  </td>
                  <td className="p-4">
                    <span className="px-3 py-1 bg-surface-container text-on-surface-variant rounded-full font-label-sm">
                      {item.class_label.replace(/___/g, ' - ').replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="p-4 text-on-surface-variant font-body-md">
                    {Math.round(item.confidence * 100)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
