#!/bin/bash

# Migration Script: Replace Hardcoded IAM Values with Constants
# This script helps identify files that need to be refactored

echo "🔍 IAM Constants Migration Helper"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend hardcoded values
echo -e "${BLUE}Searching for hardcoded values in Backend...${NC}"
echo ""

echo -e "${YELLOW}1. Hardcoded Groups (grp.*)${NC}"
grep -r "\"grp\\.candidat\"\|\"grp\\.interim\"\|\"grp\\.company\"\|\"grp\\.collaborateur\"\|\"grp\\.admin\"\|\"grp\\.super_admin\"" \
  /app/auth-microservice \
  --include="*.py" \
  --exclude-dir=__pycache__ \
  | grep -v "iam_constants.py" \
  | grep -v "test_iam_constants_sync.py" \
  | awk -F: '{print $1}' \
  | sort -u \
  | while read file; do
    count=$(grep -c "\"grp\\." "$file" 2>/dev/null || echo 0)
    echo -e "  ${RED}→${NC} $file (${count} occurrences)"
  done

echo ""
echo -e "${YELLOW}2. Hardcoded Roles (role.*)${NC}"
grep -r "\"role\\.candidat\"\|\"role\\.interim\"\|\"role\\.company\"\|\"role\\.collaborateur\"\|\"role\\.admin\"\|\"role\\.super_admin\"" \
  /app/auth-microservice \
  --include="*.py" \
  --exclude-dir=__pycache__ \
  | grep -v "iam_constants.py" \
  | awk -F: '{print $1}' \
  | sort -u \
  | while read file; do
    count=$(grep -c "\"role\\." "$file" 2>/dev/null || echo 0)
    echo -e "  ${RED}→${NC} $file (${count} occurrences)"
  done

echo ""
echo -e "${YELLOW}3. Hardcoded User Roles (candidat, interim, etc.)${NC}"
grep -r "\"candidat\"\|\"interim\"\|\"company\"\|\"collaborateur\"" \
  /app/auth-microservice \
  --include="*.py" \
  --exclude-dir=__pycache__ \
  | grep -v "iam_constants.py" \
  | grep -v "test_iam_constants_sync.py" \
  | grep -v "comment\|description\|label" \
  | awk -F: '{print $1}' \
  | sort -u \
  | while read file; do
    count=$(grep -c "\"candidat\"\|\"interim\"\|\"company\"\|\"collaborateur\"" "$file" 2>/dev/null || echo 0)
    echo -e "  ${RED}→${NC} $file (${count} occurrences)"
  done

echo ""
echo -e "${BLUE}Searching for hardcoded values in Frontend...${NC}"
echo ""

echo -e "${YELLOW}4. Hardcoded String Roles in TypeScript${NC}"
grep -r "'candidat'\|'interim'\|'company'\|'collaborateur'\|'admin'\|'super_admin'" \
  /app/apps/web/src \
  --include="*.tsx" \
  --include="*.ts" \
  | grep -v "iamConstants.ts" \
  | grep -v "node_modules" \
  | awk -F: '{print $1}' \
  | sort -u \
  | while read file; do
    count=$(grep -c "'candidat'\|'interim'\|'company'" "$file" 2>/dev/null || echo 0)
    echo -e "  ${RED}→${NC} $file (${count} occurrences)"
  done

echo ""
echo -e "${YELLOW}5. Hardcoded Groups (grp.*) in TypeScript${NC}"
grep -r "'grp\\.candidat'\|'grp\\.interim'\|'grp\\.company'\|'grp\\.collaborateur'" \
  /app/apps/web/src \
  --include="*.tsx" \
  --include="*.ts" \
  | grep -v "iamConstants.ts" \
  | awk -F: '{print $1}' \
  | sort -u \
  | while read file; do
    count=$(grep -c "'grp\\." "$file" 2>/dev/null || echo 0)
    echo -e "  ${RED}→${NC} $file (${count} occurrences)"
  done

echo ""
echo -e "${GREEN}=================================="
echo -e "Migration Helper Complete${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Review the files listed above"
echo "2. Import constants: from awana_auth.core.iam_constants import IAMGroups (backend)"
echo "3. Import constants: import { IAMGroups } from '@/constants/iamConstants' (frontend)"
echo "4. Replace hardcoded values with constants"
echo "5. Run: python /app/scripts/test_iam_constants_sync.py"
echo ""
