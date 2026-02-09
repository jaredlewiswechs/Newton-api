# Quick Deployment Guide

**Updated: February 1, 2026**

## Deployment Platform

Newton is deployed on **Vercel** as a serverless application.

## Deploy Now

### 1. Push to GitHub

```bash
# Push changes to main branch
git checkout main
git push origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Vercel auto-detects `vercel.json` configuration
4. Click "Deploy"
5. Wait 1-2 minutes for deployment

### 3. Test All App URLs

Test these URLs immediately after deployment:

#### Root Page
```
https://your-project.vercel.app/
```
**Expected**: Dark UI with app icons (Newton Phone interface)
**NOT**: Plain HTML text

#### Core Apps
```
https://your-project.vercel.app/app (Newton Supercomputer)
https://your-project.vercel.app/teachers (Teacher's Aide)
https://your-project.vercel.app/builder (Interface Builder)
```

#### Development Tools
```
https://your-project.vercel.app/jester-analyzer (Jester Analyzer)
https://your-project.vercel.app/tinytalk-ide (TinyTalk IDE)
https://your-project.vercel.app/construct-studio (Construct Studio)
```

#### Demos & Games
```
https://your-project.vercel.app/newton-demo (Newton Demo)
https://your-project.vercel.app/games/gravity_wars (Gravity Wars)
```

#### Additional Apps
```
https://your-project.vercel.app/parccloud (ParcCloud)
```

### 4. Quick Functionality Tests

#### Jester Analyzer
1. Go to https://your-project.vercel.app/jester-analyzer
2. Paste this code:
```python
def test(x):
    if x > 0:
        return True
```
3. Click "Analyze Code"
4. Should show extracted constraints (NOT error 405 or 500)

#### Newton Demo
1. Go to https://your-project.vercel.app/newton-demo
2. Click "Analyze Code" tab
3. Paste any code sample
4. Click "Analyze with Jester"
5. Should work (NOT "string unexpected" error)

#### TinyTalk IDE
1. Go to https://your-project.vercel.app/tinytalk-ide
2. Should load IDE interface
3. Verify editor is functional

#### Construct Studio
1. Go to https://your-project.vercel.app/construct-studio
2. Should load studio interface
3. Verify UI elements render

#### Games
1. Go to https://your-project.vercel.app/games/gravity_wars
2. Should load game interface
3. Verify game renders

### 5. API Health Check
```bash
# Quick API test
curl https://your-project.vercel.app/health
curl https://your-project.vercel.app/jester/info
```

Both should return JSON (not errors).

## Troubleshooting

### If Deployment Fails
Check Vercel deployment logs for:
- Import errors
- Missing dependencies
- Module resolution issues

### If Apps Still Don't Work
1. Clear browser cache
2. Check browser console for errors
3. Verify API endpoint URLs in Network tab

### If You Need to Rollback
Use Vercel dashboard to rollback to a previous deployment.

## Success Criteria

✅ All URLs load without errors
✅ Jester can analyze code
✅ Demo page interactive features work
✅ No 404, 405, or 500 errors
✅ Homepage shows styled UI (not plain text)

## Support

If issues persist after deployment:
- Check APP_INVENTORY.md for detailed app info
- Review Vercel deployment logs
- Test API endpoints directly with curl

---

**Ready to deploy!** All changes are minimal, tested, and secure.
