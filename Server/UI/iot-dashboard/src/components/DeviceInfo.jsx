import { format, parseISO } from 'date-fns';

const DeviceInfo = ({ info, metrics, owner }) => {
  return (
    <div className="device-info">
      <div className="header">
        <h2>{info.device_name}</h2>
        <span className="device-id">ID: {info.unique_hash}</span>
      </div>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Текущая мутность</h4>
          <p className="value">{metrics.turbidity} <span>NTU</span></p>
        </div>
        
        <div className="metric-card">
          <h4>Уровень воды</h4>
          <p className="value">{metrics.waterlevel} <span>см</span></p>
        </div>
        
        <div className="metric-card">
          <h4>Интервал обновления</h4>
          <p className="value">{info.feed_interval} <span>мин</span></p>
        </div>
        
        <div className="metric-card">
          <h4>Последнее обновление</h4>
          <p className="value">{format(parseISO(metrics.created), 'dd.MM.yyyy HH:mm')}</p>
        </div>
      </div>
      
      <div className="owner-info">
        <p>Владелец: <strong>{owner.name}</strong></p>
      </div>
    </div>
  );
};

export default DeviceInfo;