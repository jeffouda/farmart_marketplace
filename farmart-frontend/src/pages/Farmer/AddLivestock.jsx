import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { createLivestock } from '../../features/livestock/livestockSlice';
import { toast } from 'react-toastify';

const CLOUDINARY_CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || 'di7l87qmg';
const CLOUDINARY_UPLOAD_PRESET = 'farmat_unsigned';

const AddLivestock = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.livestock);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  
  const [formData, setFormData] = useState({
    animal_type: '',
    breed: '',
    gender: '',
    age_months: '',
    weight: '',
    price: '',
    location: '',
    description: '',
    reason_for_sale: '',
    health_certified: false,
    vaccinations: [],
  });

  const [vaccination, setVaccination] = useState({
    name: '',
    date_administered: '',
    next_due_date: '',
    certificate_url: '',
  });

  // Step 1: Basic Info handlers
  const handleBasicChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // Cloudinary upload function
  const uploadToCloudinary = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);
    
    const response = await fetch(
      `https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/image/upload`,
      {
        method: 'POST',
        body: formData,
      }
    );
    
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    
    return response.json();
  };

  // Dropzone callback for multi-file upload
  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    
    try {
      const uploadPromises = acceptedFiles.map((file) => uploadToCloudinary(file));
      const results = await Promise.all(uploadPromises);
      
      const imageUrls = results.map((result) => result.secure_url);
      setUploadedImages((prev) => [...prev, ...imageUrls]);
      
      toast.success(`${acceptedFiles.length} image(s) uploaded successfully`);
    } catch (err) {
      toast.error('Failed to upload images');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
    },
    maxSize: 5 * 1024 * 1024, // 5MB
  });

  // Remove image from uploaded list
  const removeImage = (index) => {
    setUploadedImages((prev) => prev.filter((_, i) => i !== index));
  };

  // Add vaccination to list
  const addVaccination = () => {
    if (vaccination.name && vaccination.date_administered) {
      setFormData((prev) => ({
        ...prev,
        vaccinations: [...prev.vaccinations, { ...vaccination }],
      }));
      setVaccination({
        name: '',
        date_administered: '',
        next_due_date: '',
        certificate_url: '',
      });
    }
  };

  // Remove vaccination from list
  const removeVaccination = (index) => {
    setFormData((prev) => ({
      ...prev,
      vaccinations: prev.vaccinations.filter((_, i) => i !== index),
    }));
  };

  // Submit handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Build final data
    const finalData = {
      ...formData,
      image_url: uploadedImages[0] || '',
      images: uploadedImages.join(','),
      age_months: parseInt(formData.age_months) || 0,
      weight: parseFloat(formData.weight) || 0,
      price: parseFloat(formData.price) || 0,
    };
    
    try {
      const result = await dispatch(createLivestock(finalData));
      
      if (createLivestock.fulfilled.match(result)) {
        toast.success('Livestock listed successfully!');
        navigate('/farmer/dashboard');
      } else {
        toast.error(result.payload || 'Failed to create listing');
      }
    } catch (err) {
      toast.error('An error occurred');
      console.error(err);
    }
  };

  // Navigation between steps
  const nextStep = () => setCurrentStep((prev) => prev + 1);
  const prevStep = () => setCurrentStep((prev) => prev - 1);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Add New Livestock</h1>
      
      {/* Progress Indicator */}
      <div className="flex items-center justify-between mb-8">
        {[1, 2, 3, 4].map((step) => (
          <div
            key={step}
            className={`flex items-center ${
              step !== 4 ? 'flex-1' : ''
            }`}
          >
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                currentStep >= step
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {step}
            </div>
            {step !== 4 && (
              <div
                className={`flex-1 h-1 mx-2 ${
                  currentStep > step ? 'bg-green-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Step 1: Basic Info */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Animal Type *</label>
                <select
                  name="animal_type"
                  value={formData.animal_type}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  required
                >
                  <option value="">Select type</option>
                  <option value="Cow">Cow</option>
                  <option value="Goat">Goat</option>
                  <option value="Sheep">Sheep</option>
                  <option value="Pig">Pig</option>
                  <option value="Chicken">Chicken</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Breed</label>
                <input
                  type="text"
                  name="breed"
                  value={formData.breed}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  placeholder="e.g., Friesian"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                >
                  <option value="">Select</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Age (months)</label>
                <input
                  type="number"
                  name="age_months"
                  value={formData.age_months}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  min="0"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Weight (kg) *</label>
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  min="0"
                  step="0.1"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Price (KES) *</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  min="0"
                  required
                />
              </div>
              
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Location *</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleBasicChange}
                  className="w-full p-2 border rounded"
                  placeholder="e.g., Nairobi, Kenya"
                  required
                />
              </div>
            </div>
            
            <button
              type="button"
              onClick={nextStep}
              className="bg-green-600 text-white px-6 py-2 rounded mt-4"
            >
              Next
            </button>
          </div>
        )}

        {/* Step 2: Health Records */}
        {currentStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Health Records (Vaccinations)</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Vaccine Name</label>
                <input
                  type="text"
                  value={vaccination.name}
                  onChange={(e) =>
                    setVaccination((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full p-2 border rounded"
                  placeholder="e.g., Foot and Mouth"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Date Administered</label>
                <input
                  type="date"
                  value={vaccination.date_administered}
                  onChange={(e) =>
                    setVaccination((prev) => ({
                      ...prev,
                      date_administered: e.target.value,
                    }))
                  }
                  className="w-full p-2 border rounded"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Next Due Date</label>
                <input
                  type="date"
                  value={vaccination.next_due_date}
                  onChange={(e) =>
                    setVaccination((prev) => ({
                      ...prev,
                      next_due_date: e.target.value,
                    }))
                  }
                  className="w-full p-2 border rounded"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={addVaccination}
                  className="bg-blue-600 text-white px-4 py-2 rounded"
                >
                  Add Vaccination
                </button>
              </div>
            </div>
            
            {/* Vaccination List */}
            {formData.vaccinations.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Added Vaccinations:</h3>
                <ul className="space-y-2">
                  {formData.vaccinations.map((vax, index) => (
                    <li
                      key={index}
                      className="flex justify-between items-center bg-gray-100 p-2 rounded"
                    >
                      <span>
                        {vax.name} - {vax.date_administered}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeVaccination(index)}
                        className="text-red-600"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="flex gap-4 mt-4">
              <button
                type="button"
                onClick={prevStep}
                className="bg-gray-500 text-white px-6 py-2 rounded"
              >
                Back
              </button>
              <button
                type="button"
                onClick={nextStep}
                className="bg-green-600 text-white px-6 py-2 rounded"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Photos */}
        {currentStep === 3 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Photos</h2>
            
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer ${
                isDragActive ? 'border-green-600 bg-green-50' : 'border-gray-300'
              }`}
            >
              <input {...getInputProps()} />
              {isDragActive ? (
                <p className="text-green-600">Drop the files here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Drag & drop photos here, or click to select
                  </p>
                  <p className="text-sm text-gray-500">
                    Max 5MB per image (JPEG, PNG, GIF)
                  </p>
                </div>
              )}
            </div>
            
            {uploading && (
              <p className="text-blue-600">Uploading images...</p>
            )}
            
            {/* Uploaded Images Preview */}
            {uploadedImages.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Uploaded Photos:</h3>
                <div className="grid grid-cols-4 gap-2">
                  {uploadedImages.map((url, index) => (
                    <div key={index} className="relative">
                      <img
                        src={url}
                        alt={`Upload ${index + 1}`}
                        className="w-full h-24 object-cover rounded"
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex gap-4 mt-4">
              <button
                type="button"
                onClick={prevStep}
                className="bg-gray-500 text-white px-6 py-2 rounded"
              >
                Back
              </button>
              <button
                type="button"
                onClick={nextStep}
                className="bg-green-600 text-white px-6 py-2 rounded"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Description & Submit */}
        {currentStep === 4 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Description & Details</h2>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleBasicChange}
                className="w-full p-2 border rounded h-32"
                placeholder="Describe your animal..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Reason for Sale</label>
              <select
                name="reason_for_sale"
                value={formData.reason_for_sale}
                onChange={handleBasicChange}
                className="w-full p-2 border rounded"
              >
                <option value="">Select reason</option>
                <option value="Breeding">Breeding</option>
                <option value="Slaughter">Slaughter</option>
                <option value="Dairy">Dairy</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                name="health_certified"
                checked={formData.health_certified}
                onChange={handleBasicChange}
                id="health_certified"
              />
              <label htmlFor="health_certified">Health Certified</label>
            </div>
            
            {/* Summary */}
            <div className="bg-gray-100 p-4 rounded mt-4">
              <h3 className="font-medium mb-2">Summary:</h3>
              <p>Animal: {formData.animal_type || 'Not specified'}</p>
              <p>Price: KES {formData.price || 0}</p>
              <p>Photos: {uploadedImages.length}</p>
              <p>Vaccinations: {formData.vaccinations.length}</p>
            </div>
            
            {error && (
              <p className="text-red-600">Error: {error}</p>
            )}
            
            <div className="flex gap-4 mt-4">
              <button
                type="button"
                onClick={prevStep}
                className="bg-gray-500 text-white px-6 py-2 rounded"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading || uploading}
                className="bg-green-600 text-white px-6 py-2 rounded disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Submit Listing'}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default AddLivestock;
