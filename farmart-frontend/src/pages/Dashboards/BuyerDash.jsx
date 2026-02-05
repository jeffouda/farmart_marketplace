import { useState } from 'react';
import Navbar from '../../components/layout/Navbar';

const BuyerDash = () => {
  const [activeTab, setActiveTab] = useState('orders');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Buyer Dashboard</h1>
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b px-6 py-4">
            <nav className="flex gap-6">
              {['orders', 'wishlist', 'settings'].map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`capitalize ${activeTab === tab ? 'text-primary-600 font-semibold' : 'text-gray-500'}`}>
                  {tab}
                </button>
              ))}
            </nav>
          </div>
          <div className="p-6">
            <p className="text-gray-500">Your {activeTab} will appear here.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerDash;
