-----------------------------------------------------------
DROP PROCEDURE IF EXISTS insert_hardware_mining;
DROP PROCEDURE IF EXISTS insert_hardware;

-----------------------------------------------------------
DROP TABLE IF EXISTS hardware_mining;
DROP TABLE IF EXISTS hardware;


-----------------------------------------------------------
CREATE TABLE hardware (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32)
);
ALTER TABLE hardware ADD CONSTRAINT unique_hardware_name UNIQUE (name);


-----------------------------------------------------------
CREATE TABLE hardware_mining (
    id SERIAL PRIMARY KEY,
    hardware_id INTEGER NOT NULL REFERENCES hardware(id) ON DELETE CASCADE,
    algo VARCHAR(32),
    hashrate NUMERIC,
    power NUMERIC
);
ALTER TABLE hardware_mining ADD CONSTRAINT unique_hardware_algo UNIQUE (hardware_id, algo);


-----------------------------------------------------------
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


-----------------------------------------------------------
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
