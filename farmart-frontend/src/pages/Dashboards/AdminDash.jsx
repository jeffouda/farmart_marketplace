import { useState } from 'react';
import { useAppSelector } from '../../store/hooks';

const AdminDash = () => {
  const { user } = useAppSelector((state) => state.auth);
  
  // Mock admin data
  const [stats] = useState({
    totalUsers: 1250,
    activeListings: 340,
    pendingDisputes: 5,
    totalRevenue: 4500000
  });

  const [recentUsers] = useState([
    { id: 1, name: 'John Doe', role: 'farmer', status: 'active' },
    { id: 2, name: 'Jane Smith', role: 'buyer', status: 'active' },
    { id: 3, name: 'Bob Wilson', role: 'farmer', status: 'pending' },
  ]);

  const [disputes] = useState([
    { id: 101, buyer: 'Alice Brown', farmer: 'Bob Wilson', reason: 'Animal health issue', status: 'open' },
    { id: 102, buyer: 'Charlie Davis', farmer: 'John Doe', reason: 'Delivery delay', status: 'under_review' },
  ]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
      <p className="text-gray-600 mb-8">Welcome back, {user?.first_name}</p>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600">Total Users</p>
          <p className="text-3xl font-bold">{stats.totalUsers}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600">Active Listings</p>
          <p className="text-3xl font-bold">{stats.activeListings}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600">Pending Disputes</p>
          <p className="text-3xl font-bold text-red-600">{stats.pendingDisputes}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600">Total Revenue</p>
          <p className="text-3xl font-bold text-green-600">
            KES {(stats.totalRevenue / 1000).toFixed(0)}K
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Recent Users */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Users</h2>
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-600 border-b">
                <th className="pb-2">Name</th>
                <th className="pb-2">Role</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentUsers.map((u) => (
                <tr key={u.id} className="border-b">
                  <td className="py-2">{u.name}</td>
                  <td className="py-2 capitalize">{u.role}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      u.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {u.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Active Disputes */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Active Disputes</h2>
          {disputes.length === 0 ? (
            <p className="text-gray-600">No active disputes</p>
          ) : (
            <div className="space-y-4">
              {disputes.map((d) => (
                <div key={d.id} className="border p-4 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">{d.reason}</p>
                      <p className="text-sm text-gray-600">
                        Buyer: {d.buyer} | Farmer: {d.farmer}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-sm ${
                      d.status === 'open' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {d.status.replace('_', ' ')}
                    </span>
                  </div>
                  <button className="mt-2 text-green-600 text-sm hover:underline">
                    View Details →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDash;
