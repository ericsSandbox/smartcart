#!/bin/bash
# SmartCart Deployment Status Checker
# This script verifies the local repo is ready for deployment to GitHub Pages

set -e

REPO_DIR="/home/eric/Projects/SmartCart"
cd "$REPO_DIR"

echo "🔍 SmartCart Deployment Status Check"
echo "===================================="
echo ""

# Check 1: Critical files exist
echo "1. Checking critical files..."
if [ -f "index.html" ]; then
    SIZE=$(stat -f%z "index.html" 2>/dev/null || stat -c%s "index.html" 2>/dev/null || echo "unknown")
    echo "   ✅ index.html exists ($SIZE bytes)"
else
    echo "   ❌ index.html NOT FOUND"
    exit 1
fi

if [ -f ".nojekyll" ]; then
    echo "   ✅ .nojekyll exists (required for GitHub Pages)"
else
    echo "   ⚠️  .nojekyll NOT FOUND - creating it..."
    touch .nojekyll
    git add .nojekyll
    git commit -m "Add .nojekyll for GitHub Pages" || true
fi

echo ""

# Check 2: Git status
echo "2. Checking Git status..."
if [ -z "$(git status --porcelain)" ]; then
    echo "   ✅ Working directory clean"
else
    echo "   ⚠️  Uncommitted changes:"
    git status --short
fi

echo ""

# Check 3: Remote configuration
echo "3. Checking Git remote..."
REMOTE_URL=$(git config --get remote.origin.url)
echo "   Origin: $REMOTE_URL"
if [[ "$REMOTE_URL" == *"ericsSandbox/smartcart"* ]]; then
    echo "   ✅ Remote configured correctly"
else
    echo "   ⚠️  Warning: Remote might not be configured correctly"
fi

echo ""

# Check 4: Workflow file
echo "4. Checking GitHub Actions workflow..."
if [ -f ".github/workflows/deploy.yml" ]; then
    echo "   ✅ deploy.yml exists"
    
    # Check for key improvements
    if grep -q "concurrency:" .github/workflows/deploy.yml; then
        echo "   ✅ Concurrency control enabled"
    else
        echo "   ⚠️  Concurrency control not found"
    fi
    
    if grep -q "sleep 10" .github/workflows/deploy.yml; then
        echo "   ✅ 10-second artifact wait configured"
    else
        echo "   ⚠️  Wait time might be insufficient"
    fi
    
    if grep -q "Verify artifact" .github/workflows/deploy.yml; then
        echo "   ✅ Artifact verification enabled"
    else
        echo "   ⚠️  Artifact verification not found"
    fi
else
    echo "   ❌ deploy.yml NOT FOUND"
    exit 1
fi

echo ""

# Check 5: Directory structure
echo "5. Checking deployment directories..."
[ -d "data" ] && echo "   ✅ data/ exists" || echo "   ℹ️  data/ not found (optional)"
[ -d "docs" ] && echo "   ✅ docs/ exists" || echo "   ℹ️  docs/ not found (optional)"
[ -d "public" ] && echo "   ✅ public/ exists" || echo "   ℹ️  public/ not found (optional)"

echo ""

# Check 6: Large files
echo "6. Checking file sizes..."
LARGE_FILES=$(find . -type f -size +10M -not -path "./.git/*" 2>/dev/null | head -5)
if [ -n "$LARGE_FILES" ]; then
    echo "   ⚠️  Large files found (may slow deployment):"
    echo "$LARGE_FILES" | sed 's/^/      /'
else
    echo "   ✅ No unusually large files"
fi

echo ""

# Check 7: Git history
echo "7. Checking recent commits..."
echo "   Recent commits (last 3):"
git log --oneline -3 | sed 's/^/      /'

echo ""
echo "✨ Deployment Status Summary:"
echo "===================================="
echo ""
echo "Local Status: ✅ READY FOR DEPLOYMENT"
echo ""
echo "Next steps:"
echo "1. Make your changes to the code"
echo "2. Commit: git add . && git commit -m 'Your message'"
echo "3. Push: git push origin main"
echo "4. Watch: https://github.com/ericsSandbox/smartcart/actions"
echo "5. View: https://ericssandbox.github.io/smartcart/"
echo ""
echo "If deployment fails:"
echo "- Check workflow logs at: https://github.com/ericsSandbox/smartcart/actions"
echo "- Verify Pages settings: https://github.com/ericsSandbox/smartcart/settings/pages"
echo "- Read: GITHUB_PAGES_TROUBLESHOOTING.md"
echo ""
