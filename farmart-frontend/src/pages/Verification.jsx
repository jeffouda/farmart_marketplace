import { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';

const Verification = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [documents, setDocuments] = useState({
    idDocument: null,
    farmCertificate: null,
    veterinaryCert: null
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setDocuments({ ...documents, [e.target.name]: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');

    // Simulate API call
    setTimeout(() => {
      setSubmitting(false);
      setMessage('Verification documents submitted successfully! We will review within 2-3 business days.');
    }, 2000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Farmer Verification</h1>
      
      {user?.is_verified ? (
        <div className="bg-green-100 text-green-700 p-4 rounded-lg">
          ✓ Your account is verified
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="mb-4">
            Complete the verification process to start selling livestock on FarmAT.
          </p>

          {message && (
            <div className="bg-blue-100 text-blue-700 p-3 rounded mb-4">
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                National ID / Passport
              </label>
              <input
                type="file"
                name="idDocument"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Farm Registration Certificate
              </label>
              <input
                type="file"
                name="farmCertificate"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Veterinary Certificate (if applicable)
              </label>
              <input
                type="file"
                name="veterinaryCert"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="bg-green-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
            >
              {submitting ? 'Submitting...' : 'Submit for Verification'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Verification;
