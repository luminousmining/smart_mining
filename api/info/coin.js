const express = require('express');
const router = express.Router();
const db = require('../common/database');

router.get('/:tag', async (req, res) => {
    const coinTag = req.params.tag;

    try {
        const result = await db.query(
            'SELECT * FROM coins WHERE tag=$1',
            [coinTag]
        );

        if (result.rows.length > 0) {
            const coinInfo = result.rows[0];
            res.json(coinInfo);
        } else {
            res.status(404).json({ error: `coin [${coinTag}] not found.` });
        }
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal error.' });
    }
});

module.exports = router;
