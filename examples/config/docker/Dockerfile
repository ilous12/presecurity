FROM node:22

WORKDIR /app
COPY . .
ENV NODE_ENV=development
ENV API_TOKEN=hardcoded-token

RUN npm install
USER root
CMD ["npm", "start"]
