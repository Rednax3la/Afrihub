from datetime import datetime, timedelta, timezone


def today_eat():
    return datetime.now(timezone(timedelta(hours=3))).date()


def sm2(ease_factor: float, interval: int, score: int) -> tuple[float, int]:
    if score >= 80:
        if interval == 0:
            new_interval = 1
        elif interval == 1:
            new_interval = 3
        else:
            new_interval = round(interval * ease_factor)
        new_ef = ease_factor + (0.1 - (5 - min(score // 20, 5)) * (0.08 + (5 - min(score // 20, 5)) * 0.02))
    elif score >= 60:
        new_interval = interval
        new_ef = ease_factor
    else:
        new_interval = 1
        new_ef = max(1.3, ease_factor - 0.2)
    return round(min(new_ef, 2.5), 2), new_interval
