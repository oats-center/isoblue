FROM node 

RUN mkdir /code
WORKDIR /code

COPY "./" "/code/"
RUN yarn install
RUN yarn run build

CMD ["yarn", "run", "start"]
