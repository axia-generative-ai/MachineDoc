-- demo.sql — 데모/개발 환경 초기 데이터 부트스트랩
--
-- 적용: docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/seeds/demo.sql
-- 선행 조건: migrations/ 폴더의 모든 SQL이 먼저 적용되어 있어야 함
--
-- 멱등성: 기존 데이터 TRUNCATE 후 재삽입. **admin user는 보존**되도록 user 테이블은 건드리지 않음.
--
-- 시드 범위: 기획서 "가상 설비 5종 / 오류코드 20여 개"에 맞춘 초기 데이터.
-- 매뉴얼 업로드 기능이 정상 작동하므로 이후 추가 매뉴얼은 admin이 UI에서 등록 가능하다.

BEGIN;

TRUNCATE TABLE error_code, equipment_threshold, log, action_log, notification, search_history, saved_manual, equipment RESTART IDENTITY CASCADE;

-- 1. equipment 5종 (기획서 "가상 설비 5종"에 대응. 동적 추가 UI 없음 — 데모 범위 한정)
INSERT INTO equipment (location, equipment_code, state) VALUES
  ('LINE_A', 'EQ-MOTOR-001',    'RUNNING'),
  ('LINE_A', 'EQ-CONVEYOR-002', 'RUNNING'),
  ('LINE_B', 'EQ-PRESS-003',    'RUNNING'),
  ('LINE_B', 'EQ-ROBOT-004',    'RUNNING'),
  ('LINE_C', 'EQ-WELDING-005',  'RUNNING');

-- 2. equipment_threshold (장비별 TEMP/VIB 임계값, 가상 로그의 warning/error 판정 기준)
INSERT INTO equipment_threshold (equipment_id, data_type, warning_threshold, error_threshold)
SELECT equipment_id, 'TEMPERATURE', 70, 90 FROM equipment;
INSERT INTO equipment_threshold (equipment_id, data_type, warning_threshold, error_threshold)
SELECT equipment_id, 'VIBRATION', 800, 1100 FROM equipment;

-- 3. saved_manual 5건 — admin(user_id=3) 소유로 ai-service/manuals/의 실 PDF에 매핑
-- file_url: ai-service 폴더 내 실제 파일명 (backend config.MANUAL_URL 기준 prefix 조합)
-- equipment_id: 알림 → 오류코드 추천 경로의 핵심 매핑. 추가 업로드 시 admin UI에서 선택해야 함.
INSERT INTO saved_manual (user_id, title, file_url, category, version, equipment_id) VALUES
  (3, 'YASKAWA GA700 모터 매뉴얼',          'ga700.pdf',                            '점검', 'v1.0', 1),
  (3, 'Rockwell PowerFlex 컨베이어 매뉴얼', '520-um001_-en-e.pdf',                  '수리', 'v1.0', 2),
  (3, 'FANUC 0M 프레스 매뉴얼',             'fanuc_series0m_maintenance.pdf',       '점검', 'v1.0', 3),
  (3, 'ABB IRB 로봇 매뉴얼',                'abb_irb_troubleshooting.pdf',          '수리', 'v1.0', 4),
  (3, 'Mitsubishi Servo 용접기 매뉴얼',     'mitsubishi_servo_amp_instruction.pdf', '점검', 'v1.0', 5);

