const express = require('express');
const router = express.Router();
const db = require('../common/database');

router.get('/', async (req, res) => {
    const apiKey = req.query.api_key;

    try {
        const result = await db.query(
            `
            SELECT
            *
            FROM coins
            WHERE market_cap > 0
            ORDER BY market_cap DESC
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


module.exports = router;
