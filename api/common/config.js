const fs = require('fs');
const path = require('path');

const configPath = path.join(process.cwd(), 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

module.exports = config;
