#!/bin/bash
# Newton Interface Builder - Cloudflare Pages Deployment
# Usage: CLOUDFLARE_API_TOKEN=your_token ./deploy.sh

set -e

echo "🔧 Newton Interface Builder - Deploying to Cloudflare Pages..."

# Check for API token
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ CLOUDFLARE_API_TOKEN not set"
    echo ""
    echo "Option 1: Set token and re-run"
    echo "  export CLOUDFLARE_API_TOKEN=your_token_here"
    echo "  ./deploy.sh"
    echo ""
    echo "Option 2: Manual upload at Cloudflare Dashboard"
    echo "  1. Go to https://pages.cloudflare.com"
    echo "  2. Click 'Create a project' → 'Direct Upload'"
    echo "  3. Upload the 'interface-builder' folder"
    echo "  4. Your site deploys at: https://newton-interface-builder.pages.dev"
    echo ""
    exit 1
fi

# Deploy
echo "📦 Deploying to Cloudflare Pages..."
npx wrangler pages deploy . --project-name=newton-interface-builder

echo ""
echo "✅ Deployment complete!"
echo "🌐 Live at: https://newton-interface-builder.pages.dev"
echo ""
echo "🔗 Newton Interface Builder Features:"
echo "   • 7 templates (dashboard, form, settings, etc.)"
echo "   • 30 components (buttons, inputs, cards, etc.)"
echo "   • Multiple output formats (JSON, JSX, HTML)"
echo "   • Verified UI generation via Newton Supercomputer"
