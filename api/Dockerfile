FROM node:18

WORKDIR /app

COPY package*.json ./
COPY profile ./profile
COPY common ./common
COPY info ./info
COPY config.json .
COPY index.js .

RUN npm install --production

EXPOSE 3000

CMD ["npm", "start"]
