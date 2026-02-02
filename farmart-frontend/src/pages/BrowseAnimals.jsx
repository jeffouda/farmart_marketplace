import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchLivestock, setFilters } from '../features/livestock/livestockSlice';
import Navbar from '../components/layout/Navbar';
import LivestockCard from '../components/cards/LivestockCard';
import Loader from '../components/common/Loader';

const BrowseAnimals = () => {
  const dispatch = useAppDispatch();
  const { items, total, loading, filters } = useAppSelector((state) => state.livestock);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    dispatch(fetchLivestock(filters));
  }, [dispatch, filters]);

  const handleSearch = (e) => {
    e.preventDefault();
    dispatch(setFilters({ q: searchTerm }));
  };

  const handleFilterChange = (key, value) => {
    dispatch(setFilters({ [key]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <form onSubmit={handleSearch} className="flex gap-4 mb-6">
            <input
              type="text"
              placeholder="Search animals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 rounded-lg border-gray-300 border px-4 py-2"
            />
            <button type="submit" className="bg-primary-600 text-white px-6 py-2 rounded-lg">Search</button>
          </form>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <select onChange={(e) => handleFilterChange('species', e.target.value)} className="rounded-lg border-gray-300 border px-4 py-2">
              <option value="">All Species</option>
              <option value="cattle">Cattle</option>
              <option value="goat">Goats</option>
              <option value="sheep">Sheep</option>
            </select>
            <input type="number" placeholder="Min Price" onChange={(e) => handleFilterChange('min_price', e.target.value)} className="rounded-lg border-gray-300 border px-4 py-2" />
            <input type="number" placeholder="Max Price" onChange={(e) => handleFilterChange('max_price', e.target.value)} className="rounded-lg border-gray-300 border px-4 py-2" />
            <select onChange={(e) => handleFilterChange('sort', e.target.value)} className="rounded-lg border-gray-300 border px-4 py-2">
              <option value="created_at">Newest First</option>
              <option value="price">Price: Low to High</option>
            </select>
          </div>
        </div>
        {loading ? (
          <div className="flex justify-center py-20"><Loader size="lg" /></div>
        ) : (
          <>
            <p className="mb-4 text-gray-600">{total} animals found</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {items.map((animal) => <LivestockCard key={animal.id} livestock={animal} />)}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default BrowseAnimals;
