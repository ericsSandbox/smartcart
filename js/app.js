// ============================================
// MAIN APP INITIALIZATION
// ============================================

import { initFirebase, db, householdId } from './config.js';
import { renderUI, setupEventListeners, initScanner } from './pantry.js';
import { setupFirestoreListeners, loadData } from './household.js';

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 SmartCart initializing...');
    
    // Initialize Firebase
    const firebaseReady = await initFirebase();
    if (!firebaseReady) {
        alert('❌ Failed to connect to Firebase. Please check your connection.');
        return;
    }
    
    // Set up real-time listeners
    await setupFirestoreListeners();
    
    // Load initial data
    await loadData();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize pantry view mode
    const viewMode = localStorage.getItem('pantryViewMode') || 'category';
    const btn = document.getElementById('viewToggleBtn');
    if (btn) {
        btn.textContent = viewMode === 'category' ? '📂 View: Categories' : '📋 View: Items';
    }
    
    // Render initial UI
    renderUI();
    
    // Initialize barcode scanner
    initScanner();
    
    console.log('✅ SmartCart ready!');
});

// Tab switching
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
        const targetTab = e.target.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.getElementById(targetTab)?.classList.add('active');
        
        console.log('📑 Switched to tab:', targetTab);
    }
});

// Form toggle (manual vs barcode)
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-toggle')) {
        const targetForm = e.target.dataset.form;
        
        // Update active toggle
        document.querySelectorAll('.tab-toggle').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update active form
        document.querySelectorAll('.form-section').forEach(form => form.classList.remove('active'));
        document.querySelector(`.form-section[data-form="${targetForm}"]`)?.classList.add('active');
    }
});

console.log('📱 SmartCart app.js loaded');
