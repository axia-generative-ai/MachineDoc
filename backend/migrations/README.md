# backend/migrations

스키마 변경(DDL) SQL. 번호순으로 한 번씩만 적용.

ai-service에도 별도 `migrations/` 폴더가 있고 (manual_sections / manual_chunks_v2 등 RAG용), 두 서비스가 같은 `smart_factory` DB를 공유하지만 **테이블 네임스페이스가 분리**되어 있어 마이그레이션을 따로 관리해도 충돌 없음.

## 적용

```bash
for f in backend/migrations/*.sql; do
  docker exec -i smart_factory_db psql -U ax_user -d smart_factory < "$f"
done
```

## 파일

| 번호 | 파일 | 설명 |
|---|---|---|
| 001 | init_prompts.sql | `prompts` 테이블 (admin이 ai-service LLM 프롬프트를 hot-edit) |
| 002 | add_saved_manual_equipment_id.sql | `saved_manual.equipment_id` FK 추가 (알림→오류코드 추천 경로) |

## 주의

- 기존 `app.db.base.Base.metadata.create_all()` 호출이 SQLAlchemy 모델 기반으로 일부 테이블을 자동 생성하므로, 마이그레이션과 모델이 어긋나지 않게 유지할 것.
- 데모 후 alembic 도입 시 이 파일들을 alembic versions로 옮기면 됨.
