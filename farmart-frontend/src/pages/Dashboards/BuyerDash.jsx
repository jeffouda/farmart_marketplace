import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { ShoppingBag, Heart, Settings, MapPin, Calendar, Phone, Mail, Package, Clock, CheckCircle, XCircle } from 'lucide-react';
import Navbar from '../../components/layout/Navbar';
import { fetchOrders, fetchWishlist, fetchBuyerProfile } from '../../features/buyer/buyerSlice';
import { optimizeImageUrl } from '../../components/cards/LivestockCard';

const BuyerDash = () => {
  const dispatch = useDispatch();
  const { orders, wishlist, profile, ordersStatus, wishlistStatus, profileStatus } = useSelector((state) => state.buyer);
  const [activeTab, setActiveTab] = useState('orders');

  useEffect(() => {
    dispatch(fetchOrders());
    dispatch(fetchWishlist());
    dispatch(fetchBuyerProfile());
  }, [dispatch]);

  const loading = ordersStatus === 'loading' || wishlistStatus === 'loading' || profileStatus === 'loading';

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Buyer Dashboard</h1>
        
        {/* Profile Summary */}
        {profile && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {profile.name?.[0] || 'U'}
              </div>
              <div>
                <h2 className="text-xl font-semibold">{profile.name || 'Buyer'}</h2>
                <p className="text-gray-500">{profile.email}</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b px-6 py-4">
            <nav className="flex gap-6">
              {[
                { id: 'orders', icon: ShoppingBag, label: 'Orders' },
                { id: 'wishlist', icon: Heart, label: 'Wishlist' },
                { id: 'settings', icon: Settings, label: 'Settings' }
              ].map(({ id, icon: Icon, label }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`flex items-center gap-2 capitalize ${activeTab === id ? 'text-green-600 font-semibold' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  <Icon className="w-5 h-5" />
                  {label}
                  {id === 'wishlist' && wishlist.length > 0 && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{wishlist.length}</span>
                  )}
                </button>
              ))}
            </nav>
          </div>
          
          <div className="p-6">
            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse bg-gray-100 rounded-lg p-4 h-24"></div>
                ))}
              </div>
            ) : activeTab === 'orders' ? (
              orders.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">No orders yet</h3>
                  <p className="text-gray-500">Start shopping to see your orders here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-semibold">Order #{order.id}</h3>
                          <p className="text-sm text-gray-500 flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {formatDate(order.created_at)}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                          {order.status || 'Pending'}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-4 mb-4">
                        {order.items?.map((item, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <img
                              src={optimizeImageUrl(item.images?.[0], 80, 80)}
                              alt={item.name}
                              className="w-16 h-16 object-cover rounded-lg"
                            />
                            <div>
                              <p className="font-medium">{item.name}</p>
                              <p className="text-sm text-gray-500">Qty: {item.quantity || 1}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex justify-between items-center pt-4 border-t">
                        <div className="text-sm">
                          {order.shipping_address && (
                            <p className="text-gray-500 flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {order.shipping_address}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Total</p>
                          <p className="text-xl font-bold text-green-600">KES {order.total?.toLocaleString() || '0'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : activeTab === 'wishlist' ? (
              wishlist.length === 0 ? (
                <div className="text-center py-12">
                  <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Your wishlist is empty</h3>
                  <p className="text-gray-500">Save items you love to your wishlist</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {wishlist.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <img
                        src={optimizeImageUrl(item.images?.[0], 200, 150)}
                        alt={item.name}
                        className="w-full h-40 object-cover rounded-lg mb-3"
                      />
                      <h3 className="font-semibold">{item.name || item.breed}</h3>
                      <p className="text-gray-500 text-sm mb-2">{item.species}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-xl font-bold text-green-600">KES {item.price?.toLocaleString() || '0'}</span>
                        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                          Add to Cart
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              <div className="max-w-md">
                <h3 className="text-lg font-semibold mb-4">Account Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input
                      type="text"
                      defaultValue={profile?.name || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      defaultValue={profile?.email || ''}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input
                      type="tel"
                      defaultValue={profile?.phone || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Default Shipping Address</label>
                    <textarea
                      defaultValue={profile?.shipping_address || ''}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  <button className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors">
                    Save Changes
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerDash;
