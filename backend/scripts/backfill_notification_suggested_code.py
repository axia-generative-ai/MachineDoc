"""기존 notification 행에 suggested_error_code 백필.

004 migration으로 컬럼은 추가됐지만 옛 알림들은 NULL이라 알림 이력에서
"분석 불가"로 보인다. anomaly_rules.json 풀에서 random.choice로 채워
새 알림과 동일한 정책을 적용한다.

실행:
    python -m backend.scripts.backfill_notification_suggested_code
또는:
    cd backend && python scripts/backfill_notification_suggested_code.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

# repo root로부터의 import 위해 backend를 sys.path에 추가
HERE = Path(__file__).resolve()
BACKEND_ROOT = HERE.parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

# base가 모든 모델을 등록하니 먼저 로드해서 순환 import 회피.
from app.db import base  # noqa: F401, E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.equipment import Equipment  # noqa: E402
from app.models.error_code import ErrorCode  # noqa: E402
from app.models.log import EquipmentLog  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.saved_manual import SavedManual  # noqa: E402


def _pool_for(db: Session, *, equipment_id: int) -> list[str]:
    """설비에 매핑된 매뉴얼의 모든 코드 (없으면 글로벌 50건 fallback)."""
    eq_rows = (
        db.query(ErrorCode.code_name)
        .join(SavedManual, SavedManual.manual_id == ErrorCode.manual_id)
        .filter(SavedManual.equipment_id == equipment_id)
        .all()
    )
    if eq_rows:
        return [r.code_name for r in eq_rows]
    return [r.code_name for r in db.query(ErrorCode.code_name).limit(50).all()]


def main() -> None:
    db = SessionLocal()
    try:
        rows = (
            db.query(
                Notification.notification_id,
                Equipment.equipment_id,
            )
            .join(EquipmentLog, EquipmentLog.log_id == Notification.log_id)
            .join(Equipment, Equipment.equipment_id == EquipmentLog.equipment_id)
            .filter(Notification.suggested_error_code.is_(None))
            .all()
        )
        print(f"NULL인 알림 {len(rows)}건 백필 시작")

        updated = 0
        skipped = 0
        for noti_id, equipment_id in rows:
            pool = _pool_for(db, equipment_id=equipment_id)
            if not pool:
                skipped += 1
                continue
            picked = random.choice(pool)
            db.query(Notification).filter(Notification.notification_id == noti_id).update(
                {"suggested_error_code": picked}
            )
            updated += 1

        db.commit()
        print(f"백필 완료: updated={updated}, skipped(풀 0건)={skipped}")
    except Exception as exc:
        db.rollback()
        print(f"백필 실패: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
