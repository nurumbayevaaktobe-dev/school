import React, { useState } from 'react';
import { useAI } from '../../hooks/useAI';
import { Code, Check, AlertTriangle, X, Loader2, Zap, FileCode } from 'lucide-react';

const CodeReview = ({ students, screenData }) => {
  const { checkAllCode, isLoading } = useAI();
  const [results, setResults] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const handleCheckCode = async () => {
    // Prepare student screens for AI analysis
    const studentsToCheck = Object.entries(students)
      .filter(([id, student]) => screenData[id]?.image)
      .map(([id, student]) => ({
        id,
        name: student.username,
        screenshot: screenData[id].image
      }));

    if (studentsToCheck.length === 0) {
      alert('No student screens available for analysis');
      return;
    }

    // Set progress
    setProgress({ current: 0, total: studentsToCheck.length });

    // Simulate progress updates (since batch processing happens server-side)
    const progressInterval = setInterval(() => {
      setProgress(prev => ({
        ...prev,
        current: Math.min(prev.current + 1, prev.total)
      }));
    }, 2000);

    try {
      const analysisResults = await checkAllCode(studentsToCheck, selectedLanguage);
      setResults(analysisResults);
    } finally {
      clearInterval(progressInterval);
      setProgress({ current: 0, total: 0 });
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      correct: <Check className="w-5 h-5" />,
      has_issues: <AlertTriangle className="w-5 h-5" />,
      errors: <X className="w-5 h-5" />,
      no_code: <Code className="w-5 h-5" />,
      off_task: <AlertTriangle className="w-5 h-5" />
    };
    return icons[category] || icons.no_code;
  };

  const getCategoryColor = (category) => {
    const colors = {
      correct: 'bg-green-50 border-green-300 text-green-800',
      has_issues: 'bg-yellow-50 border-yellow-300 text-yellow-800',
      errors: 'bg-red-50 border-red-300 text-red-800',
      no_code: 'bg-gray-50 border-gray-300 text-gray-800',
      off_task: 'bg-orange-50 border-orange-300 text-orange-800'
    };
    return colors[category] || colors.no_code;
  };

  const getCategoryTitle = (category) => {
    const titles = {
      correct: '✅ Code Looks Good',
      has_issues: '⚠️ Has Minor Issues',
      errors: '❌ Has Errors',
      no_code: '📝 No Code Detected',
      off_task: '🎮 Off Task'
    };
    return titles[category] || 'Unknown';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      high: 'bg-red-100 text-red-700',
      medium: 'bg-yellow-100 text-yellow-700',
      low: 'bg-blue-100 text-blue-700'
    };
    return colors[severity] || colors.medium;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Code className="w-7 h-7 text-blue-600" />
          AI Code Review
          <Zap className="w-5 h-5 text-yellow-500" />
        </h2>

        <div className="flex items-center gap-3">
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="csharp">C#</option>
            <option value="html">HTML/CSS</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
          </select>

          <button
            onClick={handleCheckCode}
            disabled={isLoading || Object.keys(students).length === 0}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold shadow-md transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Check All Code (AI)
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading State with Progress */}
      {isLoading && (
        <div className="text-center py-12 bg-blue-50 rounded-lg border-2 border-blue-200">
          <div className="inline-flex items-center gap-3 mb-4">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <div className="text-left">
              <p className="font-semibold text-blue-900 text-lg">AI is reviewing code...</p>
              {progress.total > 0 && (
                <p className="text-sm text-blue-600 mt-1">
                  Analyzing {progress.current} of {progress.total} students
                </p>
              )}
            </div>
          </div>

          {progress.total > 0 && (
            <div className="max-w-md mx-auto">
              <div className="w-full bg-blue-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.current / progress.total) * 100}%` }}
                />
              </div>
              <p className="text-xs text-blue-600 mt-2">This may take 10-30 seconds</p>
            </div>
          )}
        </div>
      )}

      {/* Results */}
      {results && !isLoading && (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-5 gap-3">
            {Object.entries(results).map(([category, items]) => {
              const count = Array.isArray(items) ? items.length : 0;
              return (
                <div
                  key={category}
                  className={`p-4 rounded-lg border-2 ${getCategoryColor(category)} transition-all hover:scale-105 cursor-default`}
                >
                  <div className="flex items-center justify-between mb-2">
                    {getCategoryIcon(category)}
                    <span className="text-2xl font-bold">{count}</span>
                  </div>
                  <div className="text-sm font-medium">{getCategoryTitle(category)}</div>
                </div>
              );
            })}
          </div>

          {/* Detailed Results */}
          <div className="space-y-4 mt-6">
            {/* Correct */}
            {results.correct && results.correct.length > 0 && (
              <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                  <Check className="w-5 h-5" />
                  Code Looks Good ({results.correct.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.correct.map((name, idx) => (
                    <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Has Issues */}
            {results.has_issues && results.has_issues.length > 0 && (
              <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                <h3 className="font-bold text-yellow-900 mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Minor Issues Detected ({results.has_issues.length})
                </h3>
                <div className="space-y-3">
                  {results.has_issues.map((student, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-3 border border-yellow-200 hover:border-yellow-400 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <FileCode className="w-4 h-4 text-yellow-600" />
                        <span className="font-semibold text-gray-900">{student.name}</span>
                      </div>
                      {student.issues && student.issues.length > 0 && (
                        <ul className="space-y-2 ml-6">
                          {student.issues.map((issue, i) => (
                            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className={`
                                px-2 py-0.5 rounded text-xs font-bold mt-0.5 flex-shrink-0
                                ${getSeverityColor(issue.severity)}
                              `}>
                                {issue.type}
                              </span>
                              <span className="flex-1">
                                {issue.description}
                                {issue.line && <span className="text-gray-500"> (line {issue.line})</span>}
                              </span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Errors */}
            {results.errors && results.errors.length > 0 && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                <h3 className="font-bold text-red-900 mb-3 flex items-center gap-2">
                  <X className="w-5 h-5" />
                  Errors Found ({results.errors.length})
                </h3>
                <div className="space-y-3">
                  {results.errors.map((student, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-3 border border-red-200 hover:border-red-400 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <FileCode className="w-4 h-4 text-red-600" />
                        <span className="font-semibold text-gray-900">{student.name}</span>
                      </div>
                      {student.issues && student.issues.length > 0 && (
                        <ul className="space-y-2 ml-6">
                          {student.issues.map((issue, i) => (
                            <li key={i} className="text-sm text-red-700 flex items-start gap-2">
                              <X className="w-4 h-4 mt-0.5 flex-shrink-0" />
                              <span className="flex-1">
                                {issue.description}
                                {issue.line && <span className="font-mono"> (line {issue.line})</span>}
                              </span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Code */}
            {results.no_code && results.no_code.length > 0 && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  No Code on Screen ({results.no_code.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.no_code.map((name, idx) => (
                    <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Off Task */}
            {results.off_task && results.off_task.length > 0 && (
              <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-4">
                <h3 className="font-bold text-orange-900 mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Off Task ({results.off_task.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.off_task.map((name, idx) => (
                    <span key={idx} className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!results && !isLoading && (
        <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border-2 border-gray-200">
          <Code className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium mb-2">Ready to Review Code</p>
          <p className="text-sm mb-4">Click "Check All Code" to analyze student screens with AI</p>
          <div className="text-xs text-gray-400">
            <p>✓ Uses Gemini Vision API for code analysis</p>
            <p>✓ Detects syntax, logic, and style issues</p>
            <p>✓ Analyzes {Object.keys(students).length} students in 10-30 seconds</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeReview;
