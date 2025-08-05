DROP TABLE IF EXISTS coins;

DROP PROCEDURE IF EXISTS insert_coin;


CREATE TABLE coins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32),
    tag VARCHAR(32),
    algorithm VARCHAR(32),
    usd NUMERIC,
    usd_sec NUMERIC,
    difficulty NUMERIC,
    network_hashrate NUMERIC,
    hash_usd NUMERIC,
    emission_coin NUMERIC,
    emission_usd NUMERIC,
    market_cap NUMERIC
);
ALTER TABLE coins ADD CONSTRAINT unique_name UNIQUE (name);


CREATE PROCEDURE insert_coin(
    p_name VARCHAR(32),
    p_tag VARCHAR(32),
    p_algorithm VARCHAR(32),
    p_usd NUMERIC,
    p_usd_sec NUMERIC,
    p_difficulty NUMERIC,
    p_network_hashrate NUMERIC,
    p_hash_usd NUMERIC,
    p_emission_coin NUMERIC,
    p_emission_usd NUMERIC,
    p_market_cap NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO coins(
        name,
        tag,
        algorithm,
        usd,
        usd_sec,
        difficulty,
        network_hashrate,
        hash_usd,
        emission_coin,
        emission_usd,
        market_cap
    ) VALUES (
        p_name,
        p_tag,
        p_algorithm,
        p_usd,
        p_usd_sec,
        p_difficulty,
        p_network_hashrate,
        p_hash_usd,
        p_emission_coin,
        p_emission_usd,
        p_market_cap
    )
    ON CONFLICT (
        name
    ) DO UPDATE
    SET
        tag = EXCLUDED.tag,
        algorithm = EXCLUDED.algorithm,
        usd = EXCLUDED.usd,
        usd_sec = EXCLUDED.usd_sec,
        difficulty = EXCLUDED.difficulty,
        network_hashrate = EXCLUDED.network_hashrate,
        hash_usd = EXCLUDED.hash_usd,
        emission_coin = EXCLUDED.emission_coin,
        emission_usd = EXCLUDED.emission_usd,
        market_cap = EXCLUDED.market_cap;
END;
$$;
