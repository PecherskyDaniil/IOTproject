import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

const MetricsChart = ({ data, metric, title, color }) => {
  const formattedData = data.map(item => ({
    ...item,
    created: format(parseISO(item.created), 'HH:mm'),
    [metric]: parseFloat(item[metric])
  }));

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis 
            dataKey="created" 
            tick={{ fill: '#555' }}
          />
          <YAxis tick={{ fill: '#555' }} />
          <Tooltip 
            contentStyle={{
              background: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey={metric} 
            stroke={color} 
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;