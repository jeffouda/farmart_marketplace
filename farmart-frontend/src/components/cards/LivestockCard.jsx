import { Link } from 'react-router-dom';

// Cloudinary URL optimization function
// Handles URLs with and without /v version tags
const optimizeImageUrl = (url) => {
  if (!url) return url;
  
  // Get cloud name from environment
  const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
  
  // Check if it's a Cloudinary URL
  if (url.includes('cloudinary.com') && cloudName) {
    // Remove existing version tag if present (/v1234567890)
    const urlWithoutVersion = url.replace(/\/v\d+\//, '/');
    
    // Check if already has optimization parameters
    if (urlWithoutVersion.includes('w_')) {
      return urlWithoutVersion;
    }
    
    // Add optimization parameters
    // w_400,h_300,c_fill,q_auto,f_auto for card thumbnails
    const optimizedUrl = urlWithoutVersion.replace(
      `/upload/`,
      `/upload/w_400,h_300,c_fill,q_auto,f_auto/`
    );
    
    return optimizedUrl;
  }
  
  return url;
};

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

  const mainImageRaw = images?.[0] || 'https://placehold.co/400x300?text=No+Image';
  const mainImage = optimizeImageUrl(mainImageRaw);

  return (
    <Link to={`/animals/${id}`} className="block">
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        <img
          src={mainImage}
          alt={`${breed} ${species}`}
          className="w-full h-48 object-cover"
          onError={(e) => {
            // Fallback if optimized URL fails
            e.target.src = mainImageRaw || 'https://placehold.co/400x300?text=No+Image';
          }}
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

export { optimizeImageUrl };

export default LivestockCard;
