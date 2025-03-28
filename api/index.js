const express = require('express');
const app = express();
const port = 3000;

const routeInfoCoins = require('./info/coins');
const routeInfoCoin = require('./info/coin');
const routeInfoGpuSpecs = require('./info/gpu_specs')
const routeInfoGpuSpec = require('./info/gpu_spec')
const routeProfileEmission = require('./profile/emission');
const routeProfileHashUsd = require('./profile/hash_usd');
const routeProfileUsdSecond = require('./profile/usd_sec');
const routeProfileMarketCap = require('./profile/market_cap');
const routeProfileNetworkHasrate = require('./profile/network_hashrate');


app.use((req, res, next) => {
    const apiKey = req.query.api_key;
    if (!apiKey) {
        return res.status(400).json({ error: 'missing api_key!' });
    }
    next();
});

app.use('/info/coins', routeInfoCoins);
app.use('/info/coin', routeInfoCoin);
app.use('/info/gpu_specs',routeInfoGpuSpecs)
app.use('/info/gpu_spec',routeInfoGpuSpec)
app.use('/profile/emission', routeProfileEmission);
app.use('/profile/hash_usd', routeProfileHashUsd);
app.use('/profile/usd_sec', routeProfileUsdSecond);
app.use('/profile/market_cap', routeProfileMarketCap);
app.use('/profile/network_hashrate', routeProfileNetworkHasrate);

app.listen(port, () => {
    console.log(`Run at http://0.0.0.0:${port}`);
});
