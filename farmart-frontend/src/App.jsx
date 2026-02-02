import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from './store/hooks';

import Home from './pages/Home';
import BrowseAnimals from './pages/BrowseAnimals';
import AnimalDetails from './pages/AnimalDetails';
import Login from './pages/Login';
import Register from './pages/Register';
import Settings from './pages/Settings';
import Verification from './pages/Verification';
import FarmerDash from './pages/Dashboards/FarmerDash';
import BuyerDash from './pages/Dashboards/BuyerDash';
import AdminDash from './pages/Dashboards/AdminDash';

const ProtectedRoute = ({ children, roles }) => {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/browse" element={<BrowseAnimals />} />
      <Route path="/animal/:id" element={<AnimalDetails />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} />

      <Route path="/dashboard" element={
        <ProtectedRoute>
          {user?.role === 'farmer' ? <FarmerDash /> : user?.role === 'admin' ? <AdminDash /> : <BuyerDash />}
        </ProtectedRoute>
      } />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/verification" element={<ProtectedRoute><Verification /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
