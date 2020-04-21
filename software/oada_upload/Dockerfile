FROM node
#ENV NPM_CONFIG_LOGLEVEL info

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

RUN mkdir /code
WORKDIR /code

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "oada_upload.js" ]
