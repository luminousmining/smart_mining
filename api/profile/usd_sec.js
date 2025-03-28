const express = require('express');
const router = express.Router();
const db = require('../common/database');

router.use(express.json())

router.get('/', async (req, res) => {
    const apiKey = req.query.api_key;

    try {
        const result = await db.query(
            `
            SELECT
                name,
                UPPER(tag) as tag,
                usd_sec
            FROM coins
            ORDER BY usd_sec DESC
            `
        );

        if (result.rows.length > 0) {
            res.json(result.rows);
        } else {
            res.status(404).json({ error: 'request fail!' });
        }
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal error!' });
    }
});

router.get('/coin', async (req, res) => {
    const apiKey = req.query.api_key;
    const dataList = req.body.data; 

    if (!Array.isArray(dataList) || dataList.length === 0) {
        return res.status(400).json({ error: 'Key "data" must be list not empty.' });
    }

    try {
        const result = await Promise.all(
            dataList.map(async (dataItem) => {
                const { tag, hashrate } = dataItem;

                const queryResult = await db.query(
                    `
                    SELECT
                        tag,
                        usd_sec,
                        (CAST($1 as NUMERIC) * CAST(100 as NUMERIC)) / network_hashrate AS worker_percent,
                        (
                            (
                                (
                                    (
                                        CAST($1 as NUMERIC) * CAST(100 as NUMERIC)
                                    ) / network_hashrate
                                ) * usd_sec
                            ) / 100
                        ) as usd_sec_rig
                    FROM coins
                    WHERE tag = $2
                    `, [hashrate, tag]
                );

                if (queryResult.rows.length > 0) {
                    const coinInfo = queryResult.rows[0];
                    return {
                        ...coinInfo
                    };
                } else {
                    return { error: `Coin with tag [${tag}] not found` };
                }
            })
        );

        res.json({ result });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal error!' });
    }
});

module.exports = router;
