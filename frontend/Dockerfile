# ============================================
# LeadFlow Frontend — Multi-stage Dockerfile
# ============================================

# ─────────────────────────────────────────────────────────────
# STAGE 1: Build the React app with Vite
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# ── Install dependencies (cached layer) ──────────────────────────────────────
COPY package*.json ./
RUN npm ci

# ── Copy source and build ────────────────────────────────────────────────────
COPY . .

# ── Vite build args (passed at build time) ───────────────────────────────────
# The API URL is baked into the static build
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ─────────────────────────────────────────────────────────────
# STAGE 2: Serve with Nginx
# ─────────────────────────────────────────────────────────────
FROM nginx:alpine

# ── Copy built static files from builder stage ───────────────────────────────
COPY --from=builder /app/dist /usr/share/nginx/html

# ── Copy custom Nginx configuration ──────────────────────────────────────────
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ── Expose Nginx port ────────────────────────────────────────────────────────
EXPOSE 80

# ── Healthcheck ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# ── Start Nginx in foreground ────────────────────────────────────────────────
CMD ["nginx", "-g", "daemon off;"]