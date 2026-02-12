import React from 'react';
import { Monitor, Circle } from 'lucide-react';

const StudentCard = ({ studentId, student, screenData }) => {
  const isOnline = student.status === 'online';

  return (
    <div className={`
      relative rounded-lg overflow-hidden border-4 transition-all duration-200 hover:shadow-xl
      ${isOnline ? 'border-green-500' : 'border-gray-300'}
    `}>
      {/* Screenshot */}
      <div className="aspect-video bg-gray-900 relative">
        {screenData?.image ? (
          <img
            src={`data:image/jpeg;base64,${screenData.image}`}
            alt={student.username}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Monitor className="w-12 h-12 text-gray-600" />
          </div>
        )}

        {/* Status indicator */}
        <div className={`
          absolute top-2 right-2 w-4 h-4 rounded-full
          ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}
        `} />
      </div>

      {/* Info bar */}
      <div className="bg-white p-3">
        <div className="font-semibold text-gray-900 truncate">
          {student.username}
        </div>
        <div className="text-xs text-gray-600 truncate mt-1">
          {screenData?.active_app || 'No activity'}
        </div>
        <div className={`text-xs font-medium mt-1 ${isOnline ? 'text-green-600' : 'text-gray-500'}`}>
          {isOnline ? 'Online' : 'Offline'}
        </div>
      </div>
    </div>
  );
};

export default StudentCard;
