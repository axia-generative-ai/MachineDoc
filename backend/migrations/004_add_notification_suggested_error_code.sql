-- 004_add_notification_suggested_error_code.sql
--
-- notification 생성 시점에 (equipment_code, data_type)와 anomaly_rules.json 기반으로
-- 결정한 추천 오류코드를 함께 저장한다. REST seed가 새로고침마다 다른 랜덤 코드를
-- 반환해 사용자가 혼란을 겪지 않도록 알림별 1회 결정 값을 박제하는 용도.
--
-- 조회는 항상 LEFT JOIN 가능하도록 NULL 허용.

ALTER TABLE notification
    ADD COLUMN IF NOT EXISTS suggested_error_code VARCHAR(50);

CREATE INDEX IF NOT EXISTS ix_notification_suggested_error_code
    ON notification (suggested_error_code);
