import { useSelector } from 'react-redux';
import { User } from 'lucide-react';

const UserAvatarHandler = ({ size = "h-10 w-10" }) => {
  const { user } = useSelector((state) => state.auth);
  
  // Try multiple paths for profile image
  const profileImage = 
    user?.profile_image_url || 
    user?.profile?.profile_image_url || 
    user?.profileImageUrl;
  
  if (profileImage) {
    return (
      <img 
        src={profileImage} 
        alt={`${user?.first_name || 'User'}'s profile`}
        className={`${size} rounded-full object-cover border-2 border-green-500 hover:border-green-600 transition-colors`}
        onError={(e) => {
          // Fallback to default avatar on error
          e.target.onerror = null;
          e.target.parentNode.innerHTML = `<div class="${size} rounded-full bg-green-100 flex items-center justify-center border-2 border-green-500"><svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg></div>`;
        }}
      />
    );
  }
  
  // Default avatar with initials if available
  const initials = user?.first_name && user?.last_name 
    ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
    : null;
  
  return (
    <div className={`${size} rounded-full bg-green-100 flex items-center justify-center border-2 border-green-500`}>
      {initials ? (
        <span className="text-green-700 font-semibold text-sm">
          {initials}
        </span>
      ) : (
        <User className="w-5 h-5 text-green-600" />
      )}
    </div>
  );
};

export default UserAvatarHandler;
