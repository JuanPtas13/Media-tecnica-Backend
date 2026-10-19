ALTER TABLE config_horario
    ADD COLUMN IF NOT EXISTS hora_cierre_asistencia TIME;

UPDATE config_horario
SET hora_cierre_asistencia = TIME '23:59'
WHERE hora_cierre_asistencia IS NULL;

ALTER TABLE config_horario
    ALTER COLUMN hora_cierre_asistencia SET NOT NULL;

UPDATE config_horario
SET min_tolerancia = GREATEST(
    0,
    ROUND(EXTRACT(EPOCH FROM (hora_limite_ingreso - hora_inicio_clase)) / 60)::integer
);
