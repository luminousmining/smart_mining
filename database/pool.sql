-----------------------------------------------------------
DROP PROCEDURE IF EXISTS insert_pool;


-----------------------------------------------------------
DROP TABLE IF EXISTS pools;


-----------------------------------------------------------
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



-----------------------------------------------------------
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
