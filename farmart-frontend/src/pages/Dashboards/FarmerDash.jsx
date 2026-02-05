import { useState } from 'react';
import Navbar from '../../components/layout/Navbar';

const FarmerDash = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Farmer Dashboard</h1>
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b px-6 py-4">
            <nav className="flex gap-6">
              {['overview', 'inventory', 'orders', 'analytics', 'payouts'].map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`capitalize ${activeTab === tab ? 'text-primary-600 font-semibold' : 'text-gray-500'}`}>
                  {tab}
                </button>
              ))}
            </nav>
          </div>
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-4 gap-6">
                <div className="bg-primary-50 p-6 rounded-lg"><p className="text-sm text-gray-600">Total Listings</p><p className="text-3xl font-bold text-primary-600">12</p></div>
                <div className="bg-green-50 p-6 rounded-lg"><p className="text-sm text-gray-600">Active Sales</p><p className="text-3xl font-bold text-green-600">5</p></div>
                <div className="bg-secondary-50 p-6 rounded-lg"><p className="text-sm text-gray-600">Total Revenue</p><p className="text-3xl font-bold text-secondary-600">KES 450,000</p></div>
                <div className="bg-blue-50 p-6 rounded-lg"><p className="text-sm text-gray-600">Orders</p><p className="text-3xl font-bold text-blue-600">8</p></div>
              </div>
            )}
            {activeTab === 'inventory' && <p>Your livestock listings will appear here.</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FarmerDash;
