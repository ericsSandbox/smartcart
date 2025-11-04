import { useState, useEffect } from 'react';
import apiService from '../services/apiService';

export function MembersManager({ householdId, highlightMemberId }) {
  const [members, setMembers] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [newMember, setNewMember] = useState({ name: '', role: 'adult' });
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [showAddRecipeUrl, setShowAddRecipeUrl] = useState(false);
  const [newRecipeUrl, setNewRecipeUrl] = useState('');

  const load = async () => {
    try {
      const list = await apiService.listMembers(householdId);
      setMembers(list);
      if (list.length && !selectedId) setSelectedId(list[0].id);
    } catch (e) {
      setError(e.message || 'Failed to load members');
    }
  };

  const loadSavedRecipes = async () => {
    try {
      const recipes = await apiService.getSavedRecipes(householdId);
      setSavedRecipes(recipes);
    } catch (e) {
      console.error('Failed to load saved recipes', e);
    }
  };

  useEffect(() => {
    if (householdId) {
      load();
      loadSavedRecipes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [householdId]);

  // Auto-select highlighted member
  useEffect(() => {
    if (highlightMemberId && members.length) {
      setSelectedId(highlightMemberId);
    }
  }, [highlightMemberId, members]);

  const add = async (e) => {
    e.preventDefault();
    if (!newMember.name.trim()) return;
    setSaving(true);
    try {
      const m = await apiService.addMember(householdId, newMember);
      setNewMember({ name: '', role: 'adult' });
      setMembers([...members, m]);
      setSelectedId(m.id);
    } catch (e) {
      setError(e.message || 'Failed to add member');
    } finally {
      setSaving(false);
    }
  };

  const selected = members.find(m => m.id === selectedId) || null;

  const startEdit = () => {
    if (!selected) return;
    setEditing({ ...selected });
  };

  const cancelEdit = () => setEditing(null);

  const saveEdit = async () => {
    if (!editing) return;
    setSaving(true);
    try {
      const updated = await apiService.updateMember(editing.id, {
        name: editing.name,
        role: editing.role,
        age: editing.age || null,
        likes: editing.likes || null,
        dislikes: editing.dislikes || null,
        favorite_recipes: editing.favorite_recipes || null,
        allergies: editing.allergies || null,
        dietary_pref: editing.dietary_pref || null,
      });
      setMembers(members.map(m => (m.id === updated.id ? updated : m)));
      setEditing(null);
    } catch (e) {
      setError(e.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id) => {
    setSaving(true);
    try {
      await apiService.deleteMember(id);
      const next = members.filter(m => m.id !== id);
      setMembers(next);
      if (selectedId === id) setSelectedId(next[0]?.id || null);
    } catch (e) {
      setError(e.message || 'Failed to delete member');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Household Members</h2>
      {error && <div className="mb-4 p-2 bg-red-50 text-red-700 rounded">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Members list and add */}
        <div className="md:col-span-1 bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2">Members</h3>
          <ul className="space-y-2">
            {members.map(m => (
              <li 
                key={m.id} 
                className={`flex justify-between items-center p-2 rounded cursor-pointer transition-all ${
                  selectedId === m.id 
                    ? highlightMemberId === m.id 
                      ? 'bg-red-100 border-2 border-red-500 animate-pulse' 
                      : 'bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`} 
                onClick={() => setSelectedId(m.id)}
              >
                <span>{m.name} <span className="text-gray-500 text-sm">({m.role || 'n/a'})</span></span>
                <button className="text-red-500 text-sm" onClick={(e) => { e.stopPropagation(); remove(m.id); }}>
                  Delete
                </button>
              </li>
            ))}
            {!members.length && <li className="text-gray-500">No members yet</li>}
          </ul>

          <form onSubmit={add} className="mt-4 space-y-2">
            <input
              type="text"
              value={newMember.name}
              onChange={e => setNewMember({ ...newMember, name: e.target.value })}
              placeholder="New member name"
              className="w-full p-2 border rounded"
              required
            />
            <select
              value={newMember.role}
              onChange={e => setNewMember({ ...newMember, role: e.target.value })}
              className="w-full p-2 border rounded"
            >
              <option value="adult">Adult</option>
              <option value="child">Child</option>
            </select>
            <button type="submit" disabled={saving} className="w-full py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50">
              Add Member
            </button>
          </form>
        </div>

        {/* Details */}
        <div className="md:col-span-2 bg-white p-4 rounded shadow">
          {!selected && <div className="text-gray-500">Select a member to view or edit details</div>}
          {selected && !editing && (
            <div>
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-lg">{selected.name}</h3>
                <button className="px-3 py-1 bg-blue-500 text-white rounded" onClick={startEdit}>Edit</button>
              </div>
              <div className="mt-2 text-sm text-gray-700 space-y-1">
                <div><span className="font-medium">Role:</span> {selected.role || '—'}</div>
                <div><span className="font-medium">Age:</span> {selected.age ?? '—'}</div>
                <div><span className="font-medium">Likes:</span> {selected.likes || '—'}</div>
                <div><span className="font-medium">Dislikes:</span> {selected.dislikes || '—'}</div>
                <div><span className="font-medium">Favorite Recipes:</span> {selected.favorite_recipes || '—'}</div>
                <div><span className="font-medium">Allergies:</span> {selected.allergies || '—'}</div>
                <div><span className="font-medium">Dietary Pref:</span> {selected.dietary_pref || '—'}</div>
              </div>
            </div>
          )}
          {editing && (
            <div className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <input className="p-2 border rounded" value={editing.name} onChange={e => setEditing({ ...editing, name: e.target.value })} />
                <select className="p-2 border rounded" value={editing.role || 'adult'} onChange={e => setEditing({ ...editing, role: e.target.value })}>
                  <option value="adult">Adult</option>
                  <option value="child">Child</option>
                </select>
                <input className="p-2 border rounded" type="number" placeholder="Age" value={editing.age || ''} onChange={e => setEditing({ ...editing, age: e.target.value })} />
                <input className="p-2 border rounded" placeholder="Likes" value={editing.likes || ''} onChange={e => setEditing({ ...editing, likes: e.target.value })} />
                <input className="p-2 border rounded" placeholder="Dislikes" value={editing.dislikes || ''} onChange={e => setEditing({ ...editing, dislikes: e.target.value })} />
                
                {/* Favorite Recipes Dropdown */}
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Favorite Recipes</label>
                  <select 
                    className="w-full p-2 border rounded" 
                    value={editing.favorite_recipes || ''}
                    onChange={async (e) => {
                      if (e.target.value === '__ADD_NEW__') {
                        setShowAddRecipeUrl(true);
                      } else {
                        setEditing({ ...editing, favorite_recipes: e.target.value });
                      }
                    }}
                  >
                    <option value="">-- No favorite recipe --</option>
                    {savedRecipes.map(recipe => (
                      <option key={recipe.id} value={recipe.title}>{recipe.title}</option>
                    ))}
                    <option value="__ADD_NEW__">➕ Add New Recipe from URL...</option>
                  </select>
                  
                  {showAddRecipeUrl && (
                    <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded">
                      <input
                        type="text"
                        className="w-full p-2 border rounded mb-2"
                        placeholder="Enter recipe URL"
                        value={newRecipeUrl}
                        onChange={e => setNewRecipeUrl(e.target.value)}
                      />
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="px-3 py-1 bg-gray-200 text-sm rounded"
                          onClick={() => {
                            setShowAddRecipeUrl(false);
                            setNewRecipeUrl('');
                          }}
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded"
                          onClick={async () => {
                            try {
                              // Import recipe to get its data
                              const result = await apiService.importRecipe(householdId, newRecipeUrl, false);
                              
                              // Save the recipe
                              await apiService.saveRecipe({
                                household_id: householdId,
                                title: result.title,
                                url: newRecipeUrl,
                                servings: result.servings,
                                ingredients: result.ingredients
                              });
                              
                              // Reload saved recipes and set as favorite
                              await loadSavedRecipes();
                              setEditing({ ...editing, favorite_recipes: result.title });
                              setShowAddRecipeUrl(false);
                              setNewRecipeUrl('');
                              
                              window.alert(`Recipe "${result.title}" saved and set as favorite!`);
                            } catch (err) {
                              console.error('Failed to add recipe', err);
                              window.alert('Failed to import recipe. Make sure the URL is valid.');
                            }
                          }}
                        >
                          Import & Save
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                
                <input className="p-2 border rounded" placeholder="Allergies" value={editing.allergies || ''} onChange={e => setEditing({ ...editing, allergies: e.target.value })} />
                <input className="p-2 border rounded" placeholder="Dietary Pref" value={editing.dietary_pref || ''} onChange={e => setEditing({ ...editing, dietary_pref: e.target.value })} />
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1 bg-gray-100 rounded" onClick={cancelEdit}>Cancel</button>
                <button className="px-3 py-1 bg-blue-500 text-white rounded" onClick={saveEdit} disabled={saving}>Save</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
