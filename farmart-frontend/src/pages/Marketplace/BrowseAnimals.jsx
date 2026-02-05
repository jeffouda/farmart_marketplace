import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Grid, List, ChevronDown, ShoppingCart, Heart, MapPin, Calendar, Tag } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchLivestock } from '../../features/livestock/livestockSlice';
import { optimizeImageUrl } from '../../components/cards/LivestockCard';

// BrowseAnimals.jsx - uses optimizeImageUrl from LivestockCard

const BrowseAnimals = () => {
  const dispatch = useDispatch();
  const [filters, setFilters] = useState({
    species: '',
    minPrice: '',
    maxPrice: '',
    location: '',
    sortBy: 'newest'
  });

  useEffect(() => {
    dispatch(fetchLivestock());
  }, [dispatch]);

  const loading = useSelector((state) => state.livestock.status === 'loading');
  const error = useSelector((state) => state.livestock.error);
  const animals = useSelector((state) => state.livestock.items);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const filteredAnimals = animals.filter(animal => {
    if (filters.species && animal.species !== filters.species) return false;
    if (filters.minPrice && animal.price < parseFloat(filters.minPrice)) return false;
    if (filters.maxPrice && animal.price > parseFloat(filters.maxPrice)) return false;
    if (filters.location && !animal.location?.toLowerCase().includes(filters.location.toLowerCase())) return false;
    return true;
  });

  const speciesOptions = ['Cattle', 'Goats', 'Sheep', 'Pigs', 'Chickens', 'Other'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Browse Marketplace</h1>
          <p className="text-green-100">Find quality livestock from trusted farmers across Kenya</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar Filters */}
          <div className="lg:w-1/4">
            <div className="bg-white rounded-xl shadow-md p-6 sticky top-24">
              <div className="flex items-center gap-2 mb-4">
                <Filter className="w-5 h-5 text-green-600" />
                <h2 className="font-semibold text-gray-800">Filters</h2>
              </div>

              <div className="space-y-4">
                {/* Species */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Species</label>
                  <select
                    name="species"
                    value={filters.species}
                    onChange={handleFilterChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="">All Species</option>
                    {speciesOptions.map(species => (
                      <option key={species} value={species.toLowerCase()}>{species}</option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price Range (KES)</label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      name="minPrice"
                      placeholder="Min"
                      value={filters.minPrice}
                      onChange={handleFilterChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                    <input
                      type="number"
                      name="maxPrice"
                      placeholder="Max"
                      value={filters.maxPrice}
                      onChange={handleFilterChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      name="location"
                      placeholder="Enter county..."
                      value={filters.location}
                      onChange={handleFilterChange}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                  <select
                    name="sortBy"
                    value={filters.sortBy}
                    onChange={handleFilterChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="newest">Newest First</option>
                    <option value="price-low">Price: Low to High</option>
                    <option value="price-high">Price: High to Low</option>
                  </select>
                </div>

                {/* Clear Filters */}
                <button
                  onClick={() => setFilters({ species: '', minPrice: '', maxPrice: '', location: '', sortBy: 'newest' })}
                  className="w-full px-4 py-2 text-green-600 border border-green-600 rounded-lg hover:bg-green-50 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>

          {/* Animal Grid */}
          <div className="lg:w-3/4">
            {/* Results Count */}
            <div className="flex justify-between items-center mb-4">
              <p className="text-gray-600">
                Showing <span className="font-semibold text-gray-800">{filteredAnimals.length}</span> animals
              </p>
              <div className="flex gap-2">
                <button className="p-2 bg-green-600 text-white rounded-lg">
                  <Grid className="w-5 h-5" />
                </button>
              </div>
            </div>

            {loading ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse">
                    <div className="h-48 bg-gray-200" />
                    <div className="p-4 space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-3/4" />
                      <div className="h-4 bg-gray-200 rounded w-1/2" />
                      <div className="h-6 bg-gray-200 rounded w-1/4" />
                    </div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                {error}
              </div>
            ) : filteredAnimals.length === 0 ? (
              <div className="bg-white rounded-xl shadow-md p-12 text-center">
                <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">No animals found</h3>
                <p className="text-gray-500 mb-4">Try adjusting your filters</p>
                <button
                  onClick={() => setFilters({ species: '', minPrice: '', maxPrice: '', location: '', sortBy: 'newest' })}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredAnimals.map((animal) => (
                  <Link
                    key={animal.id}
                    to={`/animal/${animal.id}`}
                    className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow group"
                  >
                    <div className="relative">
                      <img
                        src={optimizeImageUrl(animal.images?.[0], 400, 300)}
                        alt={animal.name || animal.breed}
                        className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <span className="absolute top-3 left-3 bg-green-600 text-white text-xs px-2 py-1 rounded-full capitalize">
                        {animal.species}
                      </span>
                      <button className="absolute top-3 right-3 bg-white/80 p-2 rounded-full hover:bg-white transition-colors">
                        <Heart className="w-4 h-4 text-gray-600 hover:text-red-500" />
                      </button>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-800 mb-1">{animal.name || animal.breed}</h3>
                      <div className="flex items-center gap-1 text-sm text-gray-500 mb-2">
                        <MapPin className="w-4 h-4" />
                        {animal.location || 'Kenya'}
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xl font-bold text-green-600">
                          KES {animal.price?.toLocaleString() || '0'}
                        </span>
                        <button className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 transition-colors text-sm">
                          <ShoppingCart className="w-4 h-4" />
                          Add
                        </button>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrowseAnimals;
