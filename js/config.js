// ============================================
// FIREBASE CONFIGURATION & GLOBAL STATE
// ============================================

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyANLrJ54KQJi2R4VaU02DsuA6GxGTO0BQ8",
    authDomain: "smartcart-faf36.firebaseapp.com",
    projectId: "smartcart-faf36",
    storageBucket: "smartcart-faf36.firebasestorage.app",
    messagingSenderId: "36120215522",
    appId: "1:36120215522:web:720084b2c098555d89efe3"
};

// Global state
export let db = null;
export let householdId = null;
export let pantryItems = [];
export let shoppingLists = [];
export let members = [];
export let recipes = [];
export let scannerActive = false;
export let lastDetectedBarcode = null;

// Firestore listeners (for cleanup)
export let pantryUnsubscribe = null;
export let shoppingUnsubscribe = null;
export let membersUnsubscribe = null;
export let recipesUnsubscribe = null;

// Update functions for global state
export function setPantryItems(items) {
    pantryItems = items;
}

export function setShoppingLists(lists) {
    shoppingLists = lists;
}

export function setMembers(membersList) {
    members = membersList;
}

export function setRecipes(recipesList) {
    recipes = recipesList;
}

export function setScannerActive(active) {
    scannerActive = active;
}

export function setLastDetectedBarcode(barcode) {
    lastDetectedBarcode = barcode;
}

// Initialize Firebase
export async function initFirebase() {
    try {
        firebase.initializeApp(firebaseConfig);
        db = firebase.firestore();
        
        // Enable offline persistence
        await db.enablePersistence({
            synchronizeTabs: true
        }).catch((err) => {
            if (err.code === 'failed-precondition') {
                console.warn('⚠️ Multiple tabs open, persistence only in first tab');
            } else if (err.code === 'unimplemented') {
                console.warn('⚠️ Browser does not support offline persistence');
            }
        });
        
        // Check URL for household ID parameter (e.g., ?household=household_123)
        const urlParams = new URLSearchParams(window.location.search);
        const urlHouseholdId = urlParams.get('household');
        
        if (urlHouseholdId && urlHouseholdId.startsWith('household_')) {
            // URL has household ID - use it and save it
            householdId = urlHouseholdId;
            localStorage.setItem('smartcart_household_id', householdId);
            console.log('🔗 Joined household from URL:', householdId);
        } else {
            // Get or create household ID from localStorage
            householdId = localStorage.getItem('smartcart_household_id');
            if (!householdId) {
                householdId = 'household_' + Date.now();
                localStorage.setItem('smartcart_household_id', householdId);
            }
        }
        
        console.log('✅ Firebase connected. Household ID:', householdId);
        return true;
    } catch (error) {
        console.error('❌ Firebase initialization failed:', error);
        return false;
    }
}
