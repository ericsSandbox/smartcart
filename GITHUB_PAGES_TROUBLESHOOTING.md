# GitHub Pages Deployment Troubleshooting Guide

## What Was Changed

The GitHub Actions workflow has been improved to be more reliable and include better error handling:

### Key Improvements
1. **Concurrency Control** - Prevents multiple deployments from conflicting
2. **Better Logging** - Shows exactly what files are being deployed
3. **Artifact Verification** - Checks that critical files exist before deploying
4. **Longer Wait Time** - Gives artifact storage time to process (10 seconds)
5. **Explicit Token** - Passes GitHub token explicitly to deploy action
6. **Better Error Messages** - If files are missing, the job fails with clear feedback

---

## Common Issues & Solutions

### Issue 1: "Cannot find any run with github.run_id"
**Cause:** Artifact upload failed or deployment tried to access artifact before it was ready
**Solution:** 
- The improved workflow now waits 10 seconds before deploying
- If still failing, check: Does `index.html` exist in root? (It should)
- Check: Is `.nojekyll` file present? (Required for custom Jekyll settings)

### Issue 2: "Failed to create deployment (status: 404)"
**Cause:** GitHub Pages not properly configured or artifact missing
**Solution:**
- Go to: https://github.com/ericsSandbox/smartcart/settings/pages
- Verify "Source" is set to "Deploy from a branch"
- Verify "Branch" is set to "main" with "/(root)" folder
- Check repo has "public" branch or Pages is configured correctly

### Issue 3: "Getting signed artifact URL failed"
**Cause:** Artifact management service timeout or temporary GitHub outage
**Solution:**
- This is often temporary - try triggering workflow again via "Run workflow" button
- The improved workflow includes 10-second wait to help prevent this

### Issue 4: Workflow runs but pages don't update
**Cause:** Cache, browser cache, or Pages deployment delay
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete / Cmd+Shift+Delete)
- Wait 30 seconds for Pages to propagate
- Check: https://ericssandbox.github.io/smartcart/ in private/incognito window
- Check workflow logs - look for "✅ Setup complete" to see if all files copied

---

## How to Manually Trigger Deployment

If automatic deployment fails:

1. Go to: https://github.com/ericsSandbox/smartcart/actions
2. Click "Deploy to GitHub Pages" workflow on left
3. Click "Run workflow" button
4. Select "main" branch
5. Click green "Run workflow" button
6. Watch the logs in real-time

---

## What the New Workflow Does

```
1. Checkout code from repository
   ↓
2. Setup GitHub Pages environment
   ↓
3. Create _site directory with:
   - index.html (main app)
   - .nojekyll (disable Jekyll processing)
   - public/* (if exists)
   - data/* (if exists)
   - docs/* (if exists)
   - *.md files (documentation)
   ↓
4. Verify critical files exist:
   ✓ index.html present
   ✓ .nojekyll present
   ✓ Total file count reported
   ↓
5. Upload _site as artifact
   ↓
6. Wait 10 seconds for artifact processing
   ↓
7. Deploy artifact to GitHub Pages
   ↓
8. Website live at: https://ericsSandbox.github.io/smartcart/
```

---

## Files Required for Deployment

Your repository needs these files in root:
- ✅ `index.html` - Main application (required)
- ✅ `.nojekyll` - Empty file that disables Jekyll (required for GitHub Pages)
- ✅ `.github/workflows/deploy.yml` - Workflow file (already exists)

These are optional but helpful:
- ✅ `public/` - Directory with static assets
- ✅ `docs/` - Directory with documentation
- ✅ `data/` - Directory with data files
- ✅ `*.md` - Markdown documentation files

---

## Debugging Steps

### Step 1: Check if GitHub Pages is Enabled
```
Go to: https://github.com/ericsSandbox/smartcart/settings/pages
Look for: "GitHub Pages is currently enabled from main branch"
```

### Step 2: Check Workflow Logs
```
Go to: https://github.com/ericsSandbox/smartcart/actions
Click latest "Deploy to GitHub Pages" run
Click "build-and-deploy" job
Read the logs - look for:
- "✅ Setup complete"
- "✅ index.html found"
- "✅ .nojekyll found"
```

### Step 3: Manual File Check
```bash
cd /home/eric/Projects/SmartCart
ls -la | grep -E "index.html|.nojekyll"
# Should see both files

cat .nojekyll
# Should be empty file
```

### Step 4: Test Deployment Locally
```bash
# Simulate what GitHub Actions does
mkdir -p _site
cp index.html _site/
cp .nojekyll _site/
ls -lah _site/

# Check files are there
```

---

## If Problem Persists

### Nuclear Option: Re-enable Pages
1. Go to: https://github.com/ericsSandbox/smartcart/settings/pages
2. Under "Source", select "None"
3. Wait 30 seconds
4. Select "Deploy from a branch"
5. Select branch "main" and folder "/(root)"
6. Save
7. Push a commit to trigger workflow
8. Wait 2-3 minutes for Pages to rebuild

### Check Git Repository Health
```bash
cd /home/eric/Projects/SmartCart

# Verify .nojekyll is tracked
git status | grep nojekyll

# Make sure it's committed
git log --oneline --all -- .nojekyll | head -1

# If missing, add it:
git add .nojekyll
git commit -m "Ensure .nojekyll is tracked"
git push origin main
```

---

## Workflow Status Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| ✅ All checks pass | Deployment successful | Check live site in 30 seconds |
| ⚠️ Warning (yellow) | Minor issue, still deployed | Check logs for warnings |
| ❌ Failed (red) | Deployment failed | Check error messages in logs |
| 🟡 Running (orange) | Deployment in progress | Wait for completion |

---

## Performance Notes

- **First deployment**: 2-3 minutes
- **Subsequent deployments**: 30-60 seconds
- **Pages cache propagation**: Up to 5 minutes
- **Browser cache clearing needed**: Sometimes

---

## Files Included in Deployment

The improved workflow now deploys:
```
_site/
├── index.html (SmartCart app)
├── .nojekyll (Pages configuration)
├── *.md (Documentation files)
├── public/* (Static assets)
├── docs/* (Documentation)
└── data/* (Data files)
```

All markdown documentation files are now accessible at:
- https://ericssandbox.github.io/smartcart/SMART_INVENTORY_FEATURES.md
- https://ericssandbox.github.io/smartcart/IMPROVEMENTS_V2_1_1.md
- etc.

---

## Quick Reference

**Site URL:** https://ericssandbox.github.io/smartcart/

**Settings:** https://github.com/ericsSandbox/smartcart/settings/pages

**Actions:** https://github.com/ericsSandbox/smartcart/actions

**Workflow File:** `.github/workflows/deploy.yml`

**Trigger New Deploy:** Go to Actions → Deploy to GitHub Pages → Run workflow → main branch

---

## Recent Changes (Commit b3cdcb8)

- Added concurrency control to prevent race conditions
- Improved logging with emoji indicators
- Added artifact verification step
- Increased wait time from 5 to 10 seconds
- Added explicit token passing
- Better error messages
- Now copies markdown documentation

These changes should significantly reduce deployment failures!
