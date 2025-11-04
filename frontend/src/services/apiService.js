import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Household endpoints
  async createHousehold(data) {
  const response = await api.post('/households', data);
    return response.data;
  },

  async getHousehold(id) {
  const response = await api.get(`/households/${id}`);
    return response.data;
  },

  // Shopping list endpoints
  async getShoppingLists(householdId) {
    // backend exposes lists under /lists/household/{id}/
  const response = await api.get(`/lists/household/${householdId}`);
    return response.data;
  },

  async createShoppingList(householdId, data) {
    // backend expects POST /lists/ with payload containing household_id
    const payload = { ...data, household_id: householdId };
  const response = await api.post(`/lists`, payload);
    return response.data;
  },

  // Pantry endpoints
  async getPantryItems(householdId) {
  const response = await api.get(`/households/${householdId}/pantry`);
    return response.data;
  },

  async addPantryItem(householdId, data) {
  const response = await api.post(`/households/${householdId}/pantry`, data);
    return response.data;
  },

  async updatePantryItem(householdId, itemId, data) {
    const response = await api.patch(`/households/${householdId}/pantry/${itemId}`, data);
    return response.data;
  },

  async deletePantryItem(householdId, itemId) {
    const response = await api.delete(`/households/${householdId}/pantry/${itemId}`);
    return response.data;
  },

  // Members endpoints
  async listMembers(householdId) {
    const response = await api.get(`/members/households/${householdId}`);
    return response.data;
  },

  // New: Shopping list item operations and edits
  async addItemToList(listId, data) {
    const response = await api.post(`/lists/${listId}/items`, data);
    return response.data;
  },

  async updateList(listId, data) {
    const response = await api.patch(`/lists/${listId}`, data);
    return response.data;
  },

  async deleteList(listId) {
    const response = await api.delete(`/lists/${listId}`);
    return response.data;
  },

  async updateListItem(itemId, data) {
    const response = await api.patch(`/lists/items/${itemId}`, data);
    return response.data;
  },

  async deleteListItem(itemId) {
    const response = await api.delete(`/lists/items/${itemId}`);
    return response.data;
  },

  async markListItemShopped(itemId) {
    const response = await api.post(`/lists/items/${itemId}/shopped`);
    return response.data;
  },

  async restoreListItem(itemId) {
    const response = await api.post(`/lists/items/${itemId}/restore`);
    return response.data;
  },

  async importRecipe(householdId, url, createList = false, servingsMultiplier = 1.0, excludeIngredients = []) {
    const response = await api.post(`/recipes/import`, { 
      household_id: householdId, 
      url, 
      create_list: createList,
      servings_multiplier: servingsMultiplier,
      exclude_ingredients: excludeIngredients
    });
    return response.data;
  },

  async addMember(householdId, data) {
    const response = await api.post(`/members/households/${householdId}`, data);
    return response.data;
  },

  async updateMember(memberId, data) {
    const response = await api.patch(`/members/${memberId}`, data);
    return response.data;
  },

  async deleteMember(memberId) {
    const response = await api.delete(`/members/${memberId}`);
    return response.data;
  },

  // Saved recipes endpoints
  async getSavedRecipes(householdId) {
    const response = await api.get(`/recipes/saved/${householdId}`);
    return response.data;
  },

  async saveRecipe(data) {
    const response = await api.post(`/recipes/saved`, data);
    return response.data;
  },

  async deleteSavedRecipe(recipeId, householdId) {
    const response = await api.delete(`/recipes/saved/${recipeId}?household_id=${householdId}`);
    return response.data;
  },

  async addSavedRecipeToList(data) {
    const response = await api.post(`/recipes/saved/add-to-list`, data);
    return response.data;
  },

  // Pricing endpoints
  async getPricingSettings(householdId) {
    const response = await api.get(`/pricing/settings/${householdId}`);
    return response.data;
  },

  async savePricingSettings(payload) {
    const response = await api.post(`/pricing/settings`, payload);
    return response.data;
  },

  async getOffers(payload) {
    const response = await api.post(`/pricing/offers`, payload);
    return response.data;
  },

  async getCirculars() {
    const response = await api.get(`/pricing/circulars`);
    return response.data;
  },

  // Error interceptor
  setup() {
    api.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }
};

export default apiService;