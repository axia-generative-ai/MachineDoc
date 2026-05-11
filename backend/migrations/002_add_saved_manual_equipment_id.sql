-- 002_add_saved_manual_equipment_id.sql
-- saved_manual에 equipment_id FK 추가.
-- 알림(notification)에서 추천 오류코드를 산출할 때
-- notification.equipment_id → saved_manual.equipment_id → error_code.code_name 경로로 매칭.
-- 추가 전에 매뉴얼-장비 직접 연결이 없어 모든 알림에 같은 fallback 코드만 떴음.

ALTER TABLE saved_manual
  ADD COLUMN IF NOT EXISTS equipment_id BIGINT REFERENCES equipment(equipment_id);
