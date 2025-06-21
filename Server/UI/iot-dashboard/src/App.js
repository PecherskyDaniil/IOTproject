import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DevicePage from './pages/DevicePage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/device/:deviceHash" element={<DevicePage />} />
      </Routes>
    </Router>
  );
};

export default App;