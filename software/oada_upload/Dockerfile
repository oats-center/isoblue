FROM node as builder

RUN mkdir /code
WORKDIR /code

COPY package*.json yarn.lock tsconfig.json ./
RUN ls && yarn install
COPY "./" "/code/"

RUN yarn run build


FROM node:slim as runtime

RUN mkdir /code
WORKDIR /code

COPY --from=builder "/code/src/" "/code/src/"
COPY --from=builder "/code/node_modules/" "/code/node_modules/"
COPY --from=builder "/code/package.json" "/code/package.json"
COPY --from=builder "/code/tsconfig.json" "/code/tsconfig.json"

CMD ["yarn", "run", "start"]
