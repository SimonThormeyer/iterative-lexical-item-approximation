# Docker Image which is used as foundation to create
# a custom Docker Image with this Dockerfile
FROM node:14
 
# A directory within the virtualized Docker environment
# Becomes more relevant when using Docker Compose later
WORKDIR /usr/src/app
 
# Copies package.json and package-lock.json to Docker environment
COPY package*.json ./
 
# Installs all node packages
RUN yarn install

RUN yarn global add serve
 
# Copies everything over to Docker environment
COPY . .
 
 # Building app
RUN yarn build

# Uses port which is used by the actual application
EXPOSE 3000

RUN mkdir build/thesis && mv build/static build/thesis/static && mv build/manifest.json build/thesis/manifest.json 
 
# Finally runs the application
# CMD [ "yarn", "start" ]
CMD ["serve", "-s", "build", "-l", "3000"]