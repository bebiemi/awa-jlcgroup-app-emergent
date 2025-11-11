#!/bin/bash
# Custom frontend startup script
# Forces Vite to use port 3001 regardless of environment variable
cd /app/apps/web
PORT=3001 yarn start
