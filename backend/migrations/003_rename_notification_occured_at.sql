-- 003_rename_notification_occured_at.sql
-- notification.occured_at(오타) → occurred_at(올바른 영어) 컬럼명 통일.
-- 모델/스키마/dashboard 쿼리는 이미 occurred_at을 참조하므로 DB 컬럼만 맞춰주면 정합.
-- 멱등: 이미 occurred_at으로 바뀌어 있으면 no-op.

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'notification'
      AND column_name = 'occured_at'
  ) THEN
    ALTER TABLE notification RENAME COLUMN occured_at TO occurred_at;
  END IF;
END$$;
