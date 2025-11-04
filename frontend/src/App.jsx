import { useState, useEffect } from 'react'
import './App.css'
import apiService from './services/apiService'
import { HouseholdSetup } from './components/HouseholdSetup'
import { ShoppingList } from './components/ShoppingList'
import { PantryInventory } from './components/PantryInventory'
import { MembersManager } from './components/MembersManager'
import AdCirculars from './components/AdCirculars'

function App() {
  const [currentHousehold, setCurrentHousehold] = useState(null);
  const [activeTab, setActiveTab] = useState('shopping');
  const [loadingHousehold, setLoadingHousehold] = useState(false);
  const [highlightMemberId, setHighlightMemberId] = useState(null);

  const handleNavigateToMember = (memberId) => {
    setHighlightMemberId(memberId);
    setActiveTab('household');
    // Clear highlight after 5 seconds
    setTimeout(() => setHighlightMemberId(null), 5000);
  };

  useEffect(() => {
    apiService.setup();
    // Load household from localStorage on mount
    let savedHouseholdId = localStorage.getItem('householdId');
    
    // If no household is saved, try loading the first one (default to 1)
    if (!savedHouseholdId) {
      savedHouseholdId = '1';
    }
    
    if (savedHouseholdId) {
      setLoadingHousehold(true);
      apiService.getHousehold(parseInt(savedHouseholdId))
        .then(household => {
          console.log('Loaded household from localStorage:', household);
          localStorage.setItem('householdId', household.id); // Ensure it's saved
          setCurrentHousehold(household);
        })
        .catch((err) => {
          console.warn('Failed to load household from localStorage:', err);
          localStorage.removeItem('householdId');
        })
        .finally(() => setLoadingHousehold(false));
    }
  }, []);

  const handleHouseholdCreated = (household) => {
    // fetch fresh household from backend to ensure related members and fields are populated
    (async () => {
      try {
        const fresh = await apiService.getHousehold(household.id);
        localStorage.setItem('householdId', fresh.id);
        setCurrentHousehold(fresh);
      } catch (e) {
        // fallback to passed payload
        localStorage.setItem('householdId', household.id);
        setCurrentHousehold(household);
      }
      setActiveTab('shopping');
    })();
  };

  if (loadingHousehold) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading household...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-900">SmartCart</h1>
          {currentHousehold && (
            <nav className="mt-4">
              <ul className="flex space-x-4">
                <li>
                  <button
                    onClick={() => setActiveTab('shopping')}
                    className={`px-3 py-2 rounded-md ${
                      activeTab === 'shopping'
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Shopping Lists
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => setActiveTab('pantry')}
                    className={`px-3 py-2 rounded-md ${
                      activeTab === 'pantry'
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Pantry
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => setActiveTab('household')}
                    className={`px-3 py-2 rounded-md ${
                      activeTab === 'household'
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Household
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => setActiveTab('circulars')}
                    className={`px-3 py-2 rounded-md ${
                      activeTab === 'circulars'
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Ad Circulars
                  </button>
                </li>
              </ul>
            </nav>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!currentHousehold ? (
          <HouseholdSetup onHouseholdCreated={handleHouseholdCreated} />
        ) : (
          <>
            {activeTab === 'shopping' && (
              <ShoppingList householdId={currentHousehold.id} />
            )}
            {activeTab === 'pantry' && (
              <PantryInventory 
                householdId={currentHousehold.id}
                onNavigateToMember={handleNavigateToMember}
              />
            )}
            {activeTab === 'household' && (
              <div className="max-w-4xl mx-auto">
                <h2 className="text-2xl font-bold mb-6">Household & Members</h2>
                
                {/* Household Info Section */}
                <div className="bg-white shadow rounded-lg p-6 mb-6">
                  <h3 className="text-xl font-bold mb-4">Household Details</h3>
                  <div className="space-y-2">
                    <p><span className="font-semibold">Name:</span> {currentHousehold.name}</p>
                    <p><span className="font-semibold">Budget:</span> ${currentHousehold.monthly_budget ?? currentHousehold.budget ?? 'Not set'}</p>
                  </div>
                </div>

                {/* Members Section */}
                <MembersManager 
                  householdId={currentHousehold.id}
                  highlightMemberId={highlightMemberId}
                />
              </div>
            )}
            {activeTab === 'circulars' && (
              <div className="max-w-4xl mx-auto">
                <AdCirculars householdId={currentHousehold.id} />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App