# SmartCart Firebase Setup - Quick Start

## What You Need to Do Next

Your SmartCart app has been migrated to Firebase, but you need to create a Firebase project and update the configuration before it will work.

## Steps (15 minutes)

### 1. Create Firebase Project (5 min)
1. Open browser → [console.firebase.google.com](https://console.firebase.google.com)
2. Click **"Add Project"**
3. Enter project name: `SmartCart` (or anything you prefer)
4. Disable Google Analytics (not needed) → Click **Continue**
5. Wait for project creation → Click **Continue**

### 2. Enable Firestore Database (3 min)
1. In left sidebar, click **"Firestore Database"**
2. Click **"Create Database"**
3. Choose **"Start in production mode"**
4. Select location (choose closest to you):
   - US: `us-central1` or `us-east1`
   - Europe: `europe-west1`
   - Asia: `asia-northeast1`
5. Click **"Enable"**

### 3. Set Security Rules (2 min)
1. In Firestore Database, click **"Rules"** tab
2. Replace everything with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /households/{householdId}/{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click **"Publish"**

**Note**: This allows anyone with your household ID to access data. It's fine for family use, but don't share the household ID publicly.

### 4. Get Firebase Config (5 min)
1. Click ⚙️ icon (top left) → **"Project settings"**
2. Scroll down to **"Your apps"** section
3. Click the **`</>`** icon (Web)
4. App nickname: `SmartCart` → Click **"Register app"**
5. **Copy the config object** (looks like this):

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "smartcart-xxxxx.firebaseapp.com",
  projectId: "smartcart-xxxxx",
  storageBucket: "smartcart-xxxxx.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:..."
};
```

6. Open `index.html` in VS Code
7. Find **lines 961-967** (search for `firebaseConfig`)
8. **Replace the placeholder values** with your real config:

```javascript
const firebaseConfig = {
    apiKey: "PASTE_YOUR_API_KEY_HERE",
    authDomain: "PASTE_YOUR_AUTH_DOMAIN_HERE",
    projectId: "PASTE_YOUR_PROJECT_ID_HERE",
    storageBucket: "PASTE_YOUR_STORAGE_BUCKET_HERE",
    messagingSenderId: "PASTE_YOUR_MESSAGING_ID_HERE",
    appId: "PASTE_YOUR_APP_ID_HERE"
};
```

9. Save the file

### 5. Test Locally
```bash
# In SmartCart directory
python -m http.server 8080
```

Open browser: `http://localhost:8080`

**Try these:**
- ✅ Add a pantry item
- ✅ Create a shopping list
- ✅ Add household member
- ✅ Open DevTools console - should see: `✅ Firebase connected. Household ID: household_...`

### 6. Import Your Existing Data
1. In SmartCart, click **"📄 Backup & Restore"**
2. Click **"Choose File"** → Select `smartcart-backup-2025-11-09.json`
3. Click **"Import from JSON"**
4. Watch progress dialog (should import 136 pantry items, 4 members)
5. Verify data appears in Firebase Console → Firestore Database → Data tab

### 7. Share With Family
**Option A: Manual (Works on all devices)**
1. On your phone, open SmartCart
2. Open browser DevTools/console:
   - Chrome Android: Menu → More tools → Developer tools
   - Safari iOS: Settings → Safari → Advanced → Web Inspector
3. Type: `localStorage.getItem('smartcart_household_id')`
4. Copy the household ID (e.g., `household_1737079200000`)
5. Text/email to family
6. Family members open SmartCart → DevTools → Run:
   ```javascript
   localStorage.setItem('smartcart_household_id', 'PASTE_HOUSEHOLD_ID')
   ```
7. Refresh page → Should see your data!

**Option B: Simple (For tech-savvy family)**
1. Share this exact household ID with them: `YOUR_ID_HERE`
2. They paste it in DevTools as shown above

### 8. Test Multi-Device Sync
1. Open SmartCart on your phone
2. Open SmartCart on another phone/computer (with same household ID)
3. Add a pantry item on Phone 1
4. Watch it appear on Phone 2 **instantly** (no refresh needed!)
5. Delete item on Phone 2 → Disappears on Phone 1

**🎉 If this works, Firebase migration is complete!**

### 9. Deploy to GitHub Pages
```bash
git add index.html
git commit -m "Add Firebase config"
git checkout main
git merge firebase-migration
git push origin main
```

Wait 2-3 minutes → Your app will be live at `https://YOUR_USERNAME.github.io/SmartCart/`

## Troubleshooting

### "Firebase not defined" error
- Make sure you saved `index.html` after updating config
- Check that Firebase SDK scripts are in the `<head>` section (lines 12-18)
- Clear browser cache and refresh

### "Permission denied" error
- Check Firestore Rules (Step 3) are published
- Make sure rules allow `read, write: if true;`
- Verify you're reading/writing to `/households/{householdId}/...` path

### Data not syncing between devices
- Both devices must have **same household ID** in localStorage
- Check browser console for errors
- Verify Firebase config is correct
- Make sure internet connection is active

### Import fails
- Verify JSON file is valid (open in text editor, should see proper JSON)
- Check browser console for specific error
- Make sure Firebase config is set before importing

## Get Your Household ID

Open browser console in SmartCart and run:
```javascript
localStorage.getItem('smartcart_household_id')
```

Copy and save this! You'll need it to add family members.

## Summary

✅ Firebase project created  
✅ Firestore enabled  
✅ Security rules set  
✅ Config updated in index.html  
✅ Local testing successful  
✅ Data imported  
✅ Multi-device sync working  
✅ Deployed to GitHub Pages  

**You're done! Enjoy your multi-device SmartCart! 🎉**

---

**Need Help?**  
See full documentation: `FIREBASE_MIGRATION.md`  
Questions? Open an issue on GitHub
