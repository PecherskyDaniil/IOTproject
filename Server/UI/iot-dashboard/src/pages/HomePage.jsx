import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const [deviceHash, setDeviceHash] = useState('');
  const navigate = useNavigate();
  const [bubbles, setBubbles] = useState([]);

  // Инициализация пузырьков
  useEffect(() => {
    const newBubbles = Array.from({ length: 15 }).map((_, i) => ({
      id: i,
      size: 5 + Math.random() * 15,
      left: Math.random() * 100,
      duration: 8 + Math.random() * 12,
      delay: Math.random() * 5,
      bottom: -20
    }));
    setBubbles(newBubbles);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (deviceHash.trim()) {
      navigate(`/device/${deviceHash.trim()}`);
    }
  };

  return (
    <div className="home-page">
      <div className="ocean-background">
        {/* Декоративные элементы */}
        <div className="coral coral-left"></div>
        <div className="coral coral-right"></div>
        <div className="seaweed seaweed-1"></div>
        <div className="seaweed seaweed-2"></div>
        
        {/* Анимированные пузырьки */}
        {bubbles.map(bubble => (
          <div 
            key={`bubble-${bubble.id}`}
            className="bubble"
            style={{
              left: `${bubble.left}%`,
              bottom: `${bubble.bottom}px`,
              width: `${bubble.size}px`,
              height: `${bubble.size}px`,
              animationDuration: `${bubble.duration}s`,
              animationDelay: `${bubble.delay}s`,
            }}
          />
        ))}
      </div>

      <div className="login-container">
        <div className="aquarium-logo">
          <div className="fish-logo"></div>
          <h1>AquaMonitor</h1>
        </div>
        <p>Введите Hash вашего аквариума для доступа к данным</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            value={deviceHash}
            onChange={(e) => setDeviceHash(e.target.value)}
            placeholder="Уникальный ID устройства"
            required
          />
          <button type="submit">
            <span>Погрузиться</span>
            <div className="button-bubble"></div>
          </button>
        </form>
      </div>
    </div>
  );
};

export default HomePage;