import argparse
import asyncio
import statistics
import time

import httpx


async def login(client: httpx.AsyncClient, base_url: str, username: str, password: str) -> str:
    resp = await client.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


async def single_request(
    client: httpx.AsyncClient,
    base_url: str,
    token: str,
    amount: int,
) -> tuple[bool, float]:
    started = time.perf_counter()
    try:
        resp = await client.post(
            f"{base_url}/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={"tx_type": "income", "amount": amount, "description": "load-test"},
            timeout=10.0,
        )
        ok = resp.status_code == 201
    except Exception:
        ok = False
    elapsed_ms = (time.perf_counter() - started) * 1000
    return ok, elapsed_ms


async def run_load(base_url: str, users: int, requests_count: int, username: str, password: str):
    async with httpx.AsyncClient() as client:
        token = await login(client, base_url, username, password)

        semaphore = asyncio.Semaphore(users)
        results = []

        async def worker(i: int):
            async with semaphore:
                return await single_request(client, base_url, token, 1000 + i)

        started = time.perf_counter()
        tasks = [asyncio.create_task(worker(i)) for i in range(requests_count)]
        for task in asyncio.as_completed(tasks):
            results.append(await task)
        total_time = time.perf_counter() - started

    successes = [r for r in results if r[0]]
    failures = len(results) - len(successes)
    latencies = [r[1] for r in results]

    avg_ms = statistics.mean(latencies) if latencies else 0.0
    p95_ms = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 100 else max(latencies, default=0.0)
    rps = len(results) / total_time if total_time > 0 else 0.0

    print("=== Load Test Result ===")
    print(f"Base URL: {base_url}")
    print(f"Concurrent users: {users}")
    print(f"Total requests: {len(results)}")
    print(f"Success: {len(successes)}")
    print(f"Failed: {failures}")
    print(f"Total time (sec): {total_time:.2f}")
    print(f"Requests/sec: {rps:.2f}")
    print(f"Avg latency (ms): {avg_ms:.2f}")
    print(f"P95 latency (ms): {p95_ms:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Simple load test for Fintech MVP API")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--users", type=int, default=20)
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--username", default="demo")
    parser.add_argument("--password", default="demo123")
    args = parser.parse_args()

    asyncio.run(
        run_load(
            base_url=args.base_url,
            users=args.users,
            requests_count=args.requests,
            username=args.username,
            password=args.password,
        )
    )


if __name__ == "__main__":
    main()
