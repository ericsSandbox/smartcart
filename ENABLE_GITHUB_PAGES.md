# Enable GitHub Pages - Quick Setup

Your SmartCart app is ready to deploy! Follow these steps to enable GitHub Pages.

## 📋 Step-by-Step Instructions

### 1. Go to Repository Settings
- Visit: https://github.com/ericsSandbox/smartcart/settings/pages

### 2. Configure GitHub Pages Source
Look for the **"Pages"** section and configure:

**Option A: Simple (Recommended)**
- Source: **"Deploy from a branch"**
- Branch: **"main"**
- Folder: **"/ (root)"**
- Click **"Save"**

**Option B: Using GitHub Actions**
- Source: **"GitHub Actions"**
- This will use our automated deployment workflow

### 3. Wait for Deployment
- GitHub will process the deployment
- This usually takes 1-2 minutes
- You'll see a green checkmark when complete

### 4. Access Your App
Once deployed, your app will be live at:
```
https://ericsSandbox.github.io/smartcart/
```

## ✅ Verification

After enabling GitHub Pages:

1. Visit your GitHub Pages URL above
2. You should see the SmartCart app load
3. Try adding an item to verify it works
4. Data is saved locally in your browser

## 🔄 Automatic Updates

Once GitHub Pages is enabled:
- Any push to `main` automatically deploys
- The `deploy-simple.yml` workflow handles this
- You should see a green checkmark in Actions tab after each push

## 🆘 Troubleshooting

**Still not working?**
1. Check your repository visibility is **Public** (GitHub Pages requires this)
2. Go to Settings → General → Visibility → make sure it's **Public**
3. Verify Pages settings again
4. Check the "Actions" tab for any workflow errors

**URL is different?**
- If your repo is NOT at `/smartcart`, the URL will be different
- Check your actual URL in the Pages settings

## 📚 More Help

- GitHub Pages Docs: https://docs.github.com/en/pages
- Repository: https://github.com/ericsSandbox/smartcart
- README: https://github.com/ericsSandbox/smartcart/blob/main/README.md
