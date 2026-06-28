from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.domain import Device, DeviceCategory, Lab, OperationMetric, RepairReport, Reservation, User, WorkOrder
from app.schemas.common import PageData, utc_now
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint
from app.schemas.device import DeviceCreate, DeviceRead, DeviceStatus, DeviceUpdate
from app.schemas.repair_report import RepairReportCreate, RepairReportRead, RepairReportStatus
from app.schemas.reservation import ReservationAvailabilityRead, ReservationCalendarItem, ReservationCreate, ReservationRead, ReservationStatus
from app.schemas.work_order import WorkOrderCreate, WorkOrderPriority, WorkOrderRead, WorkOrderStatus
from app.services.notification import notification_audit_service


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def _page(db: Session, statement: Select[tuple[object]], page: int, page_size: int) -> PageData:
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = db.scalar(total_statement) or 0
    items = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return PageData(items=items, page=page, page_size=page_size, total=total)


def _enum_value(value: object | None) -> str | None:
    if value is None:
        return None
    return str(getattr(value, "value", value))


def _to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


DEVICE_TO_DB = {
    DeviceStatus.available: "idle",
    DeviceStatus.reserved: "in_use",
    DeviceStatus.in_use: "in_use",
    DeviceStatus.maintenance: "maintenance",
    DeviceStatus.disabled: "disabled",
}
DEVICE_FROM_DB = {
    "idle": DeviceStatus.available,
    "in_use": DeviceStatus.in_use,
    "maintenance": DeviceStatus.maintenance,
    "fault": DeviceStatus.maintenance,
    "disabled": DeviceStatus.disabled,
}
RESERVATION_TO_DB = {
    ReservationStatus.pending: "pending",
    ReservationStatus.approved: "approved",
    ReservationStatus.rejected: "rejected",
    ReservationStatus.canceled: "cancelled",
    ReservationStatus.completed: "completed",
}
RESERVATION_FROM_DB = {value: key for key, value in RESERVATION_TO_DB.items()}
WORK_ORDER_TO_DB = {
    WorkOrderStatus.pending: "assigned",
    WorkOrderStatus.assigned: "assigned",
    WorkOrderStatus.processing: "processing",
    WorkOrderStatus.finished: "finished",
    WorkOrderStatus.canceled: "closed",
    WorkOrderStatus.closed: "closed",
}
WORK_ORDER_FROM_DB = {
    "assigned": WorkOrderStatus.pending,
    "processing": WorkOrderStatus.processing,
    "finished": WorkOrderStatus.finished,
    "closed": WorkOrderStatus.closed,
}


