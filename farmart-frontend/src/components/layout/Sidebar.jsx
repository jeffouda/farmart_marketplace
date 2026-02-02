import { Link, useLocation } from 'react-router-dom';
import { useAppSelector } from '../../store/hooks';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAppSelector((state) => state.auth);

  const isActive = (path) => location.pathname === path;

  const farmerLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/dashboard/listings', label: 'My Listings', icon: '🐄' },
    { path: '/dashboard/add-livestock', label: 'Add Livestock', icon: '➕' },
    { path: '/dashboard/bulk-upload', label: 'Bulk Upload', icon: '📁' },
    { path: '/dashboard/orders', label: 'Orders', icon: '📦' },
    { path: '/dashboard/analytics', label: 'Analytics', icon: '📈' },
  ];

  const buyerLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/dashboard/cart', label: 'Cart', icon: '🛒' },
    { path: '/dashboard/orders', label: 'My Orders', icon: '📦' },
    { path: '/dashboard/favorites', label: 'Favorites', icon: '❤️' },
  ];

  const adminLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/dashboard/users', label: 'Users', icon: '👥' },
    { path: '/dashboard/disputes', label: 'Disputes', icon: '⚠️' },
    { path: '/dashboard/commissions', label: 'Commissions', icon: '💰' },
  ];

  const links = user?.role === 'admin' ? adminLinks : user?.role === 'farmer' ? farmerLinks : buyerLinks;

  return (
    <aside className="w-64 bg-white shadow-sm min-h-screen">
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-700 mb-4 capitalize">
          {user?.role} Menu
        </h2>
        <nav className="space-y-2">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition ${
                isActive(link.path)
                  ? 'bg-green-100 text-green-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
