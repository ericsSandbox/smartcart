import { useState, useEffect } from 'react';
import apiService from '../services/apiService';

// Helper: Extract user notes from stored JSON (separates selected_offer from user notes)
function getUserNotes(itemNotes) {
  if (!itemNotes) return '';
  try {
    const obj = JSON.parse(itemNotes);
    // Return only non-selected_offer properties joined
    const userNotesParts = Object.entries(obj)
      .filter(([key]) => key !== 'selected_offer')
      .map(([, val]) => val);
    return userNotesParts.join(' ');
  } catch {
    // If not JSON, return as-is
    return itemNotes;
  }
}

// Helper: Save user notes without losing selected_offer
function saveNotesWithOffer(itemNotes, newUserNotes) {
  let obj = {};
  try {
    if (itemNotes) obj = JSON.parse(itemNotes);
  } catch {}
  // Preserve selected_offer if it exists
  const selectedOffer = obj.selected_offer;
  obj = { user_notes: newUserNotes || undefined };
  if (selectedOffer) obj.selected_offer = selectedOffer;
  // Return stringified only if there's content
  return Object.keys(obj).some(k => obj[k]) ? JSON.stringify(obj) : null;
}

export function ShoppingList({ householdId }) {
  const [lists, setLists] = useState([]);
  const [newListName, setNewListName] = useState('');
  const [selectedList, setSelectedList] = useState(null);
  const [newItem, setNewItem] = useState({ name: '', quantity: 1, unit: 'unit' });
  const [recipeUrl, setRecipeUrl] = useState('');
  const [recipeModal, setRecipeModal] = useState(null); // { title, servings, missing, conflicts }
  const [servingsAdjust, setServingsAdjust] = useState({ enabled: false, peopleEating: 4 });
  const [excludedIngredients, setExcludedIngredients] = useState(new Set());
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [showSavedRecipes, setShowSavedRecipes] = useState(false);
  // Pricing state
  const [pricingSettings, setPricingSettings] = useState({ pricing_enabled: false, zip_code: '', latitude: null, longitude: null, radius_miles: 5 });
  const [offersByItem, setOffersByItem] = useState({}); // itemId -> { loading, offers, error, expanded }
  
  useEffect(() => {
    loadLists();
    loadSavedRecipes();
    loadPricingSettings();
  }, [householdId]);

  const loadLists = async () => {
    try {
      const data = await apiService.getShoppingLists(householdId);
      setLists(data);
    } catch (error) {
      console.error('Error loading shopping lists:', error);
    }
  };

  const loadSavedRecipes = async () => {
    try {
      const data = await apiService.getSavedRecipes(householdId);
      setSavedRecipes(data);
    } catch (error) {
      console.error('Error loading saved recipes:', error);
    }
  };

  const loadPricingSettings = async () => {
    try {
      const settings = await apiService.getPricingSettings(householdId);
      setPricingSettings(settings);
    } catch (e) {
      console.error('Failed to load pricing settings', e);
    }
  };

  const savePricingSettings = async () => {
    try {
      const payload = {
        household_id: householdId,
        pricing_enabled: !!pricingSettings.pricing_enabled,
        zip_code: pricingSettings.zip_code || null,
        latitude: pricingSettings.latitude || null,
        longitude: pricingSettings.longitude || null,
        radius_miles: Number(pricingSettings.radius_miles) || 5,
      };
      const saved = await apiService.savePricingSettings(payload);
      setPricingSettings(saved);
    } catch (e) {
      console.error('Failed to save pricing settings', e);
      window.alert('Failed to save price comparison settings');
    }
  };

  const toggleOffersForItem = async (item) => {
    const existing = offersByItem[item.id] || {};
    // If already loaded, just toggle expanded
    if (existing.offers && !existing.loading && !existing.error) {
      setOffersByItem({ ...offersByItem, [item.id]: { ...existing, expanded: !existing.expanded } });
      return;
    }
    // Load offers
    setOffersByItem({ ...offersByItem, [item.id]: { loading: true, offers: [], error: null, expanded: true } });
    try {
      const resp = await apiService.getOffers({ household_id: householdId, query: item.name, radius_miles: pricingSettings.radius_miles });
      setOffersByItem({ ...offersByItem, [item.id]: { loading: false, offers: resp.offers || [], normalized_query: resp.normalized_query || null, error: null, expanded: true } });
    } catch (e) {
      console.error('Failed to load offers', e);
      setOffersByItem({ ...offersByItem, [item.id]: { loading: false, offers: [], error: 'Failed to load offers', expanded: true } });
    }
  };

  const selectOfferForItem = async (item, offer) => {
    try {
      // Merge selection into notes as JSON
      let notesObj = {};
      try { if (item.notes) notesObj = JSON.parse(item.notes); } catch {}
      notesObj.selected_offer = {
        provider: offer.provider,
        store: offer.store,
        price: offer.price,
        unit: offer.unit,
        url: offer.url,
        promo_text: offer.promo_text,
        distance_miles: offer.distance_miles,
        status: 'chosen', // future: 'ordered'
      };
      await apiService.updateListItem(item.id, { notes: JSON.stringify(notesObj) });
      await loadLists();
      const updated = (lists || []).find(l => l.id === selectedList.id);
      setSelectedList(updated || null);
      // keep the offers expanded so the chosen card remains visible/highlighted
      setOffersByItem({ ...offersByItem, [item.id]: { ...(offersByItem[item.id] || {}), expanded: true } });
    } catch (e) {
      console.error('Failed to save offer selection', e);
      window.alert('Failed to save offer selection');
    }
  };

  const clearOfferForItem = async (item) => {
    try {
      let notesObj = {};
      try { if (item.notes) notesObj = JSON.parse(item.notes); } catch {}
      if (notesObj.selected_offer) delete notesObj.selected_offer;
      // Keep only user_notes if present
      const newNotesObj = {};
      if (notesObj.user_notes) newNotesObj.user_notes = notesObj.user_notes;
      const newNotes = Object.keys(newNotesObj).length ? JSON.stringify(newNotesObj) : null;
      await apiService.updateListItem(item.id, { notes: newNotes });
      await loadLists();
      const updated = (lists || []).find(l => l.id === selectedList.id);
      setSelectedList(updated || null);
    } catch (e) {
      console.error('Failed to clear offer selection', e);
    }
  };

  const createList = async (e) => {
    e.preventDefault();
    try {
      await apiService.createShoppingList(householdId, { name: newListName });
      setNewListName('');
      loadLists();
    } catch (error) {
      console.error('Error creating shopping list:', error);
    }
  };

  const importRecipe = async (e) => {
    e.preventDefault();
    if (!recipeUrl) return;
    try {
      const result = await apiService.importRecipe(householdId, recipeUrl, false);
      if (result.missing?.length || result.conflicts?.length) {
        // Show modal with conflicts and serving size adjustment
        setRecipeModal({
          title: result.title,
          servings: result.servings || 4,
          missing: result.missing,
          conflicts: result.conflicts || [],
          substitutions: result.substitutions || [],
          url: recipeUrl
        });
        setServingsAdjust({ enabled: false, peopleEating: result.servings || 4 });
        
        // Auto-exclude ingredients with allergy conflicts
        const allergyIngredients = new Set(
          (result.conflicts || [])
            .filter(c => c.conflict_type === 'allergy')
            .map(c => c.ingredient)
        );
        setExcludedIngredients(allergyIngredients);
      } else {
        window.alert(`${result.title}: All ingredients are in your pantry!`);
      }
    } catch (err) {
      console.error('Recipe import failed', err);
      window.alert('Failed to import recipe. Make sure the URL is a supported site.');
    }
  };

  const confirmRecipeImport = async () => {
    const multiplier = servingsAdjust.enabled && recipeModal.servings 
      ? servingsAdjust.peopleEating / recipeModal.servings 
      : 1.0;
    
    try {
      const created = await apiService.importRecipe(
        householdId, 
        recipeModal.url, 
        true, 
        multiplier,
        Array.from(excludedIngredients)
      );
      await loadLists();
      const lst = (created.created_list_id && (await apiService.getShoppingLists(householdId)).find(l => l.id === created.created_list_id)) || null;
      setSelectedList(lst);
      setRecipeModal(null);
      setRecipeUrl('');
      setExcludedIngredients(new Set());
    } catch (err) {
      console.error('Failed to create shopping list', err);
    }
  };

  const saveRecipeFromModal = async () => {
    try {
      await apiService.saveRecipe({
        household_id: householdId,
        title: recipeModal.title,
        url: recipeModal.url,
        servings: recipeModal.servings,
        ingredients: recipeModal.missing
      });
      await loadSavedRecipes();
      window.alert(`Recipe "${recipeModal.title}" saved!`);
    } catch (err) {
      console.error('Failed to save recipe', err);
      window.alert('Failed to save recipe');
    }
  };

  const addSavedRecipeToList = async (recipe) => {
    try {
      const result = await apiService.addSavedRecipeToList({
        recipe_id: recipe.id,
        servings_multiplier: 1.0,
        exclude_ingredients: []
      });
      
      if (result.conflicts?.length) {
        // Show modal with conflicts
        setRecipeModal({
          title: recipe.title,
          servings: recipe.servings || 4,
          missing: recipe.ingredients.map(ing => ing.name),
          conflicts: result.conflicts || [],
          substitutions: result.substitutions || [],
          url: recipe.url,
          savedRecipeId: recipe.id
        });
        setServingsAdjust({ enabled: false, peopleEating: recipe.servings || 4 });
        
        const allergyIngredients = new Set(
          (result.conflicts || [])
            .filter(c => c.conflict_type === 'allergy')
            .map(c => c.ingredient)
        );
        setExcludedIngredients(allergyIngredients);
        setShowSavedRecipes(false);
      } else {
        await loadLists();
        if (result.created_list_id) {
          const lst = lists.find(l => l.id === result.created_list_id);
          setSelectedList(lst);
        }
        setShowSavedRecipes(false);
      }
    } catch (err) {
      console.error('Failed to add recipe to list', err);
      window.alert('Failed to add recipe to shopping list');
    }
  };

  const confirmSavedRecipeImport = async () => {
    const multiplier = servingsAdjust.enabled && recipeModal.servings 
      ? servingsAdjust.peopleEating / recipeModal.servings 
      : 1.0;
    
    try {
      const result = await apiService.addSavedRecipeToList({
        recipe_id: recipeModal.savedRecipeId,
        servings_multiplier: multiplier,
        exclude_ingredients: Array.from(excludedIngredients)
      });
      
      await loadLists();
      if (result.created_list_id) {
        const allLists = await apiService.getShoppingLists(householdId);
        const lst = allLists.find(l => l.id === result.created_list_id);
        setSelectedList(lst);
      }
      setRecipeModal(null);
      setExcludedIngredients(new Set());
    } catch (err) {
      console.error('Failed to create shopping list from saved recipe', err);
    }
  };

  const deleteSavedRecipe = async (recipeId) => {
    if (!window.confirm('Delete this saved recipe?')) return;
    try {
      await apiService.deleteSavedRecipe(recipeId, householdId);
      await loadSavedRecipes();
    } catch (err) {
      console.error('Failed to delete recipe', err);
    }
  };

  const addItemToList = async (e) => {
    e.preventDefault();
    if (!selectedList) return;

    try {
      const payload = {
        name: newItem.name,
        quantity: parseFloat(newItem.quantity),
        unit: newItem.unit,
      };
      await apiService.addItemToList(selectedList.id, payload);
      setNewItem({ name: '', quantity: 1, unit: 'unit' });
      await loadLists();
      // reselect the updated list
      const updated = (lists || []).find(l => l.id === selectedList.id);
      setSelectedList(updated || null);
    } catch (error) {
      console.error('Error adding item to list:', error);
    }
  };

  const handleRenameList = async (e) => {
    const name = e.target.value;
    setSelectedList({ ...selectedList, name });
  };

  const handleRenameListBlur = async () => {
    try {
      await apiService.updateList(selectedList.id, { name: selectedList.name });
      await loadLists();
      const updated = (lists || []).find(l => l.id === selectedList.id);
      setSelectedList(updated || null);
    } catch (e) {
      console.error('Failed to rename list', e);
    }
  };

  const handleItemChange = (itemId, field, value) => {
    const items = (selectedList.items || []).map(it => it.id === itemId ? { ...it, [field]: value } : it);
    setSelectedList({ ...selectedList, items });
  };

  const handleItemBlur = async (item) => {
    try {
      const payload = {
        name: item.name,
        quantity: parseFloat(item.quantity),
        unit: item.unit,
        notes: item.notes || null,
      };
      await apiService.updateListItem(item.id, payload);
      await loadLists();
      const updated = (lists || []).find(l => l.id === selectedList.id);
      setSelectedList(updated || null);
    } catch (e) {
      console.error('Failed to update item', e);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Shopping Lists</h2>
        <form onSubmit={createList} className="flex gap-2 mb-4">
          <input
            type="text"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            placeholder="New list name"
            className="flex-1 p-2 border rounded"
            required
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Create List
          </button>
        </form>

        <form onSubmit={importRecipe} className="flex gap-2 mb-4">
          <input
            type="url"
            value={recipeUrl}
            onChange={(e) => setRecipeUrl(e.target.value)}
            placeholder="Paste recipe URL (Allrecipes, Food Network, etc.)"
            className="flex-1 p-2 border rounded"
            required
          />
          <button
            type="submit"
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Import Recipe
          </button>
          <button
            onClick={() => setShowSavedRecipes(!showSavedRecipes)}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            {showSavedRecipes ? 'Hide' : 'Show'} Saved Recipes ({savedRecipes.length})
          </button>
        </form>

        {/* Saved Recipes Panel */}
        {showSavedRecipes && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
            <h3 className="font-bold mb-3">📚 Saved Recipes</h3>
            {savedRecipes.length === 0 ? (
              <p className="text-gray-600 text-sm">No saved recipes yet. Import a recipe and click "Save Recipe" to save it!</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {savedRecipes.map(recipe => (
                  <div key={recipe.id} className="bg-white p-3 rounded border border-green-300 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-semibold">{recipe.title}</div>
                      {recipe.url && (
                        <a href={recipe.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">
                          View Original Recipe →
                        </a>
                      )}
                      <div className="text-xs text-gray-600 mt-1">
                        {recipe.ingredients.length} ingredients
                        {recipe.servings && ` • Serves ${recipe.servings}`}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => addSavedRecipeToList(recipe)}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Add to List
                      </button>
                      <button
                        onClick={() => deleteSavedRecipe(recipe.id)}
                        className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Pricing settings panel */}
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <div className="flex items-center gap-3 mb-2">
            <input
              type="checkbox"
              id="enable-pricing"
              checked={!!pricingSettings.pricing_enabled}
              onChange={(e) => setPricingSettings({ ...pricingSettings, pricing_enabled: e.target.checked })}
            />
            <label htmlFor="enable-pricing" className="font-semibold">Enable price comparison</label>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-2 items-end">
            <div>
              <label className="block text-xs text-gray-600">ZIP Code</label>
              <input className="p-2 border rounded w-full" value={pricingSettings.zip_code || ''} onChange={(e)=> setPricingSettings({ ...pricingSettings, zip_code: e.target.value })} placeholder="e.g., 94016" />
            </div>
            <div>
              <label className="block text-xs text-gray-600">Latitude</label>
              <input type="number" className="p-2 border rounded w-full" value={pricingSettings.latitude ?? ''} onChange={(e)=> setPricingSettings({ ...pricingSettings, latitude: e.target.value })} placeholder="optional" />
            </div>
            <div>
              <label className="block text-xs text-gray-600">Longitude</label>
              <input type="number" className="p-2 border rounded w-full" value={pricingSettings.longitude ?? ''} onChange={(e)=> setPricingSettings({ ...pricingSettings, longitude: e.target.value })} placeholder="optional" />
            </div>
            <div>
              <label className="block text-xs text-gray-600">Radius (miles)</label>
              <input type="number" min="1" max="50" className="p-2 border rounded w-full" value={pricingSettings.radius_miles ?? 5} onChange={(e)=> setPricingSettings({ ...pricingSettings, radius_miles: e.target.value })} />
            </div>
            <div>
              <button onClick={savePricingSettings} className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 w-full">Save</button>
            </div>
          </div>
        </div>
        <div className="flex gap-2 mb-4">
          {lists.map(list => (
            <button
              key={list.id}
              onClick={() => setSelectedList(list)}
              className={`px-4 py-2 rounded ${
                selectedList?.id === list.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100'
              }`}
            >
              {list.name}
            </button>
          ))}
        </div>
      </div>

      {selectedList && (
        <div>
          <div className="mb-4 flex items-center gap-3">
            <input
              className="text-xl font-semibold bg-transparent border-b border-dashed focus:outline-none flex-1"
              value={selectedList.name}
              onChange={handleRenameList}
              onBlur={handleRenameListBlur}
            />
            <button
              onClick={async () => {
                const isStaples = selectedList.name.toLowerCase() === 'staples';
                const message = isStaples 
                  ? 'Deleting the Staples list will remove the staple flag from all your pantry items. Are you sure?'
                  : `Delete "${selectedList.name}"?`;
                
                if (window.confirm(message)) {
                  try {
                    await apiService.deleteList(selectedList.id);
                    setSelectedList(null);
                    await loadLists();
                  } catch (err) {
                    console.error('Failed to delete list', err);
                  }
                }
              }}
              className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
            >
              Delete List
            </button>
          </div>
          <form onSubmit={addItemToList} className="flex gap-2 mb-4">
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
              min="1"
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
            <button
              type="submit"
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Add Item
            </button>
          </form>

          <ul className="space-y-2">
            {selectedList.items?.filter(i => !i.shopped).map(item => (
              <li key={item.id} className="p-2 bg-gray-50 rounded">
                <div className="grid grid-cols-12 gap-2 items-center">
                <label className="col-span-1 flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={item.shopped || false}
                    onChange={async (e) => {
                      if (e.target.checked) {
                        try {
                          await apiService.markListItemShopped(item.id);
                          await loadLists();
                          const updated = (lists || []).find(l => l.id === selectedList.id);
                          setSelectedList(updated || null);
                        } catch (err) {
                          console.error('Failed to mark shopped', err);
                        }
                      }
                    }}
                  />
                  <span className="text-xs">Shopped!</span>
                </label>
                <input
                  className="col-span-4 p-1 border rounded"
                  value={item.name}
                  onChange={(e) => handleItemChange(item.id, 'name', e.target.value)}
                  onBlur={() => handleItemBlur(item)}
                />
                <input
                  type="number"
                  className="col-span-2 p-1 border rounded"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(item.id, 'quantity', e.target.value)}
                  onBlur={() => handleItemBlur(item)}
                />
                <select
                  className="col-span-2 p-1 border rounded"
                  value={item.unit}
                  onChange={(e) => handleItemChange(item.id, 'unit', e.target.value)}
                  onBlur={() => handleItemBlur(item)}
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
                  className="col-span-3 p-1 border rounded"
                  placeholder="notes"
                  value={getUserNotes(item.notes)}
                  onChange={(e) => {
                    const newUserNotes = e.target.value;
                    const newNotes = saveNotesWithOffer(item.notes, newUserNotes);
                    handleItemChange(item.id, 'notes', newNotes);
                  }}
                  onBlur={() => handleItemBlur(item)}
                />
                </div>
                {/* Price comparison row */}
                <div className="mt-2">
                  <div className="flex items-center gap-2">
                    <button
                      disabled={!pricingSettings.pricing_enabled}
                      onClick={() => toggleOffersForItem(item)}
                      className={`px-3 py-1 rounded text-sm ${pricingSettings.pricing_enabled ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-gray-200 text-gray-500'}`}
                    >
                      {offersByItem[item.id]?.expanded ? 'Hide prices' : 'Show prices nearby'}
                    </button>
                    {/* Inline chosen badge */}
                    {(() => {
                      try {
                        const so = item.notes ? JSON.parse(item.notes).selected_offer : null;
                        if (!so) return null;
                        return (
                          <span className="text-xs inline-flex items-center gap-2 bg-green-100 text-green-800 px-2 py-1 rounded">
                            Chosen: {so.store}{so.price != null ? ` • $${Number(so.price).toFixed(2)}` : ''}
                            <button onClick={() => clearOfferForItem(item)} className="ml-1 text-green-700 hover:underline">Clear</button>
                          </span>
                        );
                      } catch { return null; }
                    })()}
                    {!pricingSettings.pricing_enabled && (
                      <span className="text-xs text-gray-500">Enable price comparison above</span>
                    )}
                    {offersByItem[item.id]?.loading && (
                      <span className="text-xs text-gray-600">Loading offers…</span>
                    )}
                    {offersByItem[item.id]?.error && (
                      <span className="text-xs text-red-600">{offersByItem[item.id]?.error}</span>
                    )}
                  </div>
                  {offersByItem[item.id]?.expanded && !offersByItem[item.id]?.loading && (
                    <div className="mt-2">
                      {offersByItem[item.id]?.normalized_query && (
                        <div className="text-xs text-gray-500 mb-1">Searching for: "{offersByItem[item.id]?.normalized_query}"</div>
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                      {(offersByItem[item.id]?.offers || []).length === 0 && (
                        <div className="text-xs text-gray-600">No offers found for "{offersByItem[item.id]?.normalized_query || item.name}"</div>
                      )}
                      {(offersByItem[item.id]?.offers || []).map((offer, idx) => {
                        let selected = false;
                        try {
                          const so = item.notes ? JSON.parse(item.notes).selected_offer : null;
                          if (so) {
                            selected = (
                              so.store === offer.store &&
                              Number(so.price ?? -1) === Number(offer.price ?? -2) &&
                              (so.url || '') === (offer.url || '')
                            );
                          }
                        } catch {}
                        return (
                          <button
                            key={idx}
                            onClick={() => selectOfferForItem(item, offer)}
                            className={`text-left p-2 border rounded hover:bg-green-50 ${selected ? 'ring-2 ring-green-500 bg-green-50' : ''}`}
                            title={offer.url || ''}
                          >
                            <div className="flex items-center justify-between">
                              <div className="font-medium">{offer.store}</div>
                              {selected && <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">Chosen</span>}
                            </div>
                            <div className="text-sm">{offer.price != null ? `$${offer.price.toFixed(2)}` : 'Price N/A'} {offer.unit ? `• ${offer.unit}` : ''}</div>
                            {offer.promo_text && <div className="text-xs text-green-700 mt-1">{offer.promo_text}</div>}
                            <div className="text-xs text-gray-500">{offer.provider}{offer.distance_miles != null ? ` • ${offer.distance_miles.toFixed(1)} mi` : ''}</div>
                          </button>
                        );
                      })}
                      </div>
                    </div>
                  )}
                </div>
              </li>))}
            
            {/* Shopped items at bottom, dimmed */}
            {selectedList.items?.filter(i => i.shopped).length > 0 && (
              <>
                <li className="mt-4 pt-4 border-t border-gray-300">
                  <span className="text-sm text-gray-500 font-semibold">Shopped Items</span>
                </li>
                {selectedList.items?.filter(i => i.shopped).map(item => (
                  <li key={item.id} className="grid grid-cols-12 gap-2 items-center p-2 bg-gray-100 rounded opacity-60">
                    <div className="col-span-1 flex items-center gap-1">
                      <button
                        onClick={async () => {
                          try {
                            await apiService.restoreListItem(item.id);
                            await loadLists();
                            const updated = (lists || []).find(l => l.id === selectedList.id);
                            setSelectedList(updated || null);
                          } catch (err) {
                            console.error('Failed to restore item', err);
                          }
                        }}
                        className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        Restore
                      </button>
                    </div>
                    <div className="col-span-4 p-1 text-gray-500 line-through">{item.name}</div>
                    <div className="col-span-2 p-1 text-gray-500">{item.quantity} {item.unit}</div>
                    <div className="col-span-5 p-1 text-gray-500 text-sm">{item.notes || ''}</div>
                  </li>
                ))}
              </>
            )}
          </ul>
        </div>
      )}

      {/* Recipe Import Modal */}
      {recipeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold mb-4">{recipeModal.title}</h3>
            
            {/* Servings Adjustment */}
            {recipeModal.servings && (
              <div className="mb-4 p-4 bg-blue-50 rounded">
                <div className="flex items-center gap-3 mb-2">
                  <input
                    type="checkbox"
                    id="adjust-servings"
                    checked={servingsAdjust.enabled}
                    onChange={(e) => setServingsAdjust({ ...servingsAdjust, enabled: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <label htmlFor="adjust-servings" className="font-semibold">Adjust recipe quantities for servings</label>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm">Recipe serves: <strong>{recipeModal.servings}</strong></span>
                  <span className="text-sm">→</span>
                  <label className="text-sm">People eating:</label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={servingsAdjust.peopleEating}
                    onChange={(e) => setServingsAdjust({ ...servingsAdjust, peopleEating: parseInt(e.target.value) || 1 })}
                    disabled={!servingsAdjust.enabled}
                    className="w-20 p-1 border rounded disabled:bg-gray-100"
                  />
                  {servingsAdjust.enabled && (
                    <span className="text-sm text-blue-600 font-semibold">
                      (×{(servingsAdjust.peopleEating / recipeModal.servings).toFixed(2)})
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Conflicts Warning */}
            {recipeModal.conflicts.length > 0 && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-red-800">⚠️ Dietary Conflicts Detected</h4>
                  <button
                    onClick={() => setExcludedIngredients(new Set())}
                    className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Accept All Conflicts
                  </button>
                </div>
                <p className="text-sm text-red-700 mb-3">Check ingredients to EXCLUDE from your shopping list:</p>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {/* Group conflicts by ingredient */}
                  {Array.from(new Set(recipeModal.conflicts.map(c => c.ingredient))).map((ingredient) => {
                    const ingredientConflicts = recipeModal.conflicts.filter(c => c.ingredient === ingredient);
                    const hasAllergy = ingredientConflicts.some(c => c.conflict_type === 'allergy');
                    const isExcluded = excludedIngredients.has(ingredient);
                    
                    return (
                      <div key={ingredient} className="flex items-start gap-2 bg-white p-2 rounded">
                        <input
                          type="checkbox"
                          id={`exclude-${ingredient}`}
                          checked={isExcluded}
                          onChange={(e) => {
                            const newExcluded = new Set(excludedIngredients);
                            if (e.target.checked) {
                              newExcluded.add(ingredient);
                            } else {
                              newExcluded.delete(ingredient);
                            }
                            setExcludedIngredients(newExcluded);
                          }}
                          className="mt-1 w-4 h-4"
                        />
                        <label htmlFor={`exclude-${ingredient}`} className="flex-1 text-sm cursor-pointer">
                          <span className="font-semibold">{ingredient}</span>
                          <div className="ml-2 space-y-1">
                            {ingredientConflicts.map((conflict, idx) => (
                              <div key={idx} className={
                                conflict.conflict_type === 'allergy' ? 'text-red-700 font-bold' :
                                conflict.conflict_type === 'dietary' ? 'text-orange-600' :
                                'text-gray-600'
                              }>
                                → {conflict.member_name}: {conflict.details}
                              </div>
                            ))}
                          </div>
                        </label>
                        {hasAllergy && (
                          <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">ALLERGY</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Substitution Suggestions */}
            {recipeModal.substitutions && recipeModal.substitutions.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2 text-blue-700">💡 Suggested Substitutions:</h4>
                <div className="bg-blue-50 p-3 rounded text-sm space-y-3">
                  {recipeModal.substitutions.map((sub, idx) => (
                    <div key={idx} className="border-b border-blue-200 pb-2 last:border-b-0">
                      <div className="font-medium text-gray-800 mb-1">{sub.ingredient}</div>
                      {sub.dietary_subs && sub.dietary_subs.length > 0 && (
                        <div className="ml-3 mb-1">
                          <span className="text-blue-600 font-medium">Dietary:</span>
                          <ul className="list-disc list-inside ml-3">
                            {sub.dietary_subs.map((ds, dsIdx) => {
                              const text = typeof ds === 'string' ? ds : ds.substitute;
                              const reason = typeof ds === 'string' ? '' : ds.reason;
                              return (
                                <li key={dsIdx}>
                                  <span className="font-medium">{text}</span>
                                  {reason && <span className="text-gray-600 text-xs ml-1">({reason})</span>}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}
                      {sub.healthy_subs && sub.healthy_subs.length > 0 && (
                        <div className="ml-3">
                          <span className="text-green-600 font-medium">Healthier alternatives:</span>
                          <ul className="list-disc list-inside ml-3">
                            {sub.healthy_subs.map((hs, hsIdx) => {
                              const text = typeof hs === 'string' ? hs : hs.substitute;
                              const reason = typeof hs === 'string' ? '' : hs.reason;
                              return (
                                <li key={hsIdx}>
                                  <span className="font-medium">{text}</span>
                                  {reason && <span className="text-gray-600 text-xs ml-1">({reason})</span>}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Ingredients */}
            <div className="mb-4">
              <h4 className="font-semibold mb-2">Missing Ingredients ({recipeModal.missing.length}):</h4>
              <ul className="list-disc list-inside text-sm max-h-60 overflow-y-auto bg-gray-50 p-3 rounded">
                {recipeModal.missing.map((ing, idx) => (
                  <li key={idx} className="mb-1">{ing}</li>
                ))}
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setRecipeModal(null);
                  setRecipeUrl('');
                }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              {recipeModal.url && !recipeModal.savedRecipeId && (
                <button
                  onClick={saveRecipeFromModal}
                  className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                >
                  💾 Save Recipe
                </button>
              )}
              <button
                onClick={recipeModal.savedRecipeId ? confirmSavedRecipeImport : confirmRecipeImport}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Create Shopping List
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}