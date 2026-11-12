"""
퀴즈 데이터가 많아졌을 때(1,000개 이상) 프로그램의 주요 동작이
얼마나 걸리고 메모리를 얼마나 쓰는지 측정하는 스크립트.

- state.json은 읽거나 바꾸지 않는다. 측정용 데이터는 메모리 안에서만 만든다.
- 표준 라이브러리(time, tracemalloc, json, random)만 사용한다.

실행 방법: python benchmark.py
"""

import json
import random
import time
import tracemalloc

from quiz import Quiz


def make_quizzes(count):
    """측정용 가짜 퀴즈를 count개 만든다."""
    quizzes = []

    for number in range(count):
        quizzes.append(
            Quiz(
                f"측정용 문제 {number}번: Python 기초 개념을 묻는 문제입니다.",
                ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
                (number % 4) + 1,
                f"측정용 힌트 {number}번입니다."
            )
        )

    return quizzes


def measure(task):
    """task 함수를 한 번 실행하고 걸린 시간(밀리초)과 결과를 돌려준다."""
    start = time.perf_counter()
    result = task()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, result


def run_benchmark(count):
    tracemalloc.start()

    # 1. 퀴즈 객체 만들기
    create_ms, quizzes = measure(lambda: make_quizzes(count))
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 2. 저장: 객체 → dict → JSON 문자열 (save_state와 같은 방식)
    save_ms, text = measure(
        lambda: json.dumps(
            {"quizzes": [quiz.to_dict() for quiz in quizzes]},
            ensure_ascii=False,
            indent=4
        )
    )
    file_kb = len(text.encode("utf-8")) / 1024

    # 3. 불러오기: JSON 문자열 → dict → 객체 (load_state와 같은 방식)
    load_ms, _ = measure(
        lambda: [Quiz.from_dict(data) for data in json.loads(text)["quizzes"]]
    )

    # 4. 랜덤 출제: 10문제 뽑기 (play_quiz와 같은 방식)
    sample_ms, _ = measure(lambda: random.sample(quizzes, 10))

    # 5. 검색: 마지막 문제를 처음부터 찾아보기 (가장 오래 걸리는 경우)
    target = quizzes[-1].question
    search_ms, _ = measure(
        lambda: next(quiz for quiz in quizzes if quiz.question == target)
    )

    # 6. 삭제: 맨 앞 문제 삭제 (뒤의 문제들이 한 칸씩 당겨지는 가장 느린 경우)
    delete_ms, _ = measure(lambda: quizzes.pop(0))

    print(f"\n[퀴즈 {count:,}개]")
    print(f"  객체 생성       : {create_ms:8.2f} ms")
    print(f"  저장 (JSON 변환): {save_ms:8.2f} ms")
    print(f"  불러오기        : {load_ms:8.2f} ms")
    print(f"  랜덤 10문제 출제: {sample_ms:8.3f} ms")
    print(f"  검색 (최악)     : {search_ms:8.3f} ms")
    print(f"  삭제 (최악)     : {delete_ms:8.3f} ms")
    print(f"  JSON 파일 크기  : {file_kb:8.1f} KB")
    print(f"  최대 메모리 사용: {peak_bytes / 1024 / 1024:8.2f} MB")


def main():
    print("퀴즈 데이터 양에 따른 성능 측정")
    print("(측정값은 컴퓨터 성능에 따라 달라집니다.)")

    for count in [1_000, 10_000, 100_000]:
        run_benchmark(count)


if __name__ == "__main__":
    main()
