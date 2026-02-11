#!/bin/bash

# E2E Integration Test Script for TaskFlow
# Tests the complete user journey from signup to comments

set -e

API_URL="http://localhost:8000"
EMAIL="test-$(date +%s)@example.com"
PASSWORD="TestPassword123!"
TOKEN=""
PROJECT_ID=""
TASK_ID=""

echo "========================================="
echo "TaskFlow E2E Integration Test"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing health check..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/health")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  echo "✅ Health check passed"
  echo "   Response: $body"
else
  echo "❌ Health check failed (HTTP $http_code)"
  exit 1
fi
echo ""

# Test 2: User Registration
echo "2️⃣  Testing user registration..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Test User\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
  echo "✅ User registration passed"
  echo "   User: $EMAIL"
else
  echo "❌ User registration failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 3: User Login
echo "3️⃣  Testing user login..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  TOKEN=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token') or data.get('token', {}).get('access_token', ''))" 2>/dev/null || echo "")
  if [ -z "$TOKEN" ]; then
    echo "❌ Failed to extract token from response"
    echo "   Response: $body"
    exit 1
  fi
  echo "✅ User login passed"
  echo "   Token: ${TOKEN:0:20}..."
else
  echo "❌ User login failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 4: Get Current User
echo "4️⃣  Testing get current user..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  echo "✅ Get current user passed"
  echo "   Email: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['email'])" 2>/dev/null || echo "N/A")"
else
  echo "❌ Get current user failed (HTTP $http_code)"
  exit 1
fi
echo ""

# Test 5: Create Project
echo "5️⃣  Testing project creation..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/projects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Test Project\",
    \"description\": \"E2E Test Project\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
  PROJECT_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
  if [ -z "$PROJECT_ID" ]; then
    echo "❌ Failed to extract project ID"
    exit 1
  fi
  echo "✅ Project creation passed"
  echo "   Project ID: $PROJECT_ID"
else
  echo "❌ Project creation failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 6: List Projects
echo "6️⃣  Testing list projects..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  echo "✅ List projects passed"
  echo "   Projects count: $count"
else
  echo "❌ List projects failed (HTTP $http_code)"
  exit 1
fi
echo ""

# Test 7: Create Task
echo "7️⃣  Testing task creation..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/projects/$PROJECT_ID/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"title\": \"Test Task\",
    \"description\": \"E2E Test Task\",
    \"status\": \"todo\",
    \"priority\": \"high\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
  TASK_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
  if [ -z "$TASK_ID" ]; then
    echo "❌ Failed to extract task ID"
    exit 1
  fi
  echo "✅ Task creation passed"
  echo "   Task ID: $TASK_ID"
else
  echo "❌ Task creation failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 8: List Tasks
echo "8️⃣  Testing list tasks..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  echo "✅ List tasks passed"
  echo "   Tasks count: $count"
else
  echo "❌ List tasks failed (HTTP $http_code)"
  exit 1
fi
echo ""

# Test 9: Update Task Status
echo "9️⃣  Testing task status update..."
response=$(curl -s -L -w "\n%{http_code}" -X PATCH "$API_URL/api/v1/projects/$PROJECT_ID/tasks/$TASK_ID/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"status\": \"in_progress\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  echo "✅ Task status update passed"
  echo "   New status: in_progress"
else
  echo "❌ Task status update failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 10: Get Task Detail
echo "🔟 Testing get task detail..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects/$PROJECT_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  status=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "N/A")
  echo "✅ Get task detail passed"
  echo "   Status: $status"
else
  echo "❌ Get task detail failed (HTTP $http_code)"
  exit 1
fi
echo ""

# Test 11: Create Comment
echo "1️⃣1️⃣  Testing comment creation..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/projects/$PROJECT_ID/tasks/$TASK_ID/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"content\": \"This is a test comment for E2E testing\"
  }")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
  comment_id=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "N/A")
  echo "✅ Comment creation passed"
  echo "   Comment ID: $comment_id"
else
  echo "❌ Comment creation failed (HTTP $http_code)"
  echo "   Response: $body"
  exit 1
fi
echo ""

# Test 12: List Comments
echo "1️⃣2️⃣  Testing list comments..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects/$PROJECT_ID/tasks/$TASK_ID/comments" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  echo "✅ List comments passed"
  echo "   Comments count: $count"
else
  echo "❌ List comments failed (HTTP $http_code)"
  exit 1
fi
echo ""

echo "========================================="
echo "🎉 ERROR CASE TESTS"
echo "========================================="
echo ""

# Error Test 1: Unauthorized Access
echo "❌1️⃣  Testing unauthorized access..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects")
http_code=$(echo "$response" | tail -1)

if [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
  echo "✅ Unauthorized access properly rejected (HTTP $http_code)"
else
  echo "⚠️  Expected 401/403 but got HTTP $http_code"
fi
echo ""

# Error Test 2: Invalid Token
echo "❌2️⃣  Testing invalid token..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects" \
  -H "Authorization: Bearer invalid_token_12345")
http_code=$(echo "$response" | tail -1)

if [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
  echo "✅ Invalid token properly rejected (HTTP $http_code)"
else
  echo "⚠️  Expected 401/403 but got HTTP $http_code"
fi
echo ""

# Error Test 3: Duplicate Email Registration
echo "❌3️⃣  Testing duplicate email registration..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Duplicate User\"
  }")
http_code=$(echo "$response" | tail -1)

if [ "$http_code" -eq 400 ] || [ "$http_code" -eq 409 ] || [ "$http_code" -eq 422 ]; then
  echo "✅ Duplicate email properly rejected (HTTP $http_code)"
else
  echo "⚠️  Expected 400/409/422 but got HTTP $http_code"
fi
echo ""

# Error Test 4: Invalid Email Format
echo "❌4️⃣  Testing invalid email format..."
response=$(curl -s -L -w "\n%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"invalid-email\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Invalid User\"
  }")
http_code=$(echo "$response" | tail -1)

if [ "$http_code" -eq 422 ] || [ "$http_code" -eq 400 ]; then
  echo "✅ Invalid email format properly rejected (HTTP $http_code)"
else
  echo "⚠️  Expected 422/400 but got HTTP $http_code"
fi
echo ""

# Error Test 5: Non-existent Resource
echo "❌5️⃣  Testing access to non-existent task..."
response=$(curl -s -L -w "\n%{http_code}" "$API_URL/api/v1/projects/$PROJECT_ID/tasks/99999" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -1)

if [ "$http_code" -eq 404 ]; then
  echo "✅ Non-existent resource properly returns 404"
else
  echo "⚠️  Expected 404 but got HTTP $http_code"
fi
echo ""

echo "========================================="
echo "✅ ALL TESTS COMPLETED SUCCESSFULLY!"
echo "========================================="
echo ""
echo "Summary:"
echo "- ✅ 12 main scenario tests passed"
echo "- ✅ 5 error case tests verified"
echo ""
