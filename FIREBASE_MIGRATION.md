# Firebase Migration Guide

## Overview
SmartCart has been migrated from localStorage + optional backend API to Firebase Firestore for real-time multi-device synchronization.

## What Changed

### Architecture
- **Before**: localStorage (single device) + optional FastAPI backend (localhost:8000)
- **After**: Firebase Firestore (cloud database) with real-time sync across all devices

### Key Benefits
1. **Multi-device access**: All household members can access pantry/shopping lists from their phones
2. **Real-time sync**: Changes appear instantly on all connected devices
3. **Offline support**: App works without internet, syncs when reconnected
4. **No server maintenance**: Firebase handles hosting, scaling, and backups

## Firebase Setup Required

### 1. Create Firebase Project
1. Go to [firebase.google.com](https://firebase.google.com)
2. Click "Get Started" → "Add Project"
3. Name: `SmartCart`
4. Disable Google Analytics (optional for household app)
5. Click "Create Project"

### 2. Enable Firestore
1. In Firebase Console, click "Firestore Database"
2. Click "Create Database"
3. Start in **production mode**
4. Choose location closest to you (e.g., `us-central1`)

### 3. Set Security Rules
In Firestore Console → Rules tab, paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write to household data
    match /households/{householdId}/{document=**} {
      allow read, write: if true;
    }
  }
}
```

**Note**: This allows anyone with the household ID to access data. For production, implement proper authentication.

### 4. Get Firebase Config
1. In Firebase Console, click ⚙️ (Settings) → "Project Settings"
2. Scroll to "Your apps" → Click Web icon `</>`
3. Register app name: `SmartCart`
4. Copy the `firebaseConfig` object
5. Paste values into `index.html` lines 961-967:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY_HERE",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_ID",
    appId: "YOUR_APP_ID"
};
```

## Data Structure

### Firestore Collections
```
households/{householdId}/
  ├─ pantry/{itemId}
  │   ├─ name: string
  │   ├─ quantity: number
  │   ├─ unit: string
  │   ├─ expires_at: string (ISO date)
  │   ├─ category: string
  │   └─ isStaple: boolean
  │
  ├─ shoppingLists/{listId}
  │   ├─ name: string
  │   ├─ items: array
  │   │   ├─ id: number
  │   │   ├─ name: string
  │   │   ├─ quantity: number
  │   │   ├─ unit: string
  │   │   └─ completed: boolean
  │   └─ createdAt: string (ISO date)
  │
  └─ members/{memberId}
      ├─ name: string
      ├─ age: number
      ├─ allergies: string
      └─ dietary_pref: string
```

### Household ID
- Stored in localStorage: `smartcart_household_id`
- Format: `household_{timestamp}`
- Auto-generated on first app load
- Share this ID with family members to access same data

## Importing Existing Data

### From Backup JSON
1. Open SmartCart
2. Click "📄 Backup & Restore"
3. Select your backup file (e.g., `smartcart-backup-2025-11-09.json`)
4. Click "Import"
5. Data will be uploaded to Firebase with progress indicator

### Manual Sharing
1. On primary device, open DevTools console (F12)
2. Run: `localStorage.getItem('smartcart_household_id')`
3. Copy the household ID
4. On secondary devices, open DevTools console
5. Run: `localStorage.setItem('smartcart_household_id', 'YOUR_HOUSEHOLD_ID')`
6. Refresh page

## Code Changes Summary

### Removed
- ❌ All backend API calls (`createPantryItemAPI`, etc.)
- ❌ `saveData()` function (replaced by Firebase auto-sync)
- ❌ Manual `renderUI()` calls after data changes
- ❌ localStorage read/write for pantry/shopping/members

### Added
- ✅ Firebase SDK v10.7.1 (compat mode)
- ✅ `initFirebase()` - Initialize connection with offline persistence
- ✅ `setupFirestoreListeners()` - Real-time data sync
- ✅ 8 Firebase CRUD functions:
  - `addPantryItemToFirebase()`
  - `updatePantryItemInFirebase()`
  - `deletePantryItemFromFirebase()`
  - `addShoppingListToFirebase()`
  - `updateShoppingListInFirebase()`
  - `deleteShoppingListFromFirebase()`
  - `addMemberToFirebase()`
  - `deleteMemberFromFirebase()`
- ✅ `importToFirebase()` - Batch import with progress UI

### Modified Functions (30+)
All data-modifying functions now call Firebase instead of localStorage:
- `addManualItem()` → `await addPantryItemToFirebase()`
- `addScannedItem()` → `await addPantryItemToFirebase()`
- `deletePantryItem()` → `await deletePantryItemFromFirebase()`
- `updateQuantity()` → `await updatePantryItemInFirebase()`
- `toggleStaple()` → `await updatePantryItemInFirebase()`
- `addMember()` → `await addMemberToFirebase()`
- `deleteMember()` → `await deleteMemberFromFirebase()`
- `createNewShoppingList()` → `await addShoppingListToFirebase()`
- `addItemToShoppingList()` → `await updateShoppingListInFirebase()`
- `toggleShoppingItem()` → `await updateShoppingListInFirebase()`
- `removeShoppingItem()` → `await updateShoppingListInFirebase()`
- `deleteShoppingList()` → `await deleteShoppingListFromFirebase()`
- `markShoppingDone()` → `await updateShoppingListInFirebase()`
- `renewShoppingList()` → `await updateShoppingListInFirebase()`
- `mergeShoppingLists()` → `await addShoppingListToFirebase()`
- `importIngredients()` → `await updateShoppingListInFirebase()`
- Plus all helper functions like `addToStaplesList()`, `addManualScanned()`

