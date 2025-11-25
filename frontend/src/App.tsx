import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { StoryViewer } from './pages/StoryViewer';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/story/:id" element={<StoryViewer />} />
      </Routes>
    </Router>
  );
}

export default App;
