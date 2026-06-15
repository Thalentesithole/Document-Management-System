#!/bin/bash
set -e

echo "Starting Production Validation..."

FRONTEND_URL=${FRONTEND_URL:-"https://app.yourdomain.com"}
BACKEND_URL=${BACKEND_URL:-"https://api.yourdomain.com"}

echo "1. Checking Frontend Availability..."
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $FRONTEND_URL)
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Frontend is up ($HTTP_STATUS)"
else
    echo "❌ Frontend check failed ($HTTP_STATUS)"
    exit 1
fi

echo "2. Checking Backend Health Probes..."
for probe in health ready live; do
    PROBE_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $BACKEND_URL/$probe)
    if [ "$PROBE_STATUS" -eq 200 ]; then
        echo "✅ Backend /$probe is up"
    else
        echo "❌ Backend /$probe failed ($PROBE_STATUS)"
        exit 1
    fi
done

echo "3. Checking HTTPS Enforcement..."
HTTP_REDIRECT=$(curl -o /dev/null -s -w "%{http_code}\n" http://${FRONTEND_URL#*://})
if [ "$HTTP_REDIRECT" -eq 301 ] || [ "$HTTP_REDIRECT" -eq 308 ]; then
    echo "✅ HTTPS Redirection active"
else
    echo "⚠️ HTTPS Redirection might not be active at origin (Status: $HTTP_REDIRECT)"
fi

echo "4. Checking Security Headers..."
HEADERS=$(curl -s -I $FRONTEND_URL)
if echo "$HEADERS" | grep -iq "Strict-Transport-Security"; then
    echo "✅ HSTS header present"
else
    echo "❌ Missing HSTS header"
fi

echo "All basic infrastructure checks passed! 🚀"
echo "Next steps: Perform manual functional tests (Auth, Uploads, Reports, PDF Exports)."
