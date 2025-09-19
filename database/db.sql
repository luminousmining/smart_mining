DROP PROCEDURE IF EXISTS insert_pool;
DROP PROCEDURE IF EXISTS insert_hardware_mining;
DROP PROCEDURE IF EXISTS insert_hardware;
DROP PROCEDURE IF EXISTS insert_coin;

DROP TABLE IF EXISTS pools;
DROP TABLE IF EXISTS hardware_mining;
DROP TABLE IF EXISTS hardware;
DROP TABLE IF EXISTS coins;

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
ALTER TABLE coins ADD CONSTRAINT unique_coin_name UNIQUE (name);

CREATE TABLE hardware (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32)
);
ALTER TABLE hardware ADD CONSTRAINT unique_hardware_name UNIQUE (name);

CREATE TABLE hardware_mining (
    id SERIAL PRIMARY KEY,
    hardware_id INTEGER NOT NULL REFERENCES hardware(id) ON DELETE CASCADE,
    algo VARCHAR(32),
    hashrate NUMERIC,
    power NUMERIC
);
ALTER TABLE hardware_mining ADD CONSTRAINT unique_hardware_algo UNIQUE (hardware_id, algo);

CREATE TABLE pools(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32),
    website VARCHAR(64),
    founded NUMERIC,
    tag VARCHAR(32),
    algorithm VARCHAR(32),
    anonymous BOOLEAN,
    registration BOOLEAN,
    fee NUMERIC
);
ALTER TABLE pools ADD CONSTRAINT unique_pool UNIQUE (name, tag, algorithm);

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
    ON CONFLICT (name) DO UPDATE
    SET tag               = EXCLUDED.tag,
        algorithm         = EXCLUDED.algorithm,
        usd               = EXCLUDED.usd,
        usd_sec           = EXCLUDED.usd_sec,
        difficulty        = EXCLUDED.difficulty,
        network_hashrate  = EXCLUDED.network_hashrate,
        hash_usd          = EXCLUDED.hash_usd,
        emission_coin     = EXCLUDED.emission_coin,
        emission_usd      = EXCLUDED.emission_usd,
        market_cap        = EXCLUDED.market_cap;
END;
$$;

CREATE PROCEDURE insert_hardware(
    p_name VARCHAR(32)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO hardware(
        name
    ) VALUES (
        p_name
    )
    ON CONFLICT (name) DO UPDATE
    SET name = EXCLUDED.name;
END;
$$;

CREATE PROCEDURE insert_pool(
    p_name VARCHAR(32),
    p_website VARCHAR(64),
    p_founded NUMERIC,
    p_tag VARCHAR(32),
    p_algorithm VARCHAR(32),
    p_anonymous BOOLEAN,
    p_registration BOOLEAN,
    p_fee NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pools(
        name,
        website,
        founded,
        tag,
        algorithm,
        anonymous,
        registration,
        fee
    ) VALUES (
        p_name,
        p_website,
        p_founded,
        p_tag,
        p_algorithm,
        p_anonymous,
        p_registration,
        p_fee
    )
    ON CONFLICT (name, tag, algorithm) DO UPDATE
    SET website         = EXCLUDED.website,
        founded         = EXCLUDED.founded,
        anonymous       = EXCLUDED.anonymous,
        registration    = EXCLUDED.registration,
        fee             = EXCLUDED.fee;
END;
$$;

CREATE PROCEDURE insert_hardware_mining(
    p_hardware_id INTEGER,
    p_algo VARCHAR(32),
    p_hashrate NUMERIC,
    p_power NUMERIC
)
LANGUAGE plpgsql
AS 
$$

BEGIN
    INSERT INTO hardware_mining(
        hardware_id,
        algo,
        hashrate,
        power
    ) VALUES (
        p_hardware_id,
        p_algo,
        p_hashrate,
        p_power
    )
    ON CONFLICT (hardware_id, algo) DO UPDATE
    SET hashrate = EXCLUDED.hashrate,
        algo     = EXCLUDED.algo,
        power    = EXCLUDED.power;
END;
$$;
