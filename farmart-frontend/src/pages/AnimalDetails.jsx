import { useParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { useEffect, useState } from 'react';
import { addToCart } from '../features/checkout/cartSlice';

const AnimalDetails = () => {
  const { id } = useParams();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  
  // Mock animal data - replace with actual API call
  const [animal, setAnimal] = useState({
    id: id,
    species: 'Cattle',
    breed: 'Friesian',
    age: 24,
    weight: 450,
    price: 85000,
    location: 'Nairobi County',
    description: 'High quality dairy cattle, well vaccinated and healthy.',
    images: ['https://placehold.co/600x400?text=Cattle'],
    seller: {
      name: 'John Farmer',
      phone: '+254712345678',
      rating: 4.5
    }
  });

  const handleAddToCart = () => {
    if (!user) {
      alert('Please login to add items to cart');
      return;
    }
    dispatch(addToCart(animal));
    alert('Added to cart!');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid md:grid-cols-2 gap-8">
        {/* Image Gallery */}
        <div className="space-y-4">
          <img 
            src={animal.images[0]} 
            alt={animal.species} 
            className="w-full h-96 object-cover rounded-lg shadow-lg"
          />
        </div>

        {/* Details */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {animal.breed} {animal.species}
            </h1>
            <p className="text-gray-600 mt-2">{animal.location}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Age</p>
              <p className="text-xl font-semibold">{animal.age} months</p>
            </div>
            <div className="bg-gray-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Weight</p>
              <p className="text-xl font-semibold">{animal.weight} kg</p>
            </div>
          </div>

          <div>
            <p className="text-3xl font-bold text-green-600">
              KES {animal.price.toLocaleString()}
            </p>
          </div>

          <p className="text-gray-700">{animal.description}</p>

          <div className="border-t pt-4">
            <h3 className="font-semibold mb-2">Seller Information</h3>
            <p>{animal.seller.name}</p>
            <p className="text-gray-600">{animal.seller.phone}</p>
            <p className="text-yellow-500">★ {animal.seller.rating}</p>
          </div>

          <button
            onClick={handleAddToCart}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnimalDetails;
