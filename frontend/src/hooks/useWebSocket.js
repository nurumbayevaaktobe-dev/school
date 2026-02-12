import { useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';

const SERVER_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const useWebSocket = () => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [students, setStudents] = useState({});
  const [screenData, setScreenData] = useState({});

  useEffect(() => {
    // Create socket connection
    const newSocket = io(SERVER_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10
    });

    // Connection events
    newSocket.on('connect', () => {
      console.log('✅ Connected to server');
      setIsConnected(true);

      // Register as teacher
      newSocket.emit('register_teacher', {
        name: 'Teacher'
      });
    });

    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from server');
      setIsConnected(false);
    });

    // Student events
    newSocket.on('student_list', (data) => {
      console.log('📋 Received student list:', data.students);
      const studentsMap = {};
      data.students.forEach(student => {
        studentsMap[student.id] = student;
      });
      setStudents(studentsMap);
    });

    newSocket.on('student_connected', (data) => {
      console.log('👤 Student connected:', data.username);
      setStudents(prev => ({
        ...prev,
        [data.user_id]: {
          id: data.user_id,
          username: data.username,
          status: 'online'
        }
      }));
    });

    newSocket.on('screen_data', (data) => {
      setScreenData(prev => ({
        ...prev,
        [data.user_id]: {
          image: data.image,
          active_window: data.active_window,
          active_app: data.active_app,
          timestamp: data.timestamp
        }
      }));
    });

    setSocket(newSocket);

    // Cleanup
    return () => {
      newSocket.close();
    };
  }, []);

  const sendMessage = useCallback((target, message, type = 'normal') => {
    if (socket) {
      socket.emit('send_message', {
        target,
        message,
        type
      });
    }
  }, [socket]);

  const lockScreens = useCallback((students, duration, message) => {
    if (socket) {
      socket.emit('lock_screens', {
        students,
        duration,
        message
      });
    }
  }, [socket]);

  const unlockScreens = useCallback((students) => {
    if (socket) {
      socket.emit('unlock_screens', {
        students
      });
    }
  }, [socket]);

  return {
    socket,
    isConnected,
    students,
    screenData,
    sendMessage,
    lockScreens,
    unlockScreens
  };
};
