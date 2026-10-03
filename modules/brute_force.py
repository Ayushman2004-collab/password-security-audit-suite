import hashlib
import itertools
import string
import time

CHARSETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "letters": string.ascii_letters,
    "lowercase_digits": string.ascii_lowercase + string.digits,
    "letters_digits": string.ascii_letters + string.digits,
    "digits": string.digits,
    "letters_digits_symbols": string.ascii_letters + string.digits + string.punctuation,
}


def search_space_size(max_length: int, charset_name: str) -> int:
    charset = CHARSETS.get(charset_name, CHARSETS["lowercase"])
    return sum(len(charset) ** length for length in range(1, max_length + 1))


def estimate_crack_time(max_length: int, charset_name: str, rate: float) -> dict:
    space = search_space_size(max_length, charset_name)
    seconds = (space / rate) if rate > 0 else None
    return {"search_space": space, "seconds": seconds}


def _human_time(seconds):
    if seconds is None:
        return "Unknown"
    if seconds < 1:
        return f"{seconds:.3f} seconds"
    units = [("year", 31557600), ("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    for name, size in units:
        if seconds >= size:
            value = seconds / size
            return f"{value:.2f} {name}{'' if value == 1 else 's'}"
    return f"{seconds:.3f} seconds"


def bounded_bruteforce(target: str, max_length: int, charset_name: str) -> dict:
    charset = CHARSETS.get(charset_name, CHARSETS["lowercase"])
    start = time.perf_counter()
    attempts = 0
    target_hash = hashlib.sha256(target.encode("utf-8")).hexdigest()

    for length in range(1, max_length + 1):
        for item in itertools.product(charset, repeat=length):
            candidate = "".join(item)
            attempts += 1
            if hashlib.sha256(candidate.encode("utf-8")).hexdigest() == target_hash:
                elapsed = time.perf_counter() - start
                rate = attempts / elapsed if elapsed else float(attempts)
                estimate = estimate_crack_time(max_length, charset_name, rate)
                return {
                    "found": True, "candidate": candidate, "attempts": attempts,
                    "elapsed": round(elapsed, 6), "rate": round(rate, 2),
                    "search_space": estimate["search_space"],
                    "estimated_worst_case": _human_time(estimate["seconds"]),
                }

    elapsed = time.perf_counter() - start
    rate = attempts / elapsed if elapsed else float(attempts)
    estimate = estimate_crack_time(max_length, charset_name, rate)
    return {
        "found": False, "candidate": None, "attempts": attempts,
        "elapsed": round(elapsed, 6), "rate": round(rate, 2),
        "search_space": estimate["search_space"],
        "estimated_worst_case": _human_time(estimate["seconds"]),
    }