-- 4. error_code 20행 (각 매뉴얼당 4개씩)
-- ai-service가 인덱싱한 실제 PDF 본문에서 등장하는 코드만 사용.
-- 가짜 코드(E0001 류)를 쓰면 RAG가 매뉴얼 출처를 인용하지 못해 ManualPreview/AI 조치절차에
-- (출처: ...) 매핑이 비게 됨. 매뉴얼별 대표 알람/Fault 코드를 4개씩 선정.
--   manual 1 (ga700.pdf, YASKAWA GA700)        : oPE03/A001/S020/OPE08 류
--   manual 2 (520-um001, Rockwell PowerFlex)   : F0xx Fault 코드
--   manual 3 (fanuc_series0m_maintenance)      : ALMxxx / NO. xxxx
--   manual 4 (abb_irb_troubleshooting)         : 5자리 Event ID (10025 류)
--   manual 5 (mitsubishi_servo_amp_instruction): AL.xx 알람
INSERT INTO error_code (manual_id, code_name) VALUES
  (1,'A001'),  (1,'OPE03'),  (1,'OPE08'),  (1,'S020'),
  (2,'F081'),  (2,'F014'),   (2,'F021'),   (2,'F111'),
  (3,'ALM197'),(3,'ALM401'), (3,'ALM403'), (3,'ALM500'),
  (4,'10025'), (4,'10026'),  (4,'10030'),  (4,'10034'),
  (5,'AL.50'), (5,'AL.25'),  (5,'AL.51'),  (5,'AL.74');

-- 5. 24시간 분산 log + notification — 대시보드 trend/digest 시각화 보강
-- 시드 직후 데이터가 한 시점에 몰려있으면 trend 차트가 직선이 되고
-- digest는 모두 확인 처리되면 비어버린다. 시간대별로 분산 + 일부 미확인 보장.
-- 기준 now()에서 23h, 21h, 19h, ... , 1h 전(2h 간격, 12개 시점) × 장비 1~5 순환.
-- ENUM: SQLAlchemy가 이름값(NORMAL/WARNING/ERROR, UNREAD/..., URGENT/...)으로 저장. 한글값(value) X.
INSERT INTO log (equipment_id, data_type, value, status, occurred_at)
SELECT
    ((g - 1) % 5) + 1                                                AS equipment_id,
    (CASE WHEN g % 2 = 0 THEN 'TEMPERATURE' ELSE 'VIBRATION' END)::datatype AS data_type,
    (CASE WHEN g % 2 = 0 THEN 75 + (g * 1.7) ELSE 850 + (g * 12.3) END) AS value,
    (CASE WHEN g % 4 = 0 THEN 'ERROR' ELSE 'WARNING' END)::logstatus AS status,
    now() - ((24 - 2 * g) || ' hours')::interval                     AS occurred_at
FROM generate_series(1, 12) AS g;

-- notification 1:1 (12건 중 4건 미확인, 4건 확인, 4건 완료 — digest 보장)
INSERT INTO notification (log_id, message, is_read, level, occurred_at)
SELECT
    l.log_id,
    e.equipment_code || ' ' || l.data_type || ' 임계 초과 (' || round(l.value::numeric, 1) || ')' AS message,
    (CASE
        WHEN l.log_id % 3 = 0 THEN 'UNREAD'
        WHEN l.log_id % 3 = 1 THEN 'CHECKED'
        ELSE 'COMPLETED'
     END)::readstatus AS is_read,
    (CASE
        WHEN l.status = 'ERROR' THEN 'URGENT'
        WHEN l.value > 1000 OR l.value > 85 THEN 'WARNING'
        ELSE 'CAUTION'
     END)::notificationlevel AS level,
    l.occurred_at
FROM log l
JOIN equipment e ON e.equipment_id = l.equipment_id
WHERE NOT EXISTS (SELECT 1 FROM notification n WHERE n.log_id = l.log_id);

COMMIT;

-- 적용 결과 검증
SELECT 'equipment' AS tbl, count(*) FROM equipment
UNION ALL SELECT 'equipment_threshold', count(*) FROM equipment_threshold
UNION ALL SELECT 'saved_manual', count(*) FROM saved_manual
UNION ALL SELECT 'error_code', count(*) FROM error_code
UNION ALL SELECT 'log (seed)', count(*) FROM log
UNION ALL SELECT 'notification (seed)', count(*) FROM notification
UNION ALL SELECT 'notification UNREAD', count(*) FROM notification WHERE is_read = 'UNREAD';
