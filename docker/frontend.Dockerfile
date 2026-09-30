# Multi-stage Dockerfile for Local Research Agent React Frontend
FROM node:22-alpine AS build

WORKDIR /app

# Copy dependency specifications
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Lightweight production web server
FROM nginx:alpine-slim AS runtime

# Copy custom nginx configuration for SPA routing
RUN printf 'server {\n\
    listen 3000;\n\
    server_name localhost;\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html index.htm;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

# Copy build artifacts
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
