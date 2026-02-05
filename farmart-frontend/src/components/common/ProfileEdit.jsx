import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updateProfile } from '../../features/auth/authSlice';
import Loader from './Loader';
import { User, Mail, Phone, MapPin, Award } from 'lucide-react';

const ProfileEdit = ({ onClose }) => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.auth);
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    location: '',
    bio: '',
    farm_name: '',
    farm_location: '',
    specialization: '',
  });
  
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || user.profile?.phone_number || '',
        location: user.location || user.profile?.location || '',
        bio: user.bio || user.profile?.bio || '',
        farm_name: user.farm_name || user.profile?.farm_name || '',
        farm_location: user.farm_location || user.profile?.farm_location || '',
        specialization: user.specialization || user.profile?.specialization || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
    setSuccess(false);
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (formData.phone_number && !/^\+?[\d\s-]{10,}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Invalid phone number format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      await dispatch(updateProfile(formData)).unwrap();
      setSuccess(true);
      if (onClose) {
        setTimeout(() => {
          onClose();
        }, 1500);
      }
    } catch (err) {
      console.error('Failed to update profile:', err);
    }
  };

  const inputFields = [
    { name: 'first_name', label: 'First Name', icon: User, type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', icon: User, type: 'text', required: true },
    { name: 'email', label: 'Email', icon: Mail, type: 'email', required: true },
    { name: 'phone_number', label: 'Phone Number', icon: Phone, type: 'tel' },
    { name: 'location', label: 'Location', icon: MapPin, type: 'text' },
    { name: 'bio', label: 'Bio', type: 'textarea', rows: 3 },
    // Farmer-specific fields
    ...(user?.role === 'farmer' || user?.role === 'admin' ? [
      { name: 'farm_name', label: 'Farm Name', icon: Award, type: 'text' },
      { name: 'farm_location', label: 'Farm Location', icon: MapPin, type: 'text' },
      { name: 'specialization', label: 'Specialization', type: 'text' },
    ] : []),
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          Profile updated successfully!
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {inputFields.map((field) => (
          <div 
            key={field.name} 
            className={field.type === 'textarea' ? 'md:col-span-2' : ''}
          >
            <label 
              htmlFor={field.name} 
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            <div className="relative">
              {field.icon && (
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <field.icon className="h-5 w-5 text-gray-400" />
                </div>
              )}
              
              {field.type === 'textarea' ? (
                <textarea
                  id={field.name}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleChange}
                  rows={field.rows || 4}
                  className={`block w-full ${field.icon ? 'pl-10' : 'pl-3'} pr-3 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500 ${
                    errors[field.name] ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder={`Enter ${field.label.toLowerCase()}`}
                />
              ) : (
                <input
                  type={field.type}
                  id={field.name}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleChange}
                  className={`block w-full ${field.icon ? 'pl-10' : 'pl-3'} pr-3 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500 ${
                    errors[field.name] ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder={`Enter ${field.label.toLowerCase()}`}
                />
              )}
            </div>
            
            {errors[field.name] && (
              <p className="mt-1 text-sm text-red-500">{errors[field.name]}</p>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader size="small" color="white" />
              Saving...
            </>
          ) : (
            'Save Changes'
          )}
        </button>
      </div>
    </form>
  );
};

export default ProfileEdit;
