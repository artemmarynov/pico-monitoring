FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# --host is required for Vite to be accessible outside the container
CMD ["npm", "run", "dev", "--", "--host"]