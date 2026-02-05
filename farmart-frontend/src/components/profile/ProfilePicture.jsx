import { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Upload, X, User, CheckCircle } from 'lucide-react';
import { updateProfile } from '../../features/auth/authSlice';
import { toast } from 'react-toastify';
import Loader from '../common/Loader';

const ProfilePicture = ({ user: propUser, size = "h-32 w-32", editable = true }) => {
  const dispatch = useDispatch();
  const { user: reduxUser, isLoading } = useSelector((state) => state.auth);
  const user = propUser || reduxUser;
  
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [sessionRefreshing, setSessionRefreshing] = useState(false);
  const fileInputRef = useRef(null);

  const profileImage = user?.profile_image_url || 
    user?.profile?.profile_image_url || 
    user?.profileImageUrl;

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
        setShowModal(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!previewUrl) return;
    
    setIsUploading(true);
    setUploadSuccess(false);
    setSessionRefreshing(false);
    
    try {
      // Convert base64 to blob for upload
      const response = await fetch(previewUrl);
      const blob = await response.blob();
      const file = new File([blob], 'profile-picture.jpg', { type: 'image/jpeg' });
      
      await dispatch(updateProfile({ image: file })).unwrap();
      
      // Show success checkmark
      setUploadSuccess(true);
      setTimeout(() => {
        setShowModal(false);
        setPreviewUrl(null);
        setUploadSuccess(false);
      }, 1500);
      
    } catch (error) {
      console.error('Failed to upload profile picture:', error);
      
      // Mercy Logic: Check for 401 session expired
      if (error.includes('Session expired') || error.includes('401')) {
        setSessionRefreshing(true);
        toast.info('Session expired. Refreshing... Please try again.', {
          position: "top-right",
          autoClose: 3000,
          theme: "colored",
        });
        
        // Auto-retry after session refresh
        setTimeout(async () => {
          setSessionRefreshing(false);
          try {
            await dispatch(updateProfile({ image: file })).unwrap();
            setUploadSuccess(true);
            setTimeout(() => {
              setShowModal(false);
              setPreviewUrl(null);
              setUploadSuccess(false);
            }, 1500);
          } catch (retryError) {
            toast.error('Upload failed after session refresh. Please try again.', {
              position: "top-right",
              autoClose: 3000,
              theme: "colored",
            });
          }
        }, 2000);
      } else {
        toast.error(error || 'Failed to upload profile picture', {
          position: "top-right",
          autoClose: 3000,
          theme: "colored",
        });
      }
    } finally {
      if (!sessionRefreshing) {
        setIsUploading(false);
      }
    }
  };

  const handleRemove = async () => {
    setIsUploading(true);
    try {
      await dispatch(updateProfile({ profile_image_url: null })).unwrap();
      setShowModal(false);
      setPreviewUrl(null);
    } catch (error) {
      console.error('Failed to remove profile picture:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const cancelPreview = () => {
    setPreviewUrl(null);
    setShowModal(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        {/* Current Profile Picture */}
        <div className={`${size} rounded-full overflow-hidden ring-4 ring-green-100`}>
          {profileImage ? (
            <img 
              src={profileImage} 
              alt={`${user?.first_name || 'User'}'s profile`}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-green-100 flex items-center justify-center">
              <User className="w-1/2 h-1/2 text-green-600" />
            </div>
          )}
        </div>

        {/* Edit Button */}
        {editable && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="absolute bottom-0 right-0 bg-green-600 text-white p-2 rounded-full hover:bg-green-700 transition-colors shadow-lg"
            title="Change profile picture"
          >
            <Upload className="w-4 h-4" />
          </button>
        )}

        {/* Loading/Success Overlay */}
        {(isLoading || isUploading || uploadSuccess) && (
          <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center">
            {uploadSuccess ? (
              <CheckCircle className="w-8 h-8 text-green-400" />
            ) : sessionRefreshing ? (
              <div className="text-center">
                <Loader size="small" color="white" />
                <p className="text-white text-xs mt-1">Refreshing...</p>
              </div>
            ) : (
              <Loader size="small" color="white" />
            )}
          </div>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Preview Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Profile Picture</h3>
              <button
                onClick={cancelPreview}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Preview Image */}
            <div className="flex justify-center mb-6">
              <div className={`${size} rounded-full overflow-hidden`}>
                {previewUrl ? (
                  <img 
                    src={previewUrl} 
                    alt="Preview" 
                    className="w-full h-full object-cover"
                  />
                ) : profileImage ? (
                  <img 
                    src={profileImage} 
                    alt="Current" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-green-100 flex items-center justify-center">
                    <User className="w-1/2 h-1/2 text-green-600" />
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              {previewUrl ? (
                <>
                  <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isUploading ? (
                      <Loader size="small" color="white" />
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Upload
                      </>
                    )}
                  </button>
                  <button
                    onClick={cancelPreview}
                    disabled={isUploading}
                    className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                </>
              ) : profileImage ? (
                <>
                  <button
                    onClick={handleRemove}
                    disabled={isUploading}
                    className="flex-1 bg-red-100 text-red-700 py-2 px-4 rounded-lg hover:bg-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Remove
                  </button>
                  <button
                    onClick={cancelPreview}
                    className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePicture;
