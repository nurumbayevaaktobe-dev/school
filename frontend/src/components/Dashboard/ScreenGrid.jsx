import React, { useState, useMemo } from 'react';
import StudentCard from './StudentCard';
import { Loader2, Users, AlertCircle } from 'lucide-react';

const ScreenGrid = ({ students, screenData, isConnected }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredStudents = useMemo(() => {
    let filtered = Object.entries(students);

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(([id, student]) =>
        student.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  }, [students, searchTerm]);

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center h-96 bg-white rounded-lg shadow">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600">Connecting to monitoring server...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4">
        <input
          type="text"
          placeholder="Search students..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Grid */}
      {filteredStudents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">
            {Object.keys(students).length === 0
              ? 'No students connected yet'
              : 'No students match your search'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredStudents.map(([id, student]) => (
            <StudentCard
              key={id}
              studentId={id}
              student={student}
              screenData={screenData[id]}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ScreenGrid;
