import { Link } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Buy & Sell Livestock with Confidence
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            Kenya's trusted marketplace for cattle, goats, sheep, and more
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/browse" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100">
              Browse Animals
            </Link>
            <Link to="/register?role=farmer" className="border-2 border-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700">
              Start Selling
            </Link>
          </div>
        </div>
      </div>
      
      {/* Features */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose FarmAT?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold mb-2">Secure Payments</h3>
            <p className="text-gray-600">M-Pesa integration with escrow protection for safe transactions</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">✓</div>
            <h3 className="text-xl font-semibold mb-2">Verified Farmers</h3>
            <p className="text-gray-600">All sellers are verified to ensure quality and trust</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">🚚</div>
            <h3 className="text-xl font-semibold mb-2">Delivery Support</h3>
            <p className="text-gray-600">Arrange delivery for your purchased livestock</p>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>© 2026 FarmAT. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
