# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
# RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build
RUN npm install --global http-server
# CMD cp -r build result_build
CMD ["cp", "-r", "/app/build/.", "/static/"]
