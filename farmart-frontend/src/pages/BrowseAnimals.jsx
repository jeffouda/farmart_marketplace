import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchLivestock } from "../features/livestock/livestockSlice";
// Check this line carefully:
import AnimalCard from "../components/AnimalCard";

const BrowseAnimals = () => {
  const dispatch = useDispatch();
  const { items, status } = useSelector((state) => state.livestock);

  const [filters, setFilters] = useState({
    type: "",
    location: "",
  });

  useEffect(() => {
    dispatch(fetchLivestock(filters));
  }, [filters, dispatch]);

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Browse Livestock</h1>

      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-8 bg-white p-4 rounded-lg shadow-sm border">
        <select
          name="type"
          className="p-2 border rounded bg-gray-50"
          onChange={handleFilterChange}
        >
          <option value="">All Animals</option>
          <option value="cow">Cows</option>
          <option value="goat">Goats</option>
          <option value="sheep">Sheep</option>
        </select>

        <input
          type="text"
          name="location"
          placeholder="Filter by Location (e.g., Kiambu)"
          className="p-2 border rounded flex-grow bg-gray-50"
          onChange={handleFilterChange}
        />
      </div>

      {status === "loading" && (
        <p className="text-center">Loading fresh listings...</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((animal) => (
          <AnimalCard key={animal.id} animal={animal} />
        ))}
      </div>

      {status === "succeeded" && items.length === 0 && (
        <p className="text-center text-gray-500">
          No animals found matching your search.
        </p>
      )}
    </div>
  );
};

export default BrowseAnimals;
