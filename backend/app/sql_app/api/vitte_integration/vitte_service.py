from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Callable, Hashable, Optional, TypeVar

from sql_app.api.vitte_integration.vitte_schemas import VitteStatus

T = TypeVar("T")


@dataclass
class _VitteSyncState:
    last_catalog_sync_at: Optional[datetime] = None
    last_consumption_sync_by_card: dict[Hashable, datetime] = None

    def __post_init__(self) -> None:
        if self.last_consumption_sync_by_card is None:
            self.last_consumption_sync_by_card = {}


class VitteService:
    status_cache_ttl = timedelta(seconds=15)
    catalog_sync_ttl = timedelta(minutes=30)
    consumption_sync_ttl = timedelta(seconds=10)
    circuit_breaker_failures = 3
    circuit_breaker_cooldown = timedelta(seconds=30)

    def __init__(self) -> None:
        self._lock = Lock()
        self._sync_state = _VitteSyncState()
        self._status = "degraded"
        self._last_status_check_at: Optional[datetime] = None
        self._last_success_at: Optional[datetime] = None
        self._last_error_at: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._consecutive_failures = 0
        self._circuit_open_until: Optional[datetime] = None
        self._catalog_sync_lock = Lock()
        self._consumption_sync_locks: dict[Hashable, Lock] = {}

    def get_status(self, health_check: Callable[[], tuple[bool, str]], *, force: bool = False) -> VitteStatus:
        now = datetime.now()
        if not force and self._is_status_cache_fresh(now):
            return self._snapshot(now)
        if not force and self._is_circuit_open(now):
            return self._snapshot(now)

        try:
            online, message = health_check()
        except Exception as err:
            self._mark_failure(err)
            return self._snapshot(datetime.now())

        if online:
            self._mark_success()
        else:
            self._mark_failure(message)
        return self._snapshot(datetime.now())

    def can_attempt_vitte(self, health_check: Callable[[], tuple[bool, str]]) -> bool:
        return self.get_status(health_check).online

    def sync_catalog_if_due(
        self,
        sync_fn: Callable[[], T],
        health_check: Callable[[], tuple[bool, str]],
        *,
        force: bool = False,
    ) -> bool:
        now = datetime.now()
        if not force and self._sync_state.last_catalog_sync_at is not None:
            if now - self._sync_state.last_catalog_sync_at < self.catalog_sync_ttl:
                return False

        if not self.can_attempt_vitte(health_check):
            return False

        if not self._catalog_sync_lock.acquire(blocking=False):
            return False

        try:
            now = datetime.now()
            if not force and self._sync_state.last_catalog_sync_at is not None:
                if now - self._sync_state.last_catalog_sync_at < self.catalog_sync_ttl:
                    return False
            sync_fn()
            with self._lock:
                self._sync_state.last_catalog_sync_at = datetime.now()
            self._mark_success()
            return True
        except Exception as err:
            self._mark_failure(err)
            return False
        finally:
            self._catalog_sync_lock.release()

    def sync_consumptions_if_due(
        self,
        tarjeta_id: Hashable,
        sync_fn: Callable[[], T],
        health_check: Callable[[], tuple[bool, str]],
        *,
        force: bool = False,
    ) -> bool:
        now = datetime.now()
        last_sync = self._sync_state.last_consumption_sync_by_card.get(tarjeta_id)
        if not force and last_sync is not None and now - last_sync < self.consumption_sync_ttl:
            return False

        if not self.can_attempt_vitte(health_check):
            return False

        lock = self._get_consumption_lock(tarjeta_id)
        if not lock.acquire(blocking=False):
            return False

        try:
            now = datetime.now()
            last_sync = self._sync_state.last_consumption_sync_by_card.get(tarjeta_id)
            if not force and last_sync is not None and now - last_sync < self.consumption_sync_ttl:
                return False
            sync_fn()
            with self._lock:
                self._sync_state.last_consumption_sync_by_card[tarjeta_id] = datetime.now()
            self._mark_success()
            return True
        except Exception as err:
            self._mark_failure(err)
            return False
        finally:
            lock.release()

    def require_online(self, health_check: Callable[[], tuple[bool, str]]) -> None:
        status = self.get_status(health_check)
        if not status.online:
            raise RuntimeError(status.last_error or "Vitte no esta disponible")

    def _get_consumption_lock(self, tarjeta_id: Hashable) -> Lock:
        with self._lock:
            if tarjeta_id not in self._consumption_sync_locks:
                self._consumption_sync_locks[tarjeta_id] = Lock()
            return self._consumption_sync_locks[tarjeta_id]

    def _is_status_cache_fresh(self, now: datetime) -> bool:
        return self._last_status_check_at is not None and now - self._last_status_check_at < self.status_cache_ttl

    def _is_circuit_open(self, now: datetime) -> bool:
        return self._circuit_open_until is not None and now < self._circuit_open_until

    def _mark_success(self) -> None:
        with self._lock:
            now = datetime.now()
            self._status = "online"
            self._last_status_check_at = now
            self._last_success_at = now
            self._last_error = None
            self._consecutive_failures = 0
            self._circuit_open_until = None

    def _mark_failure(self, err: object) -> None:
        with self._lock:
            now = datetime.now()
            self._last_status_check_at = now
            self._last_error_at = now
            self._last_error = str(err)
            self._consecutive_failures += 1
            self._status = "offline" if self._consecutive_failures >= self.circuit_breaker_failures else "degraded"
            if self._consecutive_failures >= self.circuit_breaker_failures:
                self._circuit_open_until = now + self.circuit_breaker_cooldown

    def _snapshot(self, now: datetime) -> VitteStatus:
        with self._lock:
            circuit_open = self._is_circuit_open(now)
            status = "offline" if circuit_open else self._status
            cached_for = 0
            if self._last_status_check_at is not None:
                cache_until = self._last_status_check_at + self.status_cache_ttl
                cached_for = max(0, int((cache_until - now).total_seconds()))
            return VitteStatus(
                status=status,
                online=status == "online",
                last_success_at=self._last_success_at,
                last_error_at=self._last_error_at,
                last_error=self._last_error,
                cached_for_seconds=cached_for,
                circuit_open_until=self._circuit_open_until if circuit_open else None,
                catalog_last_sync_at=self._sync_state.last_catalog_sync_at,
            )


vitte_service = VitteService()
