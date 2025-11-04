import React, { useEffect, useState } from 'react';
import apiService from '../services/apiService';

export default function AdCirculars({ householdId }) {
  const [items, setItems] = useState([]);
  const [retailers, setRetailers] = useState([]);
  const [selectedRetailer, setSelectedRetailer] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [summary, setSummary] = useState(null);
  
  // Shopping list state
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [shoppingLists, setShoppingLists] = useState([]);
  const [newListName, setNewListName] = useState('');
  const [addingToList, setAddingToList] = useState(false);
  
  // Collapsible state
  const [expandedCategories, setExpandedCategories] = useState({});

  useEffect(() => {
    loadCircularData();
    if (householdId) {
      loadShoppingLists();
    }
  }, [householdId]);

  const API_BASE = 'http://localhost:8000';

  const loadShoppingLists = async () => {
    try {
      const data = await apiService.getShoppingLists(householdId);
      setShoppingLists(data);
    } catch (err) {
      console.error('Failed to load shopping lists:', err);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Clean/sanitize product names for shopping lists
  const sanitizeProductName = (name) => {
    if (!name) return '';
    
    // Remove common size/weight indicators that are redundant in shopping lists
    let cleaned = name
      .replace(/\s*\(.*?lbs?\b.*?\)/gi, '')           // (X lbs), (X lb)
      .replace(/\s*\(.*?ounces?\b.*?\)/gi, '')        // (X oz)
      .replace(/\s*\(.*?pounds?\b.*?\)/gi, '')        // (X pounds)
      .replace(/\s*\(.*?pack\b.*?\)/gi, '')           // (X pack)
      .replace(/\s*\(.*?\d+\s*count\b.*?\)/gi, '')    // (12 count)
      .replace(/\s*Maxx?\s*Pack\b/gi, '')             // Maxx Pack / Max Pack
      .replace(/\s*or\s+.*$/i, '')                    // Remove "or alternative" options
      .replace(/\s+/g, ' ')                           // Normalize spaces
      .trim();
    
    return cleaned;
  };

  const handleAddToList = (item) => {
    setSelectedItem(item);
    setShowAddModal(true);
  };

  const addItemToNewList = async () => {
    if (!newListName.trim()) {
      alert('Please enter a list name');
      return;
    }

    try {
      setAddingToList(true);
      
      // Create new list
      const newList = await apiService.createShoppingList(householdId, { name: newListName });
      
      // Add item to new list with sanitized name
      const cleanedName = sanitizeProductName(selectedItem.item_name);
      const payload = {
        name: cleanedName,
        quantity: 1,
        unit: selectedItem.unit || 'unit',
      };
      await apiService.addItemToList(newList.id, payload);
      
      // Reset and close modal
      setNewListName('');
      setSelectedItem(null);
      setShowAddModal(false);
      
      // Reload shopping lists
      await loadShoppingLists();
      
      alert(`Added "${cleanedName}" to new list "${newListName}"`);
    } catch (err) {
      console.error('Failed to create list and add item:', err);
      alert('Failed to create list and add item');
    } finally {
      setAddingToList(false);
    }
  };

  const addItemToExistingList = async (listId) => {
    try {
      setAddingToList(true);
      
      const cleanedName = sanitizeProductName(selectedItem.item_name);
      const payload = {
        name: cleanedName,
        quantity: 1,
        unit: selectedItem.unit || 'unit',
      };
      await apiService.addItemToList(listId, payload);
      
      // Reset and close modal
      setSelectedItem(null);
      setShowAddModal(false);
      
      // Reload shopping lists
      await loadShoppingLists();
      
      const list = shoppingLists.find(l => l.id === listId);
      alert(`Added "${cleanedName}" to "${list?.name}"`);
    } catch (err) {
      console.error('Failed to add item to list:', err);
      alert('Failed to add item to list');
    } finally {
      setAddingToList(false);
    }
  };

  const loadCircularData = async () => {
    try {
      setLoading(true);
      setError(null);

      const summaryRes = await fetch(`${API_BASE}/api/circulars/summary`);
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      const retailersRes = await fetch(`${API_BASE}/api/circulars/retailers`);
      const retailersData = await retailersRes.json();
      
      if (retailersData.retailers && retailersData.retailers.length > 0) {
        setRetailers(retailersData.retailers);
        const firstRetailer = retailersData.retailers[0];
        setSelectedRetailer(firstRetailer);

        const categoriesRes = await fetch(`${API_BASE}/api/circulars/retailers/${encodeURIComponent(firstRetailer)}/categories`);
        const categoriesData = await categoriesRes.json();
        if (categoriesData.categories) {
          setCategories(categoriesData.categories);
        }

        const itemsRes = await fetch(`${API_BASE}/api/circulars/items?retailer=${encodeURIComponent(firstRetailer)}&limit=1000`);
        const itemsData = await itemsRes.json();
        setItems(Array.isArray(itemsData) ? itemsData : []);
      }
    } catch (err) {
      console.error('Failed to load circular data:', err);
      setError('Failed to load circular data');
    } finally {
      setLoading(false);
    }
  };

  const handleRetailerChange = async (retailer) => {
    setSelectedRetailer(retailer);
    setLoading(true);

    try {
      const categoriesRes = await fetch(`${API_BASE}/api/circulars/retailers/${encodeURIComponent(retailer)}/categories`);
      const categoriesData = await categoriesRes.json();
      if (categoriesData.categories) {
        setCategories(categoriesData.categories);
      }

      const itemsRes = await fetch(`${API_BASE}/api/circulars/items?retailer=${encodeURIComponent(retailer)}&limit=1000`);
      const itemsData = await itemsRes.json();
      setItems(Array.isArray(itemsData) ? itemsData : []);
    } catch (err) {
      console.error('Failed to load retailer data:', err);
      setError(`Failed to load ${retailer} items`);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = searchQuery.length > 0
    ? items.filter(item => item.item_name.toLowerCase().includes(searchQuery.toLowerCase()))
    : items;

  const groupedByCategory = filteredItems.reduce((acc, item) => {
    const category = item.category || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {});

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading circular items...</div>
          <div className="animate-spin inline-block">
            <div className="border-4 border-blue-200 border-t-blue-600 rounded-full w-8 h-8"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {summary && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📋 Weekly Ad Circulars</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded p-4 border border-green-100">
              <div className="text-3xl font-bold text-green-600">{summary.total_items}</div>
              <div className="text-sm text-gray-600 mt-1">Total Items</div>
            </div>
            <div className="bg-white rounded p-4 border border-blue-100">
              <div className="text-3xl font-bold text-blue-600">{summary.retailers}</div>
              <div className="text-sm text-gray-600 mt-1">Retailers</div>
            </div>
            <div className="bg-white rounded p-4 border border-purple-100">
              {Object.entries(summary.items_by_retailer || {}).map(([retailer, count]) => (
                <div key={retailer}>
                  <div className="text-sm font-semibold text-gray-900">{retailer}</div>
                  <div className="text-lg font-bold text-purple-600">{count} items</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {retailers.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Select Retailer</h3>
          <div className="flex flex-wrap gap-2">
            {retailers.map((retailer) => (
              <button
                key={retailer}
                onClick={() => handleRetailerChange(retailer)}
                className={`px-4 py-2 rounded transition font-medium ${
                  selectedRetailer === retailer
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                {retailer}
              </button>
            ))}
          </div>
        </div>
      )}

      {categories.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Available Categories</h3>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <span
                key={category}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {category}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <input
          type="text"
          placeholder="Search items (e.g., 'tri-tip', 'chicken', 'wine')..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
        />
      </div>

      <div className="space-y-4">
        {Object.entries(groupedByCategory).map(([category, categoryItems]) => (
          <div key={category} className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
            <button
              onClick={() => toggleCategory(category)}
              className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition"
            >
              <h3 className="font-semibold text-gray-900 text-lg flex items-center gap-2">
                <span>{expandedCategories[category] ? '▼' : '▶'}</span>
                <span>📁 {category} ({categoryItems.length})</span>
              </h3>
            </button>
            
            {expandedCategories[category] && (
              <div className="space-y-2 p-4">
                {categoryItems.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-start p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded border border-gray-200 hover:border-blue-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 transition cursor-pointer group"
                    onClick={() => handleAddToList(item)}
                  >
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 group-hover:text-blue-700 transition">{item.item_name}</p>
                      <p className="text-xs text-gray-500 mt-1">by {item.retailer}</p>
                    </div>
                    <div className="text-right ml-4 min-w-fit flex flex-col items-end gap-1">
                      {/* Display price or discount */}
                      {item.discount_percent ? (
                        <div className="flex items-center gap-2">
                          <div className="bg-red-600 text-white font-bold px-3 py-1 rounded-lg text-lg transform -skew-x-12">
                            {item.discount_percent.toFixed(0)}% OFF
                          </div>
                          {item.regular_price && (
                            <p className="text-xs text-gray-500 line-through">
                              ${item.regular_price.toFixed(2)}
                            </p>
                          )}
                        </div>
                      ) : item.price ? (
                        <p className="font-bold text-lg text-green-600">
                          ${item.price.toFixed(2)}
                        </p>
                      ) : (
                        <p className="font-bold text-lg text-gray-500">N/A</p>
                      )}
                      {item.unit && <p className="text-xs text-gray-500">per {item.unit}</p>}
                    </div>
                    <div className="ml-3 opacity-0 group-hover:opacity-100 transition">
                      <span className="text-blue-600 font-semibold text-sm">+ Add</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {filteredItems.length === 0 && (
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
            <p className="text-gray-500">No items found matching your search</p>
          </div>
        )}
      </div>

      {/* Add to Shopping List Modal */}
      {showAddModal && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Add to Shopping List</h2>
            
            <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
              <p className="text-sm font-semibold text-gray-600">Item to add:</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">{selectedItem.item_name}</p>
              <div className="mt-2 flex items-center gap-2">
                {selectedItem.discount_percent ? (
                  <>
                    <span className="bg-red-600 text-white font-bold px-3 py-1 rounded text-sm">
                      {selectedItem.discount_percent.toFixed(0)}% OFF
                    </span>
                    {selectedItem.regular_price && (
                      <span className="text-sm text-gray-600 line-through">
                        was ${selectedItem.regular_price.toFixed(2)}
                      </span>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-green-600 font-semibold">
                    💲 ${selectedItem.price?.toFixed(2)} per {selectedItem.unit}
                  </p>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">From {selectedItem.retailer}</p>
            </div>

            {/* Existing lists */}
            {shoppingLists.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Add to existing list:</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {shoppingLists.map(list => (
                    <button
                      key={list.id}
                      onClick={() => addItemToExistingList(list.id)}
                      disabled={addingToList}
                      className="w-full px-4 py-2 bg-gray-100 hover:bg-blue-100 text-gray-900 rounded border border-gray-200 hover:border-blue-400 transition font-medium disabled:opacity-50"
                    >
                      {list.name} ({list.items?.length || 0} items)
                    </button>
                  ))}
                </div>
                
                <div className="border-t border-gray-200 my-4"></div>
              </div>
            )}

            {/* New list */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Or create new list:</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="List name..."
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && addItemToNewList()}
                />
                <button
                  onClick={addItemToNewList}
                  disabled={addingToList || !newListName.trim()}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium disabled:opacity-50 transition"
                >
                  Create
                </button>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={() => {
                setShowAddModal(false);
                setSelectedItem(null);
                setNewListName('');
              }}
              className="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded font-medium transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
