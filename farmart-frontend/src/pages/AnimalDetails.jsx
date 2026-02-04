import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  FaMapMarkerAlt,
  FaWeightHanging,
  FaBirthdayCake,
} from "react-icons/fa";

const AnimalDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [animal, setAnimal] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await axios.get(`/api/livestock/${id}`);
        setAnimal(response.data);
      } catch (error) {
        console.error("Error fetching animal details:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id]);

  if (loading)
    return <div className="text-center mt-10">Loading details...</div>;
  if (!animal)
    return <div className="text-center mt-10">Animal not found.</div>;

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 text-green-600 font-bold"
      >
        ← Back to Browse
      </button>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden flex flex-col md:flex-row">
        <img
          src={animal.image_url || "https://via.placeholder.com/500"}
          className="w-full md:w-1/2 h-96 object-cover"
          alt={animal.breed}
        />

        <div className="p-8 md:w-1/2">
          <h1 className="text-3xl font-bold capitalize mb-2">
            {animal.breed} {animal.animal_type}
          </h1>
          <div className="flex items-center text-gray-600 mb-4">
            <FaMapMarkerAlt className="mr-2" /> <span>{animal.location}</span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-500 flex items-center">
                <FaBirthdayCake className="mr-1" /> Age
              </p>
              <p className="font-semibold">{animal.age} months</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-500 flex items-center">
                <FaWeightHanging className="mr-1" /> Weight
              </p>
              <p className="font-semibold">{animal.weight} kg</p>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="font-bold text-gray-700">Health Notes:</h3>
            <p className="text-gray-600 italic">
              "{animal.health_notes || "No specific health notes provided."}"
            </p>
          </div>

          <div className="mt-8 flex items-center justify-between">
            <span className="text-2xl font-bold text-green-700">
              KES {animal.price}
            </span>
            <button className="bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 transition">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimalDetails;
