# Stage 1: Base - Define base Node.js image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy dependency manifests
# Copying these first allows Docker to cache this layer if dependencies haven't changed
COPY package.json package-lock.json ./

# Install dependencies using npm ci for reproducible builds
# --omit=dev is not used here as we need devDependencies for building
RUN npm ci

# Stage 2: Builder - Build the Next.js application
FROM base AS builder
WORKDIR /app

# Copy installed dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . .

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
# This creates .next/standalone output due to next.config.ts setting
RUN npm run build

# Stage 3: Runner - Production runtime with minimal footprint
FROM base AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user and group for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy public assets (if any)
# Public files are served statically by Next.js
COPY --from=builder /app/public ./public

# Copy standalone output and static files with proper ownership
# Standalone mode includes only necessary dependencies
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port 3000
EXPOSE 3000

# Set runtime environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check to ensure the application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); })"

# Run the standalone Next.js server
CMD ["node", "server.js"]
