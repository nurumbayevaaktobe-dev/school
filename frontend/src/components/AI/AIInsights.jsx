import React, { useState, useEffect } from 'react';
import { useAI } from '../../hooks/useAI';
import { Brain, TrendingUp, AlertCircle, CheckCircle, Sparkles, RefreshCw } from 'lucide-react';

const AIInsights = ({ students, screenData }) => {
  const { analyzeClassroom, isLoading, error } = useAI();
  const [insights, setInsights] = useState(null);

  const fetchInsights = async () => {
    const studentsData = {};
    Object.entries(students).forEach(([id, student]) => {
      const data = screenData[id];
      studentsData[id] = {
        name: student.username,
        active_time: 0,
        idle_time: 0,
        switches: 0,
        current_app: data?.active_app || 'Unknown',
        violations: 0,
        progress: 0
      };
    });

    const result = await analyzeClassroom(studentsData);
    if (result) {
      setInsights(result);
    }
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Brain className="w-7 h-7 text-purple-600" />
          AI Classroom Insights
          <Sparkles className="w-5 h-5 text-yellow-500" />
        </h2>

        <button
          onClick={fetchInsights}
          disabled={isLoading}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {isLoading && !insights && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">AI is analyzing your classroom...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 text-red-700">
          <AlertCircle className="w-5 h-5 inline mr-2" />
          {error}
        </div>
      )}

      {insights && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Overall Status</h3>
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600">Engagement</span>
              <span className="font-bold text-gray-900">{insights.engagement_percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  insights.engagement_percentage >= 75 ? 'bg-green-500' :
                  insights.engagement_percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${insights.engagement_percentage}%` }}
              />
            </div>
          </div>

          {insights.recommendation && (
            <div className="bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg p-6 shadow text-white">
              <TrendingUp className="w-8 h-8 mb-2" />
              <h3 className="font-semibold text-lg mb-1">AI Recommendation</h3>
              <p className="text-sm opacity-90">{insights.recommendation}</p>
            </div>
          )}

          {insights.positive_moments && insights.positive_moments.length > 0 && (
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-bold text-gray-900 text-lg mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Positive Moments
              </h3>
              <div className="space-y-2">
                {insights.positive_moments.map((moment, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-green-500 mt-0.5">✓</span>
                    <span>{moment}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!insights && !isLoading && (
        <div className="text-center py-12 text-gray-500">
          <Brain className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium mb-2">Ready to Analyze</p>
          <p className="text-sm">Click "Analyze" to get AI-powered insights about your classroom</p>
        </div>
      )}
    </div>
  );
};

export default AIInsights;
