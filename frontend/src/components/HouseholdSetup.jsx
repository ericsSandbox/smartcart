import { useState } from 'react';
import apiService from '../services/apiService';

export function HouseholdSetup({ onHouseholdCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    budget: ''
  });
  const [status, setStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
  const household = await apiService.createHousehold(formData);
      console.log('Household created:', household);
      setStatus({ type: 'success', message: 'Household created' });
      if (onHouseholdCreated) onHouseholdCreated(household);
    } catch (error) {
      console.error('Error creating household:', error);
      setStatus({ type: 'error', message: error.message || 'Failed to create household' });
    }
  };

  // Members are managed after household creation on the Members tab

  return (
    <div className="max-w-lg mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create Your Household</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {status && (
          <div className={`p-2 rounded ${status.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {status.message}
          </div>
        )}
        <div>
          <label className="block mb-1">Household Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        
        <div>
          <label className="block mb-1">Monthly Budget</label>
          <input
            type="number"
            value={formData.budget}
            onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
            className="w-full p-2 border rounded"
            required
          />
        </div>

        {/* Members are managed after creation, on the Members tab */}

        <button
          type="submit"
          className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Create Household
        </button>
      </form>
    </div>
  );
}