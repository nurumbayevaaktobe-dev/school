import React, { useState } from 'react';
import { Lock, Unlock, Clock, MessageSquare } from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';

const LockControl = ({ students }) => {
  const { lockScreens, unlockScreens } = useWebSocket();
  const [message, setMessage] = useState('Please pay attention to the teacher');
  const [duration, setDuration] = useState(180);
  const [isLocked, setIsLocked] = useState(false);

  const handleLock = () => {
    lockScreens('all', duration, message);
    setIsLocked(true);

    if (duration !== 'manual') {
      setTimeout(() => setIsLocked(false), duration * 1000);
    }
  };

  const handleUnlock = () => {
    unlockScreens('all');
    setIsLocked(false);
  };

  const formatDuration = (seconds) => {
    if (seconds === 'manual') return 'Until manually unlocked';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Lock className="w-7 h-7 text-red-600" />
        Screen Lock Control
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MessageSquare className="w-4 h-4 inline mr-1" />
            Lock Screen Message:
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="3"
            placeholder="Enter message to display on locked screens..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="w-4 h-4 inline mr-1" />
            Lock Duration: <span className="font-bold text-blue-600">{formatDuration(duration)}</span>
          </label>

          <div className="grid grid-cols-4 gap-2">
            {[60, 180, 300, 600].map((seconds) => (
              <button
                key={seconds}
                onClick={() => setDuration(seconds)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  duration === seconds
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {seconds / 60} min
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-4 border-t">
          <button
            onClick={handleLock}
            disabled={isLocked}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-semibold shadow-md"
          >
            <Lock className="w-5 h-5" />
            Lock Screens
          </button>

          <button
            onClick={handleUnlock}
            disabled={!isLocked}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-semibold shadow-md"
          >
            <Unlock className="w-5 h-5" />
            Unlock Now
          </button>
        </div>

        {isLocked && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 text-center">
            <Lock className="w-6 h-6 text-red-600 mx-auto mb-2" />
            <p className="font-semibold text-red-900">Screens Currently Locked</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LockControl;
