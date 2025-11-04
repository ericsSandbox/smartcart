import { useState, useEffect } from 'react';
import apiService from '../services/apiService';

export function PantryInventory({ householdId, onNavigateToMember }) {
  const [items, setItems] = useState([]);
  const [lists, setLists] = useState([]);
  const [members, setMembers] = useState([]);
  const [zeroItemModal, setZeroItemModal] = useState(null); // { item, prevQuantity }
  const [selectedListId, setSelectedListId] = useState(null);
  const [newItem, setNewItem] = useState({
    name: '',
    quantity: 1,
    unit: 'unit',
    expires_at: '',
    staple: false
  });

  useEffect(() => {
    loadPantryItems();
    loadShoppingLists();
    loadMembers();
  }, [householdId]);

  const loadPantryItems = async () => {
    try {
      const data = await apiService.getPantryItems(householdId);
      setItems(data);
    } catch (error) {
      console.error('Error loading pantry items:', error);
    }
  };

  const loadShoppingLists = async () => {
    try {
      const data = await apiService.getShoppingLists(householdId);
      setLists(data);
    } catch (error) {
      console.error('Error loading shopping lists:', error);
    }
  };

  const loadMembers = async () => {
    try {
      const data = await apiService.listMembers(householdId);
      setMembers(data);
    } catch (error) {
      console.error('Error loading members:', error);
    }
  };

  // Check if an ingredient conflicts with any member's restrictions
  const checkItemConflicts = (itemName) => {
    const conflicts = [];
    const itemLower = itemName.toLowerCase();
    
    for (const member of members) {
      // Check allergies
      if (member.allergies) {
        const allergies = member.allergies.toLowerCase().split(',').map(a => a.trim());
        if (allergies.some(a => itemLower.includes(a) || a.includes(itemLower))) {
          conflicts.push({ member, type: 'allergy' });
          continue;
        }
      }
      
      // Check dietary preferences
      if (member.dietary_pref) {
        const diets = member.dietary_pref.toLowerCase().split(',').map(d => d.trim());
        // Simple checks for common conflicts
        if (diets.includes('vegan') && (itemLower.includes('milk') || itemLower.includes('cheese') || itemLower.includes('butter') || itemLower.includes('egg') || itemLower.includes('meat') || itemLower.includes('chicken') || itemLower.includes('beef') || itemLower.includes('pork') || itemLower.includes('fish'))) {
          conflicts.push({ member, type: 'dietary' });
          continue;
        }
        if (diets.includes('vegetarian') && (itemLower.includes('meat') || itemLower.includes('chicken') || itemLower.includes('beef') || itemLower.includes('pork') || itemLower.includes('fish'))) {
          conflicts.push({ member, type: 'dietary' });
          continue;
        }
      }
      
      // Check dislikes
      if (member.dislikes) {
        const dislikes = member.dislikes.toLowerCase().split(',').map(d => d.trim());
        if (dislikes.some(d => itemLower.includes(d) || d.includes(itemLower))) {
          conflicts.push({ member, type: 'dislike' });
        }
      }
    }
    
    return conflicts;
  };

  const addItem = async (e) => {
    e.preventDefault();
    try {
      // Transform data for backend: convert empty expires_at to null, ensure quantity is a number
      const itemData = {
        ...newItem,
        quantity: parseFloat(newItem.quantity),
        expires_at: newItem.expires_at ? newItem.expires_at : null
      };
      await apiService.addPantryItem(householdId, itemData);
      setNewItem({ name: '', quantity: 1, unit: 'unit', expires_at: '', staple: false });
      loadPantryItems();
    } catch (error) {
      console.error('Error adding pantry item:', error);
    }
  };

  const getExpiryStatus = (expiryDate) => {
    if (!expiryDate) return 'none';
    const days = Math.ceil((new Date(expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'expired';
    if (days < 7) return 'soon';
    return 'good';
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Pantry Inventory</h2>
      
      <form onSubmit={addItem} className="mb-6">
        <div className="flex gap-2 mb-4 items-center">
          <input
            type="text"
            value={newItem.name}
            onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
            placeholder="Item name"
            className="flex-1 p-2 border rounded"
            required
          />
          <input
            type="number"
            value={newItem.quantity}
            onChange={(e) => setNewItem({ ...newItem, quantity: e.target.value })}
            className="w-20 p-2 border rounded"
            min="0"
            required
          />
          <select
            value={newItem.unit}
            onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
            className="p-2 border rounded"
          >
            <option value="unit">unit</option>
            <option value="lb">lb</option>
            <option value="oz">oz</option>
            <option value="gal">gal</option>
            <option value="qt">qt</option>
            <option value="pt">pt</option>
            <option value="cup">cup</option>
            <option value="tbsp">tbsp</option>
            <option value="tsp">tsp</option>
            <option value="kg">kg</option>
            <option value="g">g</option>
            <option value="l">l</option>
            <option value="ml">ml</option>
          </select>
          <input
            type="date"
            value={newItem.expires_at}
            onChange={(e) => setNewItem({ ...newItem, expires_at: e.target.value })}
            className="p-2 border rounded"
          />
          <label className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={!!newItem.staple}
              onChange={e => setNewItem({ ...newItem, staple: e.target.checked })}
            />
            <span className="text-sm">Staple</span>
          </label>
          <button
            type="submit"
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Add Item
          </button>
        </div>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map(item => {
          const expiryStatus = getExpiryStatus(item.expires_at);
          const conflicts = checkItemConflicts(item.name);
          
          return (
            <div
              key={item.id}
              className={`p-4 rounded-lg border ${
                expiryStatus === 'expired' ? 'bg-red-50 border-red-200' :
                expiryStatus === 'soon' ? 'bg-yellow-50 border-yellow-200' :
                'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold">{item.name}</h3>
                    {item.staple && <span className="px-2 py-1 bg-yellow-200 text-xs rounded">Staple</span>}
                    {conflicts.map((conflict, idx) => (
                      <button
                        key={idx}
                        onClick={() => onNavigateToMember && onNavigateToMember(conflict.member.id)}
                        className={`px-2 py-1 text-xs font-bold rounded cursor-pointer hover:opacity-80 ${
                          conflict.type === 'allergy' ? 'bg-red-600 text-white' :
                          conflict.type === 'dietary' ? 'bg-orange-500 text-white' :
                          'bg-red-400 text-white'
                        }`}
                        title={`${conflict.member.name} - ${conflict.type}`}
                      >
                        {conflict.member.name.charAt(0).toUpperCase()}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      className="w-24 p-1 border rounded"
                      value={item.quantity}
                      onChange={(e) => {
                        const val = e.target.value;
                        setItems(prev => prev.map(it => it.id === item.id ? { ...it, quantity: val } : it));
                      }}
                      onBlur={async (e) => {
                        const qty = parseFloat(e.target.value);
                        if (isNaN(qty)) return;
                        
                        // If quantity is zero or negative
                        if (qty <= 0) {
                          // Staple items auto-add to shopping list, no modal
                          if (item.staple) {
                            try {
                              await apiService.updatePantryItem(householdId, item.id, { quantity: qty });
                              loadPantryItems();
                              // Backend will auto-add to Staples list
                            } catch (err) {
                              console.error('Failed to update quantity', err);
                            }
                            return;
                          }
                          
                          // Non-staple items show modal
                          setZeroItemModal({ item, prevQuantity: item.quantity });
                          return;
                        }
                        
                        try {
                          await apiService.updatePantryItem(householdId, item.id, { quantity: qty });
                          loadPantryItems();
                        } catch (err) {
                          console.error('Failed to update quantity', err);
                        }
                      }}
                    />
                    <span className="text-sm text-gray-600">{item.unit}</span>
                  </div>
                </div>
                {item.expires_at && (
                  <div className="text-sm text-gray-500">
                    Expires: {new Date(item.expires_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Zero Quantity Modal */}
      {zeroItemModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">"{zeroItemModal.item.name}" is at zero</h3>
            <p className="text-gray-600 mb-4">What would you like to do?</p>
            
            <div className="space-y-3">
              {/* Forget Item */}
              <button
                onClick={async () => {
                  try {
                    await apiService.deletePantryItem(householdId, zeroItemModal.item.id);
                    setZeroItemModal(null);
                    loadPantryItems();
                  } catch (err) {
                    console.error('Failed to delete item', err);
                  }
                }}
                className="w-full px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Forget this item
              </button>

              {/* Add to Shopping List */}
              <div className="border-t pt-3">
                <label className="block text-sm font-semibold mb-2">Add to Shopping List:</label>
                <select
                  value={selectedListId || ''}
                  onChange={(e) => setSelectedListId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full p-2 border rounded mb-2"
                >
                  <option value="">-- Select a list --</option>
                  {lists.map(list => (
                    <option key={list.id} value={list.id}>{list.name}</option>
                  ))}
                </select>
                <button
                  onClick={async () => {
                    if (!selectedListId) {
                      alert('Please select a shopping list');
                      return;
                    }
                    try {
                      await apiService.addItemToList(selectedListId, {
                        name: zeroItemModal.item.name,
                        quantity: 1,
                        unit: zeroItemModal.item.unit
                      });
                      // Keep item in pantry at zero
                      await apiService.updatePantryItem(householdId, zeroItemModal.item.id, { quantity: 0 });
                      setZeroItemModal(null);
                      setSelectedListId(null);
                      loadPantryItems();
                    } catch (err) {
                      console.error('Failed to add to shopping list', err);
                    }
                  }}
                  className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Add to List
                </button>
              </div>

              {/* Cancel */}
              <button
                onClick={() => {
                  // Restore previous quantity
                  setItems(prev => prev.map(it => 
                    it.id === zeroItemModal.item.id 
                      ? { ...it, quantity: zeroItemModal.prevQuantity } 
                      : it
                  ));
                  setZeroItemModal(null);
                  setSelectedListId(null);
                }}
                className="w-full px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}