-----------------------------------------------------------
DROP PROCEDURE IF EXISTS insert_pool;
DROP PROCEDURE IF EXISTS insert_pool_stats;


-----------------------------------------------------------
DROP TABLE IF EXISTS pools;
DROP TABLE IF EXISTS pool_stats;
DROP TABLE IF EXISTS pool_stats_history;


-----------------------------------------------------------
CREATE TABLE pools(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32),
    tag VARCHAR(32)
);
ALTER TABLE pools ADD CONSTRAINT unique_pool UNIQUE (name, tag);


-----------------------------------------------------------
CREATE TABLE pool_stats(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32),
    tag VARCHAR(32),
    block_height NUMERIC,
    mine_timestamp NUMERIC,
    difficulty NUMERIC,
    luck NUMERIC,
    block_status VARCHAR(32)
);
ALTER TABLE pool_stats ADD CONSTRAINT unique_pool_stats UNIQUE (name, tag, block_height, mine_timestamp);


-----------------------------------------------------------
CREATE PROCEDURE insert_pool(
    p_name VARCHAR(32),
    p_tag VARCHAR(32)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pools(
        name,
        tag
    ) VALUES (
        p_name,
        p_tag
    )
    ON CONFLICT (name, tag) DO NOTHING;
END;
$$;


-----------------------------------------------------------
CREATE PROCEDURE insert_pool_stats(
    p_name VARCHAR(32),
    p_tag VARCHAR(32),
    p_block_height NUMERIC,
    p_mine_timestamp NUMERIC,
    p_difficulty NUMERIC,
    p_luck NUMERIC,
    p_block_status VARCHAR(32)
)
LANGUAGE plpgsql
AS $$BEGIN
    INSERT INTO pool_stats(
        name,
        tag,
        block_height,
        mine_timestamp,
        difficulty,
        luck,
        block_status
    ) VALUES (
        p_name,
        p_tag,
        p_block_height,
        p_mine_timestamp,
        p_difficulty,
        p_luck,
        p_block_status
    )
    ON CONFLICT (name, tag, block_height, mine_timestamp) DO UPDATE
    SET block_height    = EXCLUDED.block_height,
        mine_timestamp  = EXCLUDED.mine_timestamp,
        difficulty      = EXCLUDED.difficulty,
        luck            = EXCLUDED.luck,
        block_status    = EXCLUDED.block_status;
END;
$$;
