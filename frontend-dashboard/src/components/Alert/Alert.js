import React, { useState, useRef, useEffect } from 'react';

const Chat = ({ alertMessages }) => {
  const alertMessagesRef = useRef(null);

  useEffect(() => {
    if (alertMessagesRef.current) {
      alertMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [alertMessages]);

  return (
    <div className="chat-container">
      <div className="chat-alertMessages">
        {alertMessages.map((message, index) => (
          <div key={index} className="chat-alertMessage">
            {message}
          </div>
        ))}
      </div>
      <div ref={alertMessagesRef} />
    </div>
  );
};

export default Chat;