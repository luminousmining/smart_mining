-----------------------------------------------------------
DROP FUNCTION IF EXISTS profile_emission_usd;
DROP FUNCTION IF EXISTS profile_hash_usd;


-----------------------------------------------------------
CREATE FUNCTION profile_emission_usd()
RETURNS TABLE (
    name VARCHAR(32),
    tag VARCHAR(32),
    emission_usd NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name,
        UPPER(c.tag)::VARCHAR(32) AS tag,
        c.emission_usd
    FROM coins c
    ORDER BY c.emission_usd DESC;
END;
$$;


-----------------------------------------------------------
CREATE FUNCTION profile_hash_usd()
RETURNS TABLE (
    name VARCHAR(32),
    tag VARCHAR(32),
    hash_usd NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name,
        UPPER(c.tag)::VARCHAR(32) AS tag,
        c.hash_usd
    FROM coins c
    WHERE c.hash_usd > 0
    ORDER BY c.hash_usd DESC;
END;
$$;
