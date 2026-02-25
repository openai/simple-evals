FROM node:20-alpine

WORKDIR /app

# 复制 package.json
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
