const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Household endpoints
  async createHousehold(data) {
    const response = await fetch(`${API_BASE_URL}/households`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async getHousehold(id) {
    const response = await fetch(`${API_BASE_URL}/households/${id}`);
    return response.json();
  },

  // Shopping list endpoints
  async getShoppingLists(householdId) {
    const response = await fetch(`${API_BASE_URL}/households/${householdId}/lists`);
    return response.json();
  },

  async createShoppingList(householdId, data) {
    const response = await fetch(`${API_BASE_URL}/households/${householdId}/lists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // Pantry endpoints
  async getPantryItems(householdId) {
    const response = await fetch(`${API_BASE_URL}/households/${householdId}/pantry`);
    return response.json();
  },

  async addPantryItem(householdId, data) {
    const response = await fetch(`${API_BASE_URL}/households/${householdId}/pantry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // Saved recipes endpoints
  async getSavedRecipes(householdId) {
    const response = await fetch(`${API_BASE_URL}/recipes/saved/${householdId}`);
    return response.json();
  },

  async saveRecipe(data) {
    const response = await fetch(`${API_BASE_URL}/recipes/saved`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async deleteSavedRecipe(recipeId, householdId) {
    const response = await fetch(`${API_BASE_URL}/recipes/saved/${recipeId}?household_id=${householdId}`, {
      method: 'DELETE'
    });
    return response.json();
  },

  async addSavedRecipeToList(data) {
    const response = await fetch(`${API_BASE_URL}/recipes/saved/add-to-list`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },
};