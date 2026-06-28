from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Device, MaintenanceRecord, WorkOrder
from app.schemas.common import PageData, utc_now
from app.schemas.maintenance import MaintenanceRecordCreate, MaintenanceRecordRead, MaintenanceType
from app.services.notification import notification_audit_service


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def _page(db: Session, statement: Select[tuple[object]], page: int, page_size: int) -> PageData:
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = db.scalar(total_statement) or 0
    items = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return PageData(items=items, page=page, page_size=page_size, total=total)


class MaintenanceService:
    def list_records(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        device_id: UUID | None = None,
        work_order_id: UUID | None = None,
        maintenance_type: MaintenanceType | None = None,
        device_manager_id: UUID | None = None,
    ) -> PageData[MaintenanceRecordRead]:
        statement = select(MaintenanceRecord)
        if device_manager_id is not None:
            statement = statement.join(Device, MaintenanceRecord.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if device_id is not None:
            statement = statement.where(MaintenanceRecord.device_id == device_id)
        if work_order_id is not None:
            statement = statement.where(MaintenanceRecord.work_order_id == work_order_id)
        if maintenance_type is not None:
            statement = statement.where(MaintenanceRecord.maintenance_type == maintenance_type.value)
        statement = statement.order_by(MaintenanceRecord.maintained_at.desc(), MaintenanceRecord.created_at.desc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._record_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def create_record(self, db: Session, *, payload: MaintenanceRecordCreate, maintainer_id: UUID | None) -> MaintenanceRecordRead:
        device = db.get(Device, payload.device_id)
        if device is None:
            raise _not_found("device")
        if payload.work_order_id is not None and db.get(WorkOrder, payload.work_order_id) is None:
            raise _not_found("work order")
        record = MaintenanceRecord(
            device_id=payload.device_id,
            work_order_id=payload.work_order_id,
            maintainer_id=maintainer_id,
            maintenance_type=payload.maintenance_type.value,
            title=payload.title,
            content=payload.content,
            result=payload.result,
            cost_amount=payload.cost_amount,
            maintained_at=payload.maintained_at or utc_now(),
            next_maintenance_at=payload.next_maintenance_at,
        )
        db.add(record)
        db.flush()
        notification_audit_service.audit(
            db,
            action="maintenance.create",
            resource_type="maintenance_record",
            resource_id=record.id,
            actor_id=maintainer_id,
            summary=f"Create maintenance record for {device.name}",
            detail=payload.title,
        )
        self._commit(db)
        db.refresh(record)
        return self._record_read(record)

    @staticmethod
    def _commit(db: Session) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise _conflict("request conflicts with existing data") from exc

    @staticmethod
    def _record_read(record: MaintenanceRecord) -> MaintenanceRecordRead:
        return MaintenanceRecordRead(
            id=record.id,
            device_id=record.device_id,
            work_order_id=record.work_order_id,
            maintainer_id=record.maintainer_id,
            maintenance_type=MaintenanceType(record.maintenance_type),
            title=record.title,
            content=record.content,
            result=record.result,
            cost_amount=record.cost_amount,
            maintained_at=record.maintained_at,
            next_maintenance_at=record.next_maintenance_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


maintenance_service = MaintenanceService()
