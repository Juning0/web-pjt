import asyncio
import math
from collections import defaultdict, deque
from datetime import date, datetime, timedelta
from time import monotonic


class ChatRateLimiter:
    def __init__(
        self,
        requests_per_window: int,
        window_seconds: int,
        daily_per_client: int,
        daily_global: int,
    ):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.daily_per_client = daily_per_client
        self.daily_global = daily_global

        self.recent_requests = defaultdict(deque)
        self.client_daily_counts = defaultdict(int)
        self.global_daily_count = 0
        self.current_date = date.today()
        self.lock = asyncio.Lock()

    async def check(self, client_id: str):
        async with self.lock:
            self._reset_daily_counts()

            now = monotonic()
            requests = self.recent_requests[client_id]

            while requests and now - requests[0] >= self.window_seconds:
                requests.popleft()

            if len(requests) >= self.requests_per_window:
                retry_after = math.ceil(
                    self.window_seconds - (now - requests[0])
                )
                return False, retry_after, (
                    f"요청이 너무 빠릅니다. {retry_after}초 후 다시 시도해 주세요."
                )

            if self.client_daily_counts[client_id] >= self.daily_per_client:
                return False, self._seconds_until_tomorrow(), (
                    "오늘 사용할 수 있는 챗봇 요청 횟수를 모두 사용했습니다."
                )

            if self.global_daily_count >= self.daily_global:
                return False, self._seconds_until_tomorrow(), (
                    "오늘 서비스의 챗봇 사용 한도에 도달했습니다."
                )

            requests.append(now)
            self.client_daily_counts[client_id] += 1
            self.global_daily_count += 1

            return True, 0, ""

    def _reset_daily_counts(self):
        today = date.today()

        if self.current_date != today:
            self.current_date = today
            self.client_daily_counts.clear()
            self.global_daily_count = 0

    def _seconds_until_tomorrow(self):
        now = datetime.now()
        tomorrow = datetime.combine(
            now.date() + timedelta(days=1),
            datetime.min.time(),
        )
        return max(1, math.ceil((tomorrow - now).total_seconds()))