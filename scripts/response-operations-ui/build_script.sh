!#/usr/bin/env sh
node -v && npm -v
npm install --unsafe-perms
npm rebuild node-sass
npm run gulp build
