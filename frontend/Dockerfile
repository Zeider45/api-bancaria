FROM node:20-alpine

WORKDIR /app

# Build-time env (optional). Useful because Next.js bakes NEXT_PUBLIC_* at build.
ARG NEXT_PUBLIC_API_URL
ARG INTERNAL_API_URL
ARG NEXTAUTH_URL

ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV INTERNAL_API_URL=${INTERNAL_API_URL}
ENV NEXTAUTH_URL=${NEXTAUTH_URL}

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]