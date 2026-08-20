# ── Stage 1: Build ─────────────────────────────────────────────────────────────
FROM node:18-alpine AS builder

WORKDIR /app

# Accept API URL as a build-time argument so it is baked into the bundle
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm ci --silent

COPY . .
RUN npm run build

# ── Stage 2: Serve ─────────────────────────────────────────────────────────────
FROM nginx:stable-alpine AS serve

# Copy static build output from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
