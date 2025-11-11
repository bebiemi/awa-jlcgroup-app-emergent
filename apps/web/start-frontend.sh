#!/bin/bash
# Custom frontend startup script
# Forces Vite to use port 3001 regardless of environment variable
cd /app/apps/web
yarn vite --host 0.0.0.0 --port 3001
