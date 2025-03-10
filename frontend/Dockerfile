FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./

COPY . .
# RUN npm run build
RUN npm install --global http-server

CMD ["cp", "-r", "/app/build/.", "/static/"]