class LabOpsService:
    def list_devices(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        keyword: str | None = None,
        lab_id: UUID | None = None,
        category_id: UUID | None = None,
        status: DeviceStatus | None = None,
        manager_id: UUID | None = None,
    ) -> PageData[DeviceRead]:
        statement = select(Device)
        if manager_id is not None:
            statement = statement.where(Device.manager_id == manager_id)
        if lab_id is not None:
            statement = statement.where(Device.lab_id == lab_id)
        if category_id is not None:
            statement = statement.where(Device.category_id == category_id)
        if status is not None:
            statement = statement.where(Device.status == DEVICE_TO_DB[status])
        if keyword:
            pattern = f"%{keyword.lower().strip()}%"
            statement = statement.where(or_(func.lower(Device.code).like(pattern), func.lower(Device.name).like(pattern)))
        statement = statement.order_by(Device.updated_at.desc(), Device.created_at.desc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._device_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def create_device(self, db: Session, payload: DeviceCreate) -> DeviceRead:
        if db.scalar(select(Device.id).where(Device.code == payload.code)):
            raise _conflict("device code already exists")
        category_id = payload.category_id or self._default_id(db, DeviceCategory, "device category")
        lab_id = payload.lab_id or self._default_id(db, Lab, "lab")
        device = Device(
            code=payload.code,
            name=payload.name,
            category_id=category_id,
            lab_id=lab_id,
            manager_id=self._optional_existing_user_id(db, payload.manager_id),
            status=DEVICE_TO_DB[payload.status],
            health_score=Decimal(str(payload.health_score if payload.health_score is not None else 100)),
            purchase_date=payload.purchase_date,
        )
        db.add(device)
        self._commit(db)
        db.refresh(device)
        return self._device_read(device)

    def get_device(self, db: Session, device_id: UUID) -> DeviceRead:
        return self._device_read(self._device(db, device_id))

    def update_device(self, db: Session, device_id: UUID, payload: DeviceUpdate) -> DeviceRead:
        device = self._device(db, device_id)
        changes = payload.model_dump(exclude_unset=True)
        if "code" in changes and db.scalar(select(Device.id).where(Device.id != device_id, Device.code == changes["code"])):
            raise _conflict("device code already exists")
        for key, value in changes.items():
            if key == "status" and value is not None:
                setattr(device, key, DEVICE_TO_DB[value])
            elif key == "health_score" and value is not None:
                setattr(device, key, Decimal(str(value)))
            elif key in {"category_id", "lab_id"} and value is None:
                continue
            elif key == "manager_id":
                setattr(device, key, self._optional_existing_user_id(db, value))
            else:
                setattr(device, key, value)
        self._commit(db)
        db.refresh(device)
        return self._device_read(device)

    def update_device_status(self, db: Session, device_id: UUID, status_: DeviceStatus) -> DeviceRead:
        return self.update_device(db, device_id, DeviceUpdate(status=status_))

    def delete_device(self, db: Session, device_id: UUID) -> DeviceRead:
        return self.update_device(db, device_id, DeviceUpdate(status=DeviceStatus.disabled))

    def list_reservations(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        device_id: UUID | None = None,
        applicant_id: UUID | None = None,
        status: ReservationStatus | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        device_manager_id: UUID | None = None,
    ) -> PageData[ReservationRead]:
        statement = select(Reservation)
        if device_manager_id is not None:
            statement = statement.join(Device, Reservation.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if device_id is not None:
            statement = statement.where(Reservation.device_id == device_id)
        if applicant_id is not None:
            statement = statement.where(Reservation.applicant_id == applicant_id)
        if status is not None:
            statement = statement.where(Reservation.status == RESERVATION_TO_DB[status])
        if start_time is not None:
            statement = statement.where(Reservation.end_time >= start_time)
        if end_time is not None:
            statement = statement.where(Reservation.start_time <= end_time)
        statement = statement.order_by(Reservation.updated_at.desc(), Reservation.created_at.desc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._reservation_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def reservation_calendar(
        self,
        db: Session,
        *,
        start_time: datetime,
        end_time: datetime,
        device_id: UUID | None = None,
        applicant_id: UUID | None = None,
        device_manager_id: UUID | None = None,
    ) -> list[ReservationCalendarItem]:
        if end_time <= start_time:
            raise _bad_request("end_time must be later than start_time")
        if end_time - start_time > timedelta(days=62):
            raise _bad_request("calendar range cannot exceed 62 days")

        statement = select(Reservation).where(
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
            Reservation.status.in_(["pending", "approved", "completed"]),
        )
        if device_manager_id is not None:
            statement = statement.join(Device, Reservation.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if device_id is not None:
            statement = statement.where(Reservation.device_id == device_id)
        if applicant_id is not None:
            statement = statement.where(Reservation.applicant_id == applicant_id)

        rows = db.scalars(statement.order_by(Reservation.start_time.asc(), Reservation.created_at.asc())).all()
        return [self._reservation_calendar_item(item) for item in rows]

    def check_reservation_availability(
        self,
        db: Session,
        *,
        device_id: UUID,
        start_time: datetime,
        end_time: datetime,
        ignored_reservation_id: UUID | None = None,
    ) -> ReservationAvailabilityRead:
        self._device(db, device_id)
        if end_time <= start_time:
            raise _bad_request("end_time must be later than start_time")

        conditions = [
            Reservation.device_id == device_id,
            Reservation.status == "approved",
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
        ]
        if ignored_reservation_id is not None:
            conditions.append(Reservation.id != ignored_reservation_id)

        conflicts = db.scalars(select(Reservation).where(and_(*conditions)).order_by(Reservation.start_time.asc())).all()
        return ReservationAvailabilityRead(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            available=len(conflicts) == 0,
            conflict_count=len(conflicts),
            conflicts=[self._reservation_calendar_item(item) for item in conflicts],
        )

    def create_reservation(self, db: Session, payload: ReservationCreate, applicant_id: UUID) -> ReservationRead:
        device = self._device(db, payload.device_id)
        self._ensure_no_reservation_conflict(db, payload.device_id, payload.start_time, payload.end_time)
        applicant = self._actor_user_id(db, applicant_id)
        reservation = Reservation(
            reservation_no=self._number("RSV"),
            device_id=payload.device_id,
            applicant_id=applicant,
            start_time=payload.start_time,
            end_time=payload.end_time,
            purpose=payload.purpose,
            participant_count=1,
            status="pending",
        )
        db.add(reservation)
        db.flush()
        notification_audit_service.notify_users(
            db,
            [device.manager_id],
            title="新的预约待审核",
            content=f"{device.name} 收到新的预约申请，请及时审核。",
            category="warning",
            business_type="reservation",
            business_id=reservation.id,
        )
        notification_audit_service.audit(
            db,
            action="reservation.create",
            resource_type="reservation",
            resource_id=reservation.id,
            actor_id=applicant,
            summary=f"提交 {device.name} 预约申请",
        )
        self._commit(db)
        db.refresh(reservation)
        return self._reservation_read(reservation)

    def get_reservation(self, db: Session, reservation_id: UUID) -> ReservationRead:
        return self._reservation_read(self._reservation(db, reservation_id))

    def approve_reservation(self, db: Session, reservation_id: UUID, approver_id: UUID) -> ReservationRead:
        reservation = self._reservation(db, reservation_id)
        self._ensure_no_reservation_conflict(
            db, reservation.device_id, reservation.start_time, reservation.end_time, reservation.id
        )
        reservation.status = "approved"
        reservation.approver_id = self._actor_user_id(db, approver_id)
        reservation.reject_reason = None
        reservation.approved_at = utc_now()
        notification_audit_service.notify_users(
            db,
            [reservation.applicant_id],
            title="预约已通过",
            content="您的设备预约已审核通过，请按预约时段使用设备。",
            category="success",
            business_type="reservation",
            business_id=reservation.id,
        )
        notification_audit_service.audit(
            db,
            action="reservation.approve",
            resource_type="reservation",
            resource_id=reservation.id,
            actor_id=reservation.approver_id,
            summary="预约审核通过",
        )
        self._commit(db)
        db.refresh(reservation)
        return self._reservation_read(reservation)

    def reject_reservation(self, db: Session, reservation_id: UUID, approver_id: UUID, reject_reason: str) -> ReservationRead:
        reservation = self._reservation(db, reservation_id)
        reservation.status = "rejected"
        reservation.approver_id = self._actor_user_id(db, approver_id)
        reservation.reject_reason = reject_reason
        notification_audit_service.notify_users(
            db,
            [reservation.applicant_id],
            title="预约已驳回",
            content=f"您的设备预约未通过审核，原因：{reject_reason}",
            category="error",
            business_type="reservation",
            business_id=reservation.id,
        )
        notification_audit_service.audit(
            db,
            action="reservation.reject",
            resource_type="reservation",
            resource_id=reservation.id,
            actor_id=reservation.approver_id,
            summary="预约审核驳回",
            detail=reject_reason,
        )
        self._commit(db)
        db.refresh(reservation)
        return self._reservation_read(reservation)

    def cancel_reservation(self, db: Session, reservation_id: UUID, actor_id: UUID | None = None) -> ReservationRead:
        reservation = self._reservation(db, reservation_id)
        reservation.status = "cancelled"
        reservation.cancelled_at = utc_now()
        notification_audit_service.notify_device_manager(
            db,
            reservation.device_id,
            title="预约已取消",
            content="一条设备预约已取消，设备时段重新释放。",
            category="info",
            business_type="reservation",
            business_id=reservation.id,
        )
        notification_audit_service.audit(
            db,
            action="reservation.cancel",
            resource_type="reservation",
            resource_id=reservation.id,
            actor_id=actor_id,
            summary="取消预约",
        )
        self._commit(db)
        db.refresh(reservation)
        return self._reservation_read(reservation)

    def list_repair_reports(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        device_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: RepairReportStatus | None = None,
        fault_type: str | None = None,
        device_manager_id: UUID | None = None,
    ) -> PageData[RepairReportRead]:
        statement = select(RepairReport)
        if device_manager_id is not None:
            statement = statement.join(Device, RepairReport.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if device_id is not None:
            statement = statement.where(RepairReport.device_id == device_id)
        if reporter_id is not None:
            statement = statement.where(RepairReport.reporter_id == reporter_id)
        if status is not None:
            statement = statement.where(RepairReport.status == _enum_value(status))
        if fault_type:
            statement = statement.where(func.lower(RepairReport.fault_type).like(f"%{fault_type.lower().strip()}%"))
        statement = statement.order_by(RepairReport.updated_at.desc(), RepairReport.created_at.desc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._repair_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def create_repair_report(self, db: Session, payload: RepairReportCreate, reporter_id: UUID) -> RepairReportRead:
        device = self._device(db, payload.device_id)
        report = RepairReport(
            report_no=self._number("REP"),
            device_id=payload.device_id,
            reporter_id=self._actor_user_id(db, reporter_id),
            fault_type=payload.fault_type,
            urgency="medium",
            description=payload.description,
            status="submitted",
        )
        db.add(report)
        db.flush()
        notification_audit_service.notify_users(
            db,
            [device.manager_id],
            title="新的设备报修",
            content=f"{device.name} 收到新的{payload.fault_type}报修，请安排处理。",
            category="warning",
            business_type="repair",
            business_id=report.id,
        )
        notification_audit_service.notify_admins(
            db,
            title="新的设备报修",
            content=f"{device.name} 收到新的报修记录。",
            category="info",
            business_type="repair",
            business_id=report.id,
        )
        notification_audit_service.audit(
            db,
            action="repair.create",
            resource_type="repair_report",
            resource_id=report.id,
            actor_id=report.reporter_id,
            summary=f"提交 {device.name} 报修",
            detail=payload.description,
        )
        self._commit(db)
        db.refresh(report)
        return self._repair_read(report)

    def get_repair_report(self, db: Session, report_id: UUID) -> RepairReportRead:
        return self._repair_read(self._repair_report(db, report_id))

    def list_work_orders(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        assignee_id: UUID | None = None,
        status: WorkOrderStatus | None = None,
        priority: WorkOrderPriority | None = None,
        device_manager_id: UUID | None = None,
    ) -> PageData[WorkOrderRead]:
        statement = select(WorkOrder)
        if device_manager_id is not None:
            statement = statement.join(Device, WorkOrder.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if assignee_id is not None:
            statement = statement.where(WorkOrder.assignee_id == assignee_id)
        if status is not None:
            statement = statement.where(WorkOrder.status == WORK_ORDER_TO_DB[status])
        if priority is not None:
            statement = statement.where(WorkOrder.priority == _enum_value(priority))
        statement = statement.order_by(WorkOrder.updated_at.desc(), WorkOrder.created_at.desc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._work_order_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def create_work_order(self, db: Session, payload: WorkOrderCreate, creator_id: UUID | None = None) -> WorkOrderRead:
        report = self._repair_report(db, payload.repair_report_id)
        work_order = WorkOrder(
            work_order_no=self._number("WO"),
            repair_report_id=report.id,
            device_id=report.device_id,
            creator_id=self._actor_user_id(db, creator_id) if creator_id else self._first_user_id(db),
            assignee_id=self._optional_existing_user_id(db, payload.assignee_id),
            priority=payload.priority.value,
            status="assigned",
        )
        report.status = "assigned"
        report.accepted_at = report.accepted_at or utc_now()
        db.add(work_order)
        db.flush()
        notification_audit_service.notify_users(
            db,
            [work_order.assignee_id, report.reporter_id],
            title="维修工单已创建",
            content="报修记录已生成维修工单，请关注处理进度。",
            category="info",
            business_type="work_order",
            business_id=work_order.id,
        )
        notification_audit_service.audit(
            db,
            action="work_order.create",
            resource_type="work_order",
            resource_id=work_order.id,
            actor_id=work_order.creator_id,
            summary="创建维修工单",
        )
        self._commit(db)
        db.refresh(work_order)
        return self._work_order_read(work_order)

    def get_work_order(self, db: Session, work_order_id: UUID) -> WorkOrderRead:
        return self._work_order_read(self._work_order(db, work_order_id))

    def update_work_order_status(self, db: Session, work_order_id: UUID, status_: WorkOrderStatus) -> WorkOrderRead:
        work_order = self._work_order(db, work_order_id)
        new_status = WORK_ORDER_TO_DB[status_]
        work_order.status = new_status
        now = utc_now()
        if new_status == "processing" and work_order.started_at is None:
            work_order.started_at = now
            self._repair_report(db, work_order.repair_report_id).status = "processing"
        if new_status == "finished":
            work_order.finished_at = now
            self._repair_report(db, work_order.repair_report_id).status = "finished"
        if new_status == "closed":
            work_order.closed_at = now
            self._close_repair_report(db, work_order.repair_report_id, work_order.result)
        notification_audit_service.notify_users(
            db,
            [work_order.assignee_id],
            title="工单状态已更新",
            content=f"工单 {work_order.work_order_no} 状态更新为 {new_status}。",
            category="info",
            business_type="work_order",
            business_id=work_order.id,
        )
        notification_audit_service.audit(
            db,
            action=f"work_order.{new_status}",
            resource_type="work_order",
            resource_id=work_order.id,
            actor_id=work_order.assignee_id,
            summary=f"更新工单状态为 {new_status}",
        )
        self._commit(db)
        db.refresh(work_order)
        return self._work_order_read(work_order)

    def finish_work_order(self, db: Session, work_order_id: UUID, result: str) -> WorkOrderRead:
        work_order = self._work_order(db, work_order_id)
        now = utc_now()
        work_order.status = "finished"
        work_order.result = result
        work_order.finished_at = now
        self._close_repair_report(db, work_order.repair_report_id, result)
        report = self._repair_report(db, work_order.repair_report_id)
        notification_audit_service.notify_users(
            db,
            [work_order.assignee_id, report.reporter_id],
            title="维修工单已完成",
            content=f"工单 {work_order.work_order_no} 已完成：{result}",
            category="success",
            business_type="work_order",
            business_id=work_order.id,
        )
        notification_audit_service.audit(
            db,
            action="work_order.finish",
            resource_type="work_order",
            resource_id=work_order.id,
            actor_id=work_order.assignee_id,
            summary="完成维修工单",
            detail=result,
        )
        self._commit(db)
        db.refresh(work_order)
        return self._work_order_read(work_order)

    def dashboard_summary(
        self,
        db: Session,
        *,
        applicant_id: UUID | None = None,
        reporter_id: UUID | None = None,
        device_manager_id: UUID | None = None,
    ) -> DashboardSummary:
        today_start = datetime.combine(date.today(), datetime.min.time()).astimezone()
        tomorrow_start = today_start + timedelta(days=1)
        device_count_statement = select(func.count()).select_from(Device)
        available_count_statement = select(func.count()).select_from(Device).where(Device.status == "idle")
        reservation_count_statement = (
            select(func.count())
            .select_from(Reservation)
            .where(Reservation.start_time >= today_start, Reservation.start_time < tomorrow_start)
        )
        repair_count_statement = select(func.count()).select_from(RepairReport).where(RepairReport.status == "submitted")
        work_order_count_statement = select(func.count()).select_from(WorkOrder).where(WorkOrder.status.in_(["assigned", "processing"]))

        if device_manager_id is not None:
            device_count_statement = device_count_statement.where(Device.manager_id == device_manager_id)
            available_count_statement = available_count_statement.where(Device.manager_id == device_manager_id)
            reservation_count_statement = reservation_count_statement.join(Device, Reservation.device_id == Device.id).where(Device.manager_id == device_manager_id)
            repair_count_statement = repair_count_statement.join(Device, RepairReport.device_id == Device.id).where(Device.manager_id == device_manager_id)
            work_order_count_statement = work_order_count_statement.join(Device, WorkOrder.device_id == Device.id).where(Device.manager_id == device_manager_id)
        if applicant_id is not None:
            reservation_count_statement = reservation_count_statement.where(Reservation.applicant_id == applicant_id)
            work_order_count_statement = work_order_count_statement.where(WorkOrder.id.is_(None))
        if reporter_id is not None:
            repair_count_statement = repair_count_statement.where(RepairReport.reporter_id == reporter_id)

        return DashboardSummary(
            device_total=db.scalar(device_count_statement) or 0,
            device_available=db.scalar(available_count_statement) or 0,
            today_reservations=db.scalar(reservation_count_statement) or 0,
            pending_repairs=db.scalar(repair_count_statement) or 0,
            open_work_orders=db.scalar(work_order_count_statement) or 0,
        )

    def device_utilization(
        self,
        db: Session,
        start_date: date | None,
        end_date: date | None,
        lab_id: UUID | None,
        device_manager_id: UUID | None = None,
    ) -> list[TrendPoint]:
        if device_manager_id is not None:
            start = start_date or date.today() - timedelta(days=6)
            end = end_date or start + timedelta(days=6)
            days = min((end - start).days + 1, 31)
            avg_health = db.scalar(select(func.avg(Device.health_score)).where(Device.manager_id == device_manager_id)) or Decimal("0")
            return [TrendPoint(date=start + timedelta(days=index), value=float(avg_health)) for index in range(days)]
        return self._metric_trend(db, start_date, end_date, lab_id, OperationMetric.utilization_rate)

    def repair_trend(
        self,
        db: Session,
        start_date: date | None,
        end_date: date | None,
        lab_id: UUID | None,
        reporter_id: UUID | None = None,
        device_manager_id: UUID | None = None,
    ) -> list[TrendPoint]:
        if reporter_id is not None or device_manager_id is not None:
            start = start_date or date.today() - timedelta(days=6)
            end = end_date or start + timedelta(days=6)
            days = min((end - start).days + 1, 31)
            wanted_dates = [start + timedelta(days=index) for index in range(days)]
            statement = select(func.date(RepairReport.created_at), func.count()).where(func.date(RepairReport.created_at).in_(wanted_dates))
            if reporter_id is not None:
                statement = statement.where(RepairReport.reporter_id == reporter_id)
            if device_manager_id is not None:
                statement = statement.join(Device, RepairReport.device_id == Device.id).where(Device.manager_id == device_manager_id)
            rows = {metric_date: count for metric_date, count in db.execute(statement.group_by(func.date(RepairReport.created_at))).all()}
            return [TrendPoint(date=metric_date, value=float(rows.get(metric_date, 0))) for metric_date in wanted_dates]
        return self._metric_trend(db, start_date, end_date, lab_id, OperationMetric.repair_report_count)

    def reservation_status(
        self,
        db: Session,
        *,
        applicant_id: UUID | None = None,
        device_manager_id: UUID | None = None,
    ) -> list[StatusCount]:
        statement = select(Reservation.status, func.count()).select_from(Reservation)
        if applicant_id is not None:
            statement = statement.where(Reservation.applicant_id == applicant_id)
        if device_manager_id is not None:
            statement = statement.join(Device, Reservation.device_id == Device.id).where(Device.manager_id == device_manager_id)
        rows = db.execute(statement.group_by(Reservation.status)).all()
        counts = {status_: 0 for status_ in ReservationStatus}
        for db_status, count in rows:
            counts[RESERVATION_FROM_DB.get(db_status, db_status)] = count
        return [StatusCount(status=status_, count=count) for status_, count in counts.items()]

    def _metric_trend(
        self,
        db: Session,
        start_date: date | None,
        end_date: date | None,
        lab_id: UUID | None,
        value_column: object,
    ) -> list[TrendPoint]:
        start = start_date or date.today() - timedelta(days=6)
        end = end_date or start + timedelta(days=6)
        if end < start:
            raise _bad_request("end_date must be later than start_date")
        days = min((end - start).days + 1, 31)
        wanted_dates = [start + timedelta(days=index) for index in range(days)]
        statement = select(OperationMetric.metric_date, value_column).where(
            OperationMetric.period_type == "daily",
            OperationMetric.metric_date.in_(wanted_dates),
            OperationMetric.device_id.is_(None),
        )
        statement = statement.where(OperationMetric.lab_id == lab_id) if lab_id else statement.where(OperationMetric.lab_id.is_(None))
        rows = {metric_date: float(value or 0) for metric_date, value in db.execute(statement).all()}
        return [TrendPoint(date=metric_date, value=rows.get(metric_date, 0.0)) for metric_date in wanted_dates]

    def _ensure_no_reservation_conflict(
        self,
        db: Session,
        device_id: UUID,
        start_time: datetime,
        end_time: datetime,
        ignored_reservation_id: UUID | None = None,
    ) -> None:
        conditions = [
            Reservation.device_id == device_id,
            Reservation.status == "approved",
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
        ]
        if ignored_reservation_id is not None:
            conditions.append(Reservation.id != ignored_reservation_id)
        if db.scalar(select(Reservation.id).where(and_(*conditions)).limit(1)):
            raise _conflict("reservation time conflicts with an approved reservation")

    def _close_repair_report(self, db: Session, report_id: UUID, note: str | None) -> None:
        report = self._repair_report(db, report_id)
        report.status = "closed"
        report.closed_at = utc_now()
        report.close_note = note

    def _device(self, db: Session, device_id: UUID) -> Device:
        device = db.get(Device, device_id)
        if device is None:
            raise _not_found("device")
        return device

    def _reservation(self, db: Session, reservation_id: UUID) -> Reservation:
        reservation = db.get(Reservation, reservation_id)
        if reservation is None:
            raise _not_found("reservation")
        return reservation

    def _repair_report(self, db: Session, report_id: UUID) -> RepairReport:
        report = db.get(RepairReport, report_id)
        if report is None:
            raise _not_found("repair report")
        return report

    def _work_order(self, db: Session, work_order_id: UUID) -> WorkOrder:
        work_order = db.get(WorkOrder, work_order_id)
        if work_order is None:
            raise _not_found("work order")
        return work_order

    def _default_id(self, db: Session, model: type[Lab] | type[DeviceCategory], resource: str) -> UUID:
        item_id = db.scalar(select(model.id).order_by(model.created_at.asc()).limit(1))
        if item_id is None:
            raise _bad_request(f"default {resource} not found")
        return item_id

    def _actor_user_id(self, db: Session, user_id: UUID | None) -> UUID:
        if user_id is not None and db.get(User, user_id) is not None:
            return user_id
        return self._first_user_id(db)

    def _optional_existing_user_id(self, db: Session, user_id: UUID | None) -> UUID | None:
        if user_id is None:
            return None
        return user_id if db.get(User, user_id) is not None else self._first_user_id(db)

    def _first_user_id(self, db: Session) -> UUID:
        user_id = db.scalar(select(User.id).order_by(User.created_at.asc()).limit(1))
        if user_id is None:
            raise _bad_request("user not found")
        return user_id

    @staticmethod
    def _number(prefix: str) -> str:
        return f"{prefix}-{utc_now().strftime('%Y%m%d%H%M%S%f')}"

    @staticmethod
    def _commit(db: Session) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise _conflict("request conflicts with existing data") from exc

    @staticmethod
    def _device_read(device: Device) -> DeviceRead:
        return DeviceRead(
            id=device.id,
            code=device.code,
            name=device.name,
            category_id=device.category_id,
            lab_id=device.lab_id,
            manager_id=device.manager_id,
            status=DEVICE_FROM_DB.get(device.status, DeviceStatus.maintenance),
            health_score=_to_float(device.health_score),
            purchase_date=device.purchase_date,
            created_at=device.created_at,
            updated_at=device.updated_at,
        )

    @staticmethod
    def _reservation_read(reservation: Reservation) -> ReservationRead:
        return ReservationRead(
            id=reservation.id,
            device_id=reservation.device_id,
            applicant_id=reservation.applicant_id,
            approver_id=reservation.approver_id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            purpose=reservation.purpose,
            status=RESERVATION_FROM_DB.get(reservation.status, ReservationStatus.pending),
            reject_reason=reservation.reject_reason,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
        )

    @staticmethod
    def _reservation_calendar_item(reservation: Reservation) -> ReservationCalendarItem:
        status_ = RESERVATION_FROM_DB.get(reservation.status, ReservationStatus.pending)
        return ReservationCalendarItem(
            id=reservation.id,
            reservation_no=reservation.reservation_no,
            device_id=reservation.device_id,
            applicant_id=reservation.applicant_id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            purpose=reservation.purpose,
            status=status_,
            title=f"{status_.value} reservation {reservation.reservation_no}",
        )

    @staticmethod
    def _repair_read(report: RepairReport) -> RepairReportRead:
        return RepairReportRead(
            id=report.id,
            device_id=report.device_id,
            reporter_id=report.reporter_id,
            fault_type=report.fault_type,
            description=report.description,
            status=RepairReportStatus(report.status),
            created_at=report.created_at,
            updated_at=report.updated_at,
        )

    @staticmethod
    def _work_order_read(work_order: WorkOrder) -> WorkOrderRead:
        return WorkOrderRead(
            id=work_order.id,
            repair_report_id=work_order.repair_report_id,
            assignee_id=work_order.assignee_id,
            priority=WorkOrderPriority(work_order.priority),
            status=WORK_ORDER_FROM_DB.get(work_order.status, WorkOrderStatus.pending),
            result=work_order.result,
            started_at=work_order.started_at,
            finished_at=work_order.finished_at,
            created_at=work_order.created_at,
            updated_at=work_order.updated_at,
        )


labops_service = LabOpsService()
