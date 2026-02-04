import React from "react";
import { Link } from "react-router-dom";

const AnimalCard = ({ animal }) => {
  return (
    <div className="border rounded-lg shadow-md overflow-hidden bg-white hover:shadow-lg transition-shadow">
      <img
        src={
          animal.image_url ||
          "https://via.placeholder.com/300x200?text=Livestock"
        }
        alt={animal.breed}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-xl font-bold capitalize">
          {animal.breed} ({animal.animal_type})
        </h3>
        <p className="text-gray-600">Location: {animal.location}</p>
        <p className="text-green-600 font-bold mt-2">KES {animal.price}</p>

        <Link
          to={`/animals/${animal.id}`}
          className="mt-4 block text-center bg-green-600 text-white py-2 rounded hover:bg-green-700"
        >
          View Details
        </Link>
      </div>
    </div>
  );
};

export default AnimalCard;
