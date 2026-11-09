-- pico.legacy_timezone is set by scripts.migrate; existing values are not guessed.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema=current_schema() AND table_name='sensor_metrics'
          AND column_name='time' AND data_type='timestamp without time zone'
    ) THEN
        ALTER TABLE sensor_metrics ALTER COLUMN time TYPE TIMESTAMPTZ
            USING time AT TIME ZONE current_setting('pico.legacy_timezone');
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS sensor_metrics_time_idx ON sensor_metrics (time);
