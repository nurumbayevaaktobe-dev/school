import React, { useState } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import ScreenGrid from './ScreenGrid';
import AIInsights from '../AI/AIInsights';
import CodeReview from '../AI/CodeReview';
import LockControl from '../Interactive/LockControl';
import PollCreator from '../Interactive/PollCreator';
import { Users, Brain, Lock, BarChart3, Code } from 'lucide-react';

const Dashboard = () => {
  const { students, screenData, isConnected } = useWebSocket();
  const [activeTab, setActiveTab] = useState('monitor');

  const tabs = [
    { id: 'monitor', label: 'Monitor', icon: Users },
    { id: 'ai', label: 'AI Insights', icon: Brain },
    { id: 'codereview', label: 'Code Review', icon: Code },
    { id: 'controls', label: 'Controls', icon: Lock },
    { id: 'polls', label: 'Polls', icon: BarChart3 }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🎓 AI ClassGuard Pro
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Next-gen classroom monitoring powered by AI
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              <div className="px-4 py-2 bg-blue-50 rounded-lg">
                <span className="text-sm font-medium text-blue-900">
                  {Object.keys(students).length} Students Online
                </span>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mt-4 border-b border-gray-200">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'monitor' && (
          <ScreenGrid students={students} screenData={screenData} isConnected={isConnected} />
        )}

        {activeTab === 'ai' && (
          <AIInsights students={students} screenData={screenData} />
        )}

        {activeTab === 'codereview' && (
          <CodeReview students={students} screenData={screenData} />
        )}

        {activeTab === 'controls' && (
          <LockControl students={students} />
        )}

        {activeTab === 'polls' && (
          <PollCreator />
        )}
      </main>
    </div>
  );
};

export default Dashboard;
