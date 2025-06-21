import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchDeviceData, fetchDeviceHistory } from '../services/api';
import { format, parseISO } from 'date-fns';
import './DevicePage.css';

const DevicePage = () => {
  const { deviceHash } = useParams();
  const navigate = useNavigate();
  const [deviceData, setDeviceData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [device, history] = await Promise.all([
          fetchDeviceData(deviceHash),
          fetchDeviceHistory(deviceHash)
        ]);
        
        const formattedHistory = history.map(item => ({
          ...item,
          created: format(parseISO(item.created), 'HH:mm'),
          turbidity: parseFloat(item.turbidity),
          waterlevel: parseFloat(item.waterlevel)
        }));

        setDeviceData(device);
        setHistoryData(formattedHistory);
      } catch (err) {
        setError('Ошибка загрузки данных');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [deviceHash]);

  if (loading) return (
    <div className="loading-container">
      <div className="bubble-animation">
        {[...Array(5)].map((_, i) => <div key={i} className="bubble" />)}
      </div>
      <p>Загрузка данных...</p>
    </div>
  );

  if (error) return <div className="error-message">{error}</div>;
  if (!deviceData) return <div className="no-data">Данные не найдены</div>;

  return (
    <div className="device-page">
      {/* Фон с морской тематикой */}
      <div className="aquarium-background">
        {[...Array(10)].map((_, i) => (
          <div 
            key={`particle-${i}`}
            className="aquarium-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${5 + Math.random() * 15}px`,
              height: `${5 + Math.random() * 15}px`,
              animationDuration: `${10 + Math.random() * 20}s`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      {/* Основное содержимое */}
      <div className="device-content">
        <header className="device-header">
          <div>
            <h1>{deviceData.info.device_name}</h1>
            <p className="device-id">Hash: {deviceData.info.unique_hash}</p>
          </div>
          <button onClick={() => navigate('/')} className="back-button">
            Назад
          </button>
        </header>
<p>Интервал кормления: <strong>{deviceData.info.feed_interval} часов</strong></p>
        <div className="current-metrics">
            
          <div className="metric-card">
            <h3>Текущая мутность</h3>
            <p className="metric-value">{deviceData.metrics.turbidity}</p>
            <p className="metric-unit"></p>
          </div>
          
          <div className="metric-card">
            <h3>Уровень воды</h3>
            <p className="metric-value">{deviceData.metrics.waterlevel}</p>
            <p className="metric-unit"></p>
          </div>
          
          <div className="metric-card">
            <h3>Последнее обновление</h3>
            <p className="metric-value">
              {format(parseISO(deviceData.metrics.created), 'HH:mm')}
            </p>
          </div>
        </div>

        <div className="charts-section">
          <div className="chart-container">
            <h3>История мутности</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis 
                  dataKey="created" 
                  tick={{ fill: '#555' }}
                />
                <YAxis tick={{ fill: '#555' }} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="turbidity" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>История уровня воды</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis 
                  dataKey="created" 
                  tick={{ fill: '#555' }}
                />
                <YAxis tick={{ fill: '#555' }} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="waterlevel" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="device-footer">
          <p>Владелец: <strong>{deviceData.owner.name}</strong></p>
          
        </div>
      </div>
    </div>
  );
};

export default DevicePage;