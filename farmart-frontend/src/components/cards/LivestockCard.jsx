import { Link } from 'react-router-dom';

const LivestockCard = ({ livestock }) => {
  const {
    id,
    species,
    breed,
    age,
    weight,
    price,
    location,
    images,
    seller,
  } = livestock;

  const mainImage = images?.[0] || 'https://placehold.co/400x300?text=No+Image';

  return (
    <Link to={`/animals/${id}`} className="block">
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        <img
          src={mainImage}
          alt={`${breed} ${species}`}
          className="w-full h-48 object-cover"
        />
        <div className="p-4">
          <h3 className="font-semibold text-lg text-gray-900">
            {breed} {species}
          </h3>
          <p className="text-gray-600 text-sm mb-2">{location}</p>
          <div className="flex justify-between text-sm text-gray-500 mb-3">
            <span>{age} months</span>
            <span>{weight} kg</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-green-600 font-bold">
              KES {price?.toLocaleString()}
            </span>
            <span className="text-yellow-500 text-sm">
              ★ {seller?.rating || 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default LivestockCard;
