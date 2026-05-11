# backend/seeds

데모/개발 환경 초기 데이터(DML). 마이그레이션과 분리.

## 적용

```bash
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/seeds/demo.sql
```

## 파일

| 파일 | 설명 |
|---|---|
| demo.sql | equipment 5종 / threshold 10건 / saved_manual 5건 / error_code 20건. 멱등성(TRUNCATE+INSERT). admin user 보존 |

## 주의

- 매뉴얼 업로드 기능이 작동하므로, 시드 적용 후엔 admin UI에서 추가 등록 가능.
- 이미 운영 중인 DB에 적용하면 일부 데이터가 사라진다 (TRUNCATE). 처음 셋업이나 데모 리셋용으로만 사용.
