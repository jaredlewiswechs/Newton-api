# Quick Deployment Guide

## What Was Fixed

Three critical bugs preventing apps from working on https://newton-api.onrender.com/:

1. **Error 500 in Jester API** - Fixed ValueError when no language specified
2. **Error 404 for apps** - Fixed mount path mismatches 
3. **Plain text homepage** - Fixed Content-Type header

## Deploy Now

### 1. Merge This PR
```bash
# Merge to main branch - Render will auto-deploy
git checkout main
git merge copilot/fix-apps-error-405
git push origin main
```

### 2. Wait for Render Deployment
- Watch Render dashboard for deployment status
- Should complete in 2-5 minutes

### 3. Test URLs

Test these URLs immediately after deployment:

#### Root Page
```
https://newton-api.onrender.com/
```
**Expected**: Dark UI with app icons (Newton Phone interface)
**NOT**: Plain HTML text

#### Jester Analyzer
```
https://newton-api.onrender.com/jester-analyzer
```
**Test**: 
1. Paste this code:
```python
def test(x):
    if x > 0:
        return True
```
2. Click "Analyze Code"
3. Should show extracted constraints (NOT error 405 or 500)

#### Newton Demo
```
https://newton-api.onrender.com/newton-demo
```
**Test**:
1. Click "Analyze Code" tab
2. Paste any code sample
3. Click "Analyze with Jester"
4. Should work (NOT "string unexpected" error)

### 4. API Health Check
```bash
# Quick API test
curl https://newton-api.onrender.com/health
curl https://newton-api.onrender.com/jester/info
```

Both should return JSON (not errors).

## Troubleshooting

### If Deployment Fails
Check Render logs for:
- Import errors
- Missing dependencies
- Port binding issues

### If Apps Still Don't Work
1. Clear browser cache
2. Check browser console for errors
3. Verify API endpoint URLs in Network tab

### If You Need to Rollback
```bash
git revert HEAD
git push origin main
```

## Success Criteria

✅ All three URLs load without errors
✅ Jester can analyze code
✅ Demo page interactive features work
✅ No 404, 405, or 500 errors
✅ Homepage shows styled UI (not plain text)

## Support

If issues persist after deployment:
- Check DEPLOYMENT_FIX_SUMMARY.md for detailed info
- Review Render logs
- Test API endpoints directly with curl

---

**Ready to deploy!** All changes are minimal, tested, and secure (CodeQL: 0 alerts).
