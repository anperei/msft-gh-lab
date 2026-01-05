# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build


# Runtime stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration template (uses envsubst for runtime config)
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Expose port
EXPOSE 80

# Default backend URL (will be overridden by Container Apps env var)
ENV BACKEND_URL=http://backend

# Start nginx (nginx:alpine automatically processes templates in /etc/nginx/templates/)
CMD ["nginx", "-g", "daemon off;"]
