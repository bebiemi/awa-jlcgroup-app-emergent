# Development Dockerfile for React Frontend
FROM node:20-alpine

# Set environment variables
ENV NODE_ENV=development

WORKDIR /app

# Install dependencies
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy application code
COPY . .

EXPOSE 5173

# Run Vite dev server with hot-reload
CMD ["yarn", "dev", "--host", "0.0.0.0"]
