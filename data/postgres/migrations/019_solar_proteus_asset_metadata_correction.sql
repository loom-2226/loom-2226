-- Correct the recorded byte count for the already acquired NEP098 Part 3 asset.
UPDATE loom_solar.ephemeris_source
SET byte_count = 1791917056
WHERE ephemeris_source_id = 'NAIF_NEP098_808'
  AND sha256 = '16955f87878e41b16934e697213350bc2d6a1b3e04d98f29ba7e0fce328b4355';

DO $$ DECLARE n bigint; BEGIN
    SELECT byte_count INTO n FROM loom_solar.ephemeris_source WHERE ephemeris_source_id = 'NAIF_NEP098_808';
    IF n <> 1791917056 THEN RAISE EXCEPTION 'NEP098 byte-count correction failed: %', n; END IF;
END $$;
