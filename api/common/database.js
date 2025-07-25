const { db } = require('../common/config');
const { Pool } = require('pg');


const pool = new Pool({
    user: db.username,
    host: db.host,
    database: db.database,
    password: db.password,
    port: db.port,
});


const query = async (text, params) => {
    const client = await pool.connect();
    try {
        const res = await client.query(text, params);
        return res;
    } finally {
        client.release();
    }
};

module.exports = {
    query,
};
