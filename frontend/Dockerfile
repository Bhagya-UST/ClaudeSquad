FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Use ci for faster, more reliable installs (requires package-lock.json)
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

COPY . .

# Optimize build: disable source maps, parallel build, CI mode
ENV GENERATE_SOURCEMAP=false \
    CI=true \
    NODE_OPTIONS="--max-old-space-size=3072"

RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
