from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID, uuid4
from typing import TypeVar

from fastapi import HTTPException, status

from app.schemas.common import PageData, utc_now
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint
from app.schemas.device import DeviceCreate, DeviceRead, DeviceStatus, DeviceUpdate
from app.schemas.repair_report import RepairReportCreate, RepairReportRead, RepairReportStatus
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationStatus
from app.schemas.work_order import WorkOrderCreate, WorkOrderPriority, WorkOrderRead, WorkOrderStatus

T = TypeVar("T")
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
DEVICE_A_ID = UUID("10000000-0000-0000-0000-000000000001")
DEVICE_B_ID = UUID("10000000-0000-0000-0000-000000000002")
DEVICE_C_ID = UUID("10000000-0000-0000-0000-000000000003")
RESERVATION_A_ID = UUID("20000000-0000-0000-0000-000000000001")
RESERVATION_B_ID = UUID("20000000-0000-0000-0000-000000000002")
REPAIR_A_ID = UUID("30000000-0000-0000-0000-000000000001")
REPAIR_B_ID = UUID("30000000-0000-0000-0000-000000000002")
WORK_ORDER_A_ID = UUID("40000000-0000-0000-0000-000000000001")
WORK_ORDER_B_ID = UUID("40000000-0000-0000-0000-000000000002")


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def _page(items: list[T], page: int, page_size: int) -> PageData[T]:
    start = (page - 1) * page_size
    end = start + page_size
    return PageData(items=items[start:end], page=page, page_size=page_size, total=len(items))


def _matches(value: object, expected: object | None) -> bool:
    return expected is None or value == expected


def _sort_by_updated_at(items: Iterable[T]) -> list[T]:
    return sorted(items, key=lambda item: item.updated_at, reverse=True)


