// ============================================
// MODULAR JAVASCRIPT FOR SMARTCART
// ============================================
// This file provides modular organization while maintaining 
// compatibility with the existing inline code structure

import * as Config from './config.js';
import * as Utils from './utils.js';

// Export config and utils to global scope for compatibility
window.SmartCart = {
    Config,
    Utils
};

// Make key utilities available globally for inline HTML event handlers
window.levenshteinDistance = Utils.levenshteinDistance;
window.findSimilarItem = Utils.findSimilarItem;
window.autoCategorizePantryItem = Utils.autoCategorizePantryItem;
window.isExpired = Utils.isExpired;
window.getExpiresIn = Utils.getExpiresIn;

console.log('📦 SmartCart modules loaded:', Object.keys(window.SmartCart));
