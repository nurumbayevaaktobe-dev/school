import React, { useState } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { BarChart3, Plus, X, Send } from 'lucide-react';

const PollCreator = () => {
  const { socket } = useWebSocket();
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState(['', '', '', '']);
  const [pollActive, setPollActive] = useState(false);

  const createPoll = () => {
    const validOptions = options.filter(opt => opt.trim() !== '');

    if (!question.trim() || validOptions.length < 2) {
      alert('Please enter a question and at least 2 options');
      return;
    }

    socket.emit('create_poll', {
      question: question,
      options: validOptions
    });

    setPollActive(true);
  };

  const addOption = () => {
    if (options.length < 6) {
      setOptions([...options, '']);
    }
  };

  const removeOption = (index) => {
    if (options.length > 2) {
      const newOptions = options.filter((_, i) => i !== index);
      setOptions(newOptions);
    }
  };

  const updateOption = (index, value) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const resetForm = () => {
    setQuestion('');
    setOptions(['', '', '', '']);
    setPollActive(false);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <BarChart3 className="w-7 h-7 text-purple-600" />
        Quick Class Poll
      </h2>

      {!pollActive ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Poll Question:
            </label>
            <input
              type="text"
              placeholder="Enter your question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Answer Options:
            </label>
            <div className="space-y-2">
              {options.map((option, idx) => (
                <div key={idx} className="flex gap-2">
                  <input
                    type="text"
                    placeholder={`Option ${idx + 1}`}
                    value={option}
                    onChange={(e) => updateOption(idx, e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  {options.length > 2 && (
                    <button
                      onClick={() => removeOption(idx)}
                      className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {options.length < 6 && (
              <button
                onClick={addOption}
                className="mt-2 w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-purple-500 hover:text-purple-600 flex items-center justify-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Add Option
              </button>
            )}
          </div>

          <button
            onClick={createPoll}
            className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 flex items-center justify-center gap-2 font-semibold shadow-md text-lg"
          >
            <Send className="w-6 h-6" />
            Send Poll to All Students
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
            <h3 className="font-bold text-purple-900 text-lg mb-2">{question}</h3>
            <p className="text-purple-700">Poll sent to students</p>
          </div>

          <button
            onClick={resetForm}
            className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold"
          >
            Create New Poll
          </button>
        </div>
      )}
    </div>
  );
};

export default PollCreator;
