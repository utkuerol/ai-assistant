"use client";

import { useEffect, useState } from 'react';
import Siriwave from 'react-siriwave';

enum Speaker {
  User = "You",
  AI = "AI"
}

enum TransmissionCode {
  Start = "___start___",
  Stop = "___stop___"
}

type Message = {
  sender: Speaker,
  text: string,
}

const negateSpeaker = (speaker: Speaker) => {
  if (speaker === Speaker.AI) return Speaker.User

  return Speaker.AI
}

export default function Home() {
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState<Message | undefined>(undefined);
  const [currentSpeaker, setCurrentSpeaker] = useState<Speaker | undefined>(undefined);
  const [transmission, setTransmission] = useState<string>('');
  const [isTransmitting, setIsTransmitting] = useState<boolean>(false);

  useEffect(() => {
    const transcriptionSocket = new WebSocket('ws://localhost:8000/ws/transcription');
    const aiMessageSocket = new WebSocket('ws://localhost:8000/ws/ai-message');

    transcriptionSocket.onmessage = (event) => {
      if (event.data == TransmissionCode.Start || currentSpeaker === Speaker.AI) {
        setIsTransmitting(true);
        setCurrentSpeaker(Speaker.User)
      } else if (event.data == TransmissionCode.Stop) {
        setIsTransmitting(false);
        setCurrentSpeaker(Speaker.AI)
      } else {
        setTransmission(event.data)
      }
    };

    aiMessageSocket.onmessage = (event) => {
      if (event.data == TransmissionCode.Start || currentSpeaker === Speaker.User) {
        setIsTransmitting(true);
        setCurrentSpeaker(Speaker.AI)
      } else if (event.data == TransmissionCode.Stop) {
        setIsTransmitting(false);
        setCurrentSpeaker(Speaker.User)
      } else {
        setTransmission(event.data)
      }
    };

    return () => {
      transcriptionSocket.close();
      aiMessageSocket.close();
    };
  }, []);


  useEffect(() => {
    if (currentSpeaker === Speaker.AI) {
      const updatedMessage: Message = {
        sender: Speaker.AI,
        text: currentMessage?.text + transmission
      }
      setCurrentMessage(updatedMessage);
    } else {
      setCurrentMessage({ sender: Speaker.User, text: transmission });
    }
  }, [transmission])


  useEffect(() => {
    if (currentMessage && currentSpeaker) {
      const updatedHistory: Message[] = [...chatHistory, { sender: negateSpeaker(currentSpeaker), text: currentMessage.text }]
      setChatHistory(updatedHistory);
      setCurrentMessage({ sender: currentSpeaker, text: '' });
    }

  }, [currentSpeaker])


  return (
    <main>
      <header className="text-center">
        <p className="text-6xl">The Machine</p>
      </header>
      <div>
        <div className='p-12 flex justify-center'>
          <Siriwave
            color={currentSpeaker === Speaker.AI ? "#003366" : "#fff"}
            cover={false}
            speed={0.1}
            amplitude={isTransmitting ? 1.3 : 0}
            frequency={3}
          />
        </div>

        <div className='chat'>
          {chatHistory.filter((msg) => msg.sender && msg.text).map((msg, index) => (
            <div key={index} className={`message ${msg.sender === Speaker.AI ? 'justify-start' : 'justify-end'}`}>
              <div
                className={msg.sender === Speaker.AI ? 'message-ai' : 'message-user'}
              >
                <p>{msg.sender}: {msg.text}</p>
              </div>
            </div>
          ))}

          {(currentMessage && currentSpeaker) && (
            <div className={`message ${currentSpeaker === Speaker.AI ? 'justify-start' : 'justify-end'}`}>
              <div
                className={currentMessage.sender === Speaker.AI ? 'message-ai' : 'message-user'}
              >
                <p>{currentMessage.sender}: {currentMessage.text}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
