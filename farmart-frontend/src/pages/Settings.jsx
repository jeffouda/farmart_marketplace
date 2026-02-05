import { useState } from 'react';
import Navbar from '../components/layout/Navbar';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b px-6 py-4">
            <nav className="flex gap-6">
              {['profile', 'payments', 'security', 'notifications'].map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`capitalize ${activeTab === tab ? 'text-primary-600 font-semibold' : 'text-gray-500'}`}>
                  {tab}
                </button>
              ))}
            </nav>
          </div>
          <div className="p-6"><p className="text-gray-500">Settings for {activeTab}.</p></div>
        </div>
      </div>
    </div>
  );
};
export default Settings;