## Testing Checklist

### Single Device
- [ ] Add pantry item (manual entry)
- [ ] Add pantry item (barcode scan)
- [ ] Update quantity (+/-)
- [ ] Delete pantry item
- [ ] Toggle staple
- [ ] Add household member
- [ ] Delete household member
- [ ] Create shopping list
- [ ] Add items to shopping list
- [ ] Toggle item completion
- [ ] Delete shopping list item
- [ ] Mark all items done
- [ ] Renew shopping list
- [ ] Merge shopping lists
- [ ] Import ingredients from recipe
- [ ] Backup data (export JSON)
- [ ] Restore data (import JSON)

### Multi-Device
- [ ] Open app on Device 1, note household ID
- [ ] Open app on Device 2, set same household ID
- [ ] Add item on Device 1 → Verify appears on Device 2
- [ ] Delete item on Device 2 → Verify disappears on Device 1
- [ ] Create shopping list on Device 1 → Verify on Device 2
- [ ] Toggle item on Device 2 → Verify on Device 1
- [ ] Add member on Device 1 → Verify on Device 2

### Offline Behavior
- [ ] Turn off WiFi/cellular
- [ ] Add pantry item (should work)
- [ ] Add shopping list item (should work)
- [ ] Turn on WiFi/cellular
- [ ] Verify changes sync to Firebase
- [ ] Verify changes appear on other devices

## Troubleshooting

### Firebase Config Error
**Symptom**: App fails to load, console shows Firebase init error
**Solution**: 
1. Check Firebase config values in `index.html` lines 961-967
2. Ensure they match Firebase Console → Project Settings
3. Make sure `apiKey`, `projectId`, `appId` are correct

### No Data Syncing
**Symptom**: Changes don't appear on other devices
**Solution**:
1. Check browser console for errors
2. Verify both devices have same `householdId` in localStorage
3. Ensure Firestore security rules allow read/write
4. Check Firebase Console → Firestore → Data tab to see if data is being written

### Import Not Working
**Symptom**: Backup import shows error or no data
**Solution**:
1. Verify JSON file is valid (use JSONLint.com)
2. Check browser console for specific error
3. Ensure Firebase config is set correctly
4. Try smaller batch (break into multiple imports)

### Offline Not Working
**Symptom**: App doesn't work without internet
**Solution**:
1. Check browser console for persistence errors
2. Some browsers don't support offline persistence (use Chrome/Firefox)
3. Close all other tabs with SmartCart open (multi-tab limitation)
4. Try incognito mode to test fresh

## Migration Status

✅ **COMPLETED** (firebase-migration branch)
- Core infrastructure (Firebase init, listeners, CRUD)
- All pantry operations
- All shopping list operations
- All member operations
- Backup/restore system
- Old backend code removal

❌ **NOT STARTED**
- Firebase project creation (manual step)
- Config placeholder replacement (manual step)
- Real-world testing with Firebase

## Deployment

### After Firebase Setup Complete
1. Update Firebase config in `index.html`
2. Test locally with `python -m http.server 8080`
3. Commit changes: `git add . && git commit -m "Complete Firebase migration"`
4. Merge to main: `git checkout main && git merge firebase-migration`
5. Push to GitHub: `git push origin main`
6. GitHub Pages will auto-deploy

### Share With Family
1. Send household ID via text/email
2. Family members open app on their phones
3. Open browser DevTools (varies by mobile browser)
4. Set household ID in localStorage
5. Refresh - data should sync

### OR Use QR Code (Future Enhancement)
Generate QR code with household ID for easy sharing.

## Security Considerations

### Current Implementation
- Simple household ID in localStorage
- No user authentication
- Anyone with household ID can access data
- Suitable for trusted family use

### Future Enhancements
1. **Firebase Authentication**
   - Email/password login
   - Google Sign-In
   - Per-user permissions

2. **Invite System**
   - Primary user generates invite codes
   - Expiring invite links
   - Remove member access

3. **Data Encryption**
   - Encrypt sensitive fields
   - Key stored in user account
   - Prevent unauthorized access

## Support

### File Issues
- GitHub: [Your Repository URL]
- Include browser console errors
- Describe steps to reproduce

### Firebase Documentation
- [Firestore Quickstart](https://firebase.google.com/docs/firestore/quickstart)
- [Offline Persistence](https://firebase.google.com/docs/firestore/manage-data/enable-offline)
- [Security Rules](https://firebase.google.com/docs/firestore/security/get-started)

---

**Last Updated**: 2025-01-15  
**SmartCart Version**: Firebase Migration (Pre-Release)  
**Firebase SDK**: v10.7.1 (Compat Mode)