@dataclass
class LabOpsService:
    devices: dict[UUID, DeviceRead] = field(default_factory=dict)
    reservations: dict[UUID, ReservationRead] = field(default_factory=dict)
    repair_reports: dict[UUID, RepairReportRead] = field(default_factory=dict)
    work_orders: dict[UUID, WorkOrderRead] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.devices:
            self._seed()

    def _seed(self) -> None:
        now = utc_now()
        tomorrow = datetime.combine(date.today() + timedelta(days=1), time(9, 0), tzinfo=timezone.utc)
        self.devices = {
            DEVICE_A_ID: DeviceRead(
                id=DEVICE_A_ID,
                code="DEV-001",
                name="High-speed centrifuge",
                category_id=None,
                lab_id=None,
                manager_id=DEMO_USER_ID,
                status=DeviceStatus.available,
                health_score=96.5,
                purchase_date=date(2025, 9, 1),
                created_at=now - timedelta(days=80),
                updated_at=now - timedelta(hours=2),
            ),
            DEVICE_B_ID: DeviceRead(
                id=DEVICE_B_ID,
                code="DEV-002",
                name="Environmental test chamber",
                category_id=None,
                lab_id=None,
                manager_id=DEMO_USER_ID,
                status=DeviceStatus.maintenance,
                health_score=74.0,
                purchase_date=date(2024, 5, 12),
                created_at=now - timedelta(days=120),
                updated_at=now - timedelta(hours=1),
            ),
            DEVICE_C_ID: DeviceRead(
                id=DEVICE_C_ID,
                code="DEV-003",
                name="3D optical profiler",
                category_id=None,
                lab_id=None,
                manager_id=DEMO_USER_ID,
                status=DeviceStatus.in_use,
                health_score=88.0,
                purchase_date=date(2025, 1, 20),
                created_at=now - timedelta(days=95),
                updated_at=now - timedelta(hours=3),
            ),
        }
        self.reservations = {
            RESERVATION_A_ID: ReservationRead(
                id=RESERVATION_A_ID,
                device_id=DEVICE_A_ID,
                applicant_id=DEMO_USER_ID,
                approver_id=DEMO_USER_ID,
                start_time=tomorrow,
                end_time=tomorrow + timedelta(hours=2),
                purpose="Material sample analysis",
                status=ReservationStatus.approved,
                reject_reason=None,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(hours=12),
            ),
            RESERVATION_B_ID: ReservationRead(
                id=RESERVATION_B_ID,
                device_id=DEVICE_C_ID,
                applicant_id=DEMO_USER_ID,
                approver_id=None,
                start_time=tomorrow + timedelta(hours=4),
                end_time=tomorrow + timedelta(hours=6),
                purpose="Surface morphology measurement",
                status=ReservationStatus.pending,
                reject_reason=None,
                created_at=now - timedelta(hours=5),
                updated_at=now - timedelta(hours=5),
            ),
        }
        self.repair_reports = {
            REPAIR_A_ID: RepairReportRead(
                id=REPAIR_A_ID,
                device_id=DEVICE_B_ID,
                reporter_id=DEMO_USER_ID,
                fault_type="hardware",
                description="Startup vibration exceeds the warning threshold.",
                status=RepairReportStatus.assigned,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(hours=8),
            ),
            REPAIR_B_ID: RepairReportRead(
                id=REPAIR_B_ID,
                device_id=DEVICE_C_ID,
                reporter_id=DEMO_USER_ID,
                fault_type="calibration",
                description="Measurement baseline drift requires recalibration.",
                status=RepairReportStatus.submitted,
                created_at=now - timedelta(hours=9),
                updated_at=now - timedelta(hours=9),
            ),
        }
        self.work_orders = {
            WORK_ORDER_A_ID: WorkOrderRead(
                id=WORK_ORDER_A_ID,
                repair_report_id=REPAIR_A_ID,
                assignee_id=DEMO_USER_ID,
                priority=WorkOrderPriority.high,
                status=WorkOrderStatus.processing,
                result=None,
                started_at=now - timedelta(hours=7),
                finished_at=None,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(hours=7),
            ),
            WORK_ORDER_B_ID: WorkOrderRead(
                id=WORK_ORDER_B_ID,
                repair_report_id=REPAIR_B_ID,
                assignee_id=None,
                priority=WorkOrderPriority.medium,
                status=WorkOrderStatus.pending,
                result=None,
                started_at=None,
                finished_at=None,
                created_at=now - timedelta(hours=8),
                updated_at=now - timedelta(hours=8),
            ),
        }

    def list_devices(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None = None,
        lab_id: UUID | None = None,
        category_id: UUID | None = None,
        status: DeviceStatus | None = None,
    ) -> PageData[DeviceRead]:
        normalized_keyword = keyword.lower().strip() if keyword else None
        items = [
            item
            for item in self.devices.values()
            if _matches(item.lab_id, lab_id)
            and _matches(item.category_id, category_id)
            and _matches(item.status, status)
            and (
                normalized_keyword is None
                or normalized_keyword in item.code.lower()
                or normalized_keyword in item.name.lower()
            )
        ]
        return _page(_sort_by_updated_at(items), page, page_size)

    def create_device(self, payload: DeviceCreate) -> DeviceRead:
        if any(item.code == payload.code for item in self.devices.values()):
            raise _conflict("device code already exists")
        now = utc_now()
        device = DeviceRead(id=uuid4(), created_at=now, updated_at=now, **payload.model_dump())
        self.devices[device.id] = device
        return device

    def get_device(self, device_id: UUID) -> DeviceRead:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise _not_found("device") from exc

    def update_device(self, device_id: UUID, payload: DeviceUpdate) -> DeviceRead:
        current = self.get_device(device_id)
        changes = payload.model_dump(exclude_unset=True)
        if "code" in changes and any(item.id != device_id and item.code == changes["code"] for item in self.devices.values()):
            raise _conflict("device code already exists")
        updated = current.model_copy(update=changes | {"updated_at": utc_now()})
        self.devices[device_id] = updated
        return updated

    def update_device_status(self, device_id: UUID, status_: DeviceStatus) -> DeviceRead:
        return self.update_device(device_id, DeviceUpdate(status=status_))

    def delete_device(self, device_id: UUID) -> DeviceRead:
        current = self.get_device(device_id)
        return self.update_device(device_id, DeviceUpdate(status=DeviceStatus.disabled))

    def list_reservations(
        self,
        *,
        page: int,
        page_size: int,
        device_id: UUID | None = None,
        applicant_id: UUID | None = None,
        status: ReservationStatus | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> PageData[ReservationRead]:
        items = [
            item
            for item in self.reservations.values()
            if _matches(item.device_id, device_id)
            and _matches(item.applicant_id, applicant_id)
            and _matches(item.status, status)
            and (start_time is None or item.end_time >= start_time)
            and (end_time is None or item.start_time <= end_time)
        ]
        return _page(_sort_by_updated_at(items), page, page_size)

    def create_reservation(self, payload: ReservationCreate, applicant_id: UUID) -> ReservationRead:
        self.get_device(payload.device_id)
        self._ensure_no_reservation_conflict(payload.device_id, payload.start_time, payload.end_time)
        now = utc_now()
        reservation = ReservationRead(
            id=uuid4(),
            applicant_id=applicant_id,
            approver_id=None,
            status=ReservationStatus.pending,
            reject_reason=None,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        self.reservations[reservation.id] = reservation
        return reservation

    def get_reservation(self, reservation_id: UUID) -> ReservationRead:
        try:
            return self.reservations[reservation_id]
        except KeyError as exc:
            raise _not_found("reservation") from exc

    def approve_reservation(self, reservation_id: UUID, approver_id: UUID) -> ReservationRead:
        current = self.get_reservation(reservation_id)
        self._ensure_no_reservation_conflict(current.device_id, current.start_time, current.end_time, reservation_id)
        return self._save_reservation(
            current.model_copy(
                update={
                    "status": ReservationStatus.approved,
                    "approver_id": approver_id,
                    "reject_reason": None,
                    "updated_at": utc_now(),
                }
            )
        )

    def reject_reservation(self, reservation_id: UUID, approver_id: UUID, reject_reason: str) -> ReservationRead:
        current = self.get_reservation(reservation_id)
        return self._save_reservation(
            current.model_copy(
                update={
                    "status": ReservationStatus.rejected,
                    "approver_id": approver_id,
                    "reject_reason": reject_reason,
                    "updated_at": utc_now(),
                }
            )
        )

    def cancel_reservation(self, reservation_id: UUID) -> ReservationRead:
        current = self.get_reservation(reservation_id)
        return self._save_reservation(current.model_copy(update={"status": ReservationStatus.canceled, "updated_at": utc_now()}))

    def _save_reservation(self, reservation: ReservationRead) -> ReservationRead:
        self.reservations[reservation.id] = reservation
        return reservation

    def _ensure_no_reservation_conflict(
        self,
        device_id: UUID,
        start_time: datetime,
        end_time: datetime,
        ignored_reservation_id: UUID | None = None,
    ) -> None:
        conflict_statuses = {ReservationStatus.approved}
        for item in self.reservations.values():
            if item.id == ignored_reservation_id or item.device_id != device_id or item.status not in conflict_statuses:
                continue
            if start_time < item.end_time and end_time > item.start_time:
                raise _conflict("reservation time conflicts with an approved reservation")

    def list_repair_reports(
        self,
        *,
        page: int,
        page_size: int,
        device_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: RepairReportStatus | None = None,
        fault_type: str | None = None,
    ) -> PageData[RepairReportRead]:
        normalized_fault_type = fault_type.lower().strip() if fault_type else None
        items = [
            item
            for item in self.repair_reports.values()
            if _matches(item.device_id, device_id)
            and _matches(item.reporter_id, reporter_id)
            and _matches(item.status, status)
            and (normalized_fault_type is None or normalized_fault_type in item.fault_type.lower())
        ]
        return _page(_sort_by_updated_at(items), page, page_size)

    def create_repair_report(self, payload: RepairReportCreate, reporter_id: UUID) -> RepairReportRead:
        self.get_device(payload.device_id)
        now = utc_now()
        report = RepairReportRead(
            id=uuid4(),
            reporter_id=reporter_id,
            status=RepairReportStatus.submitted,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        self.repair_reports[report.id] = report
        return report

    def get_repair_report(self, report_id: UUID) -> RepairReportRead:
        try:
            return self.repair_reports[report_id]
        except KeyError as exc:
            raise _not_found("repair report") from exc

    def list_work_orders(
        self,
        *,
        page: int,
        page_size: int,
        assignee_id: UUID | None = None,
        status: WorkOrderStatus | None = None,
        priority: WorkOrderPriority | None = None,
    ) -> PageData[WorkOrderRead]:
        items = [
            item
            for item in self.work_orders.values()
            if _matches(item.assignee_id, assignee_id) and _matches(item.status, status) and _matches(item.priority, priority)
        ]
        return _page(_sort_by_updated_at(items), page, page_size)

    def create_work_order(self, payload: WorkOrderCreate) -> WorkOrderRead:
        self.get_repair_report(payload.repair_report_id)
        now = utc_now()
        work_order = WorkOrderRead(
            id=uuid4(),
            status=WorkOrderStatus.pending,
            result=None,
            started_at=None,
            finished_at=None,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        self.work_orders[work_order.id] = work_order
        self._update_repair_status(payload.repair_report_id, RepairReportStatus.assigned)
        return work_order

    def get_work_order(self, work_order_id: UUID) -> WorkOrderRead:
        try:
            return self.work_orders[work_order_id]
        except KeyError as exc:
            raise _not_found("work order") from exc

    def update_work_order_status(self, work_order_id: UUID, status_: WorkOrderStatus) -> WorkOrderRead:
        current = self.get_work_order(work_order_id)
        now = utc_now()
        changes: dict[str, object] = {"status": status_, "updated_at": now}
        if status_ == WorkOrderStatus.processing and current.started_at is None:
            changes["started_at"] = now
        if status_ == WorkOrderStatus.finished:
            changes["finished_at"] = now
        updated = current.model_copy(update=changes)
        self.work_orders[work_order_id] = updated
        return updated

    def finish_work_order(self, work_order_id: UUID, result: str) -> WorkOrderRead:
        current = self.get_work_order(work_order_id)
        now = utc_now()
        updated = current.model_copy(
            update={
                "status": WorkOrderStatus.finished,
                "result": result,
                "finished_at": now,
                "updated_at": now,
            }
        )
        self.work_orders[work_order_id] = updated
        self._update_repair_status(updated.repair_report_id, RepairReportStatus.closed)
        return updated

    def _update_repair_status(self, report_id: UUID, status_: RepairReportStatus) -> None:
        report = self.get_repair_report(report_id)
        self.repair_reports[report_id] = report.model_copy(update={"status": status_, "updated_at": utc_now()})

    def dashboard_summary(self) -> DashboardSummary:
        return DashboardSummary(
            device_total=len(self.devices),
            device_available=sum(1 for item in self.devices.values() if item.status == DeviceStatus.available),
            today_reservations=sum(1 for item in self.reservations.values() if item.start_time.date() == date.today()),
            pending_repairs=sum(1 for item in self.repair_reports.values() if item.status == RepairReportStatus.submitted),
            open_work_orders=sum(
                1
                for item in self.work_orders.values()
                if item.status in {WorkOrderStatus.pending, WorkOrderStatus.processing}
            ),
        )

    def device_utilization(self, start_date: date | None, end_date: date | None, lab_id: UUID | None) -> list[TrendPoint]:
        return self._trend(start_date, end_date, lab_id, lambda index: 58 + (index * 7) % 32)

    def repair_trend(self, start_date: date | None, end_date: date | None, lab_id: UUID | None) -> list[TrendPoint]:
        return self._trend(start_date, end_date, lab_id, lambda index: float((index % 4) + 1))

    def reservation_status(self) -> list[StatusCount]:
        return self._status_counts(ReservationStatus, (item.status for item in self.reservations.values()))

    @staticmethod
    def _status_counts(enum_cls: type, statuses: Iterable[str]) -> list[StatusCount]:
        counts = {status_: 0 for status_ in enum_cls}
        for status_ in statuses:
            counts[status_] += 1
        return [StatusCount(status=status_, count=count) for status_, count in counts.items()]

    @staticmethod
    def _trend(
        start_date: date | None,
        end_date: date | None,
        lab_id: UUID | None,
        value_for_day: Callable[[int], float],
    ) -> list[TrendPoint]:
        _ = lab_id
        start = start_date or date.today() - timedelta(days=6)
        end = end_date or start + timedelta(days=6)
        if end < start:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be later than start_date")
        days = min((end - start).days + 1, 31)
        return [TrendPoint(date=start + timedelta(days=index), value=value_for_day(index)) for index in range(days)]


labops_service = LabOpsService()
