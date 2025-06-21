import axios from 'axios';

const API_BASE = 'http://192.168.0.7:8000/api';

export const fetchDeviceData = async (deviceHash) => {
  const response = await axios.get(`${API_BASE}/devices/${deviceHash}`);
  return response.data;
};

export const fetchDeviceHistory = async (deviceHash) => {
  const response = await axios.get(`${API_BASE}/data/get/${deviceHash}`);
  return response.data;
};