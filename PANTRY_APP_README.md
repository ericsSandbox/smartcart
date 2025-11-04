# SmartCart Pantry App - Portable Version

## 📱 iPhone Installation

This is a **Progressive Web App (PWA)** - you can install it directly on your iPhone home screen like a native app!

### Installation Steps:

1. **Open in Safari Browser**
   - Go to `file:///home/eric/Projects/SmartCart/pantry-app.html` on your phone
   - OR copy the HTML file to a web server and access via URL

2. **Add to Home Screen**
   - Tap the **Share button** (↗️) at the bottom of Safari
   - Scroll down and tap **"Add to Home Screen"**
   - Name it "SmartCart Pantry" (or whatever you prefer)
   - Tap **"Add"**

3. **That's it!** 
   - The app now appears on your home screen
   - Opens full-screen like a native app
   - Works offline with local storage

### Features:

✅ **Inventory Tracking**
- Add/remove items with quantities
- Track units (lbs, oz, cups, etc.)
- Mark items as staples (frequently purchased)

✅ **Expiration Tracking**
- Set expiration dates
- Get warnings for soon-to-expire items
- Track expired items separately

✅ **Smart Stats**
- Total items in pantry
- Low stock warnings
- Expiring soon alerts

✅ **Search & Filter**
- Search items by name
- Separate view for staple items
- Color-coded status (red = expired, orange = expiring soon)

✅ **Works Offline**
- All data saved locally on your phone
- No internet needed
- Data persists between sessions

### Data Storage:

- Uses **browser local storage** (stored on your device)
- Data is NOT synced to cloud (intentional - for privacy)
- **Backup**: Export data by taking screenshots or notes

### To Transfer Data to Desktop:

If you need to sync with the main SmartCart app, manually transfer items back through the web app at `http://localhost:5173`

### Troubleshooting:

**App doesn't save data?**
- Check if Safari allows local storage (Settings > Safari > Privacy & Security)

**Icons not showing on iPhone?**
- Restart Safari and try adding to home screen again

**Want to update the app?**
- Replace the HTML file and refresh/reinstall

---

**Pro Tip**: You can have BOTH the portable pantry app AND the full web app running - they're independent and store data separately!
