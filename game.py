import json
from json import JSONDecodeError
from pathlib import Path

from quiz import Quiz


STATE_FILE = Path(__file__).resolve().parent / "state.json"


class InputCancelled(Exception):
    """
    Ctrl+C 또는 EOF 입력이 발생했을 때 안전하게 종료하기 위한 예외
    """
    pass


class QuizGame:
    """
    퀴즈 게임 전체를 관리하는 클래스
    """

    def __init__(self):
        self.quizzes = []
        self.best_score = 0
        self.best_total = 0
        self.played_count = 0
        self.running = True

        self.load_state()

    def get_default_quizzes(self):
        """
        기본 퀴즈 데이터
        주제: Python 기초
        """
        return [
            Quiz(
                "Python에서 문자열을 나타내는 자료형은 무엇인가요?",
                ["int", "str", "bool", "list"],
                2
            ),
            Quiz(
                "조건에 따라 다른 코드를 실행할 때 사용하는 문법은 무엇인가요?",
                ["for", "if", "def", "class"],
                2
            ),
            Quiz(
                "여러 값을 순서대로 저장할 수 있는 자료형은 무엇인가요?",
                ["list", "bool", "int", "None"],
                1
            ),
            Quiz(
                "함수를 정의할 때 사용하는 키워드는 무엇인가요?",
                ["function", "def", "make", "return"],
                2
            ),
            Quiz(
                "클래스 내부에서 객체 자신을 가리킬 때 주로 사용하는 이름은 무엇인가요?",
                ["this", "me", "self", "object"],
                3
            )
        ]

    def get_score_percent(self, score, total):
        """
        맞힌 개수와 전체 문제 수를 이용해 100점 만점 점수를 계산한다.
        """
        if total == 0:
            return 0

        return round((score / total) * 100)

    def load_state(self):
        """
        state.json에서 데이터를 불러온다.
        파일이 없거나 손상된 경우 기본 데이터로 복구한다.
        """
        if not STATE_FILE.exists():
            print("🗂️ 저장 파일이 없어 기본 문제 세트로 시작합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.best_total = 0
            self.played_count = 0
            self.save_state()
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            loaded_quizzes = []

            for quiz_data in data.get("quizzes", []):
                try:
                    loaded_quizzes.append(Quiz.from_dict(quiz_data))
                except (KeyError, TypeError, ValueError):
                    print("🚧 일부 문제 데이터가 올바르지 않아 제외했습니다.")

            if not loaded_quizzes:
                print("🚧 저장된 문제가 없어 기본 문제 세트로 복구합니다.")
                loaded_quizzes = self.get_default_quizzes()

            self.quizzes = loaded_quizzes
            self.best_score = int(data.get("best_score", 0))
            self.best_total = int(data.get("best_total", 0))
            self.played_count = int(data.get("played_count", 0))

            best_percent = self.get_score_percent(self.best_score, self.best_total)

            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🔄 이전 진행 기록을 불러왔습니다.")
            print(f"   저장된 문제 : {len(self.quizzes)}개")
            print(f"   최고 기록   : {best_percent}점")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        except JSONDecodeError:
            print("🚧 저장 파일이 손상되어 기본 문제 세트로 복구합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.best_total = 0
            self.played_count = 0
            self.save_state()

        except OSError:
            print("🚧 저장 파일을 읽는 중 문제가 발생했습니다. 기본 문제 세트로 시작합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.best_total = 0
            self.played_count = 0

    def save_state(self):
        """
        현재 퀴즈 목록과 점수 기록을 state.json에 저장한다.
        """
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_total": self.best_total,
            "played_count": self.played_count
        }

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        except OSError:
            print("🚧 데이터 저장 중 오류가 발생했습니다.")

    def input_text(self, message):
        """
        문자열 입력 처리
        - 앞뒤 공백 제거
        - 빈 입력 처리
        - Ctrl+C, EOFError 처리
        """
        while True:
            try:
                value = input(message).strip()

                if value == "":
                    print("🚧 빈 입력은 사용할 수 없습니다. 다시 입력해주세요.")
                    continue

                return value

            except KeyboardInterrupt:
                print("\n🚧 입력이 중단되었습니다. 데이터를 저장하고 종료합니다.")
                raise InputCancelled

            except EOFError:
                print("\n🚧 입력 스트림이 종료되었습니다. 데이터를 저장하고 종료합니다.")
                raise InputCancelled

    def input_int(self, message, min_value, max_value):
        """
        숫자 입력 처리
        - 숫자가 아닌 입력 처리
        - 범위 밖 숫자 처리
        """
        while True:
            raw_value = self.input_text(message)

            try:
                number = int(raw_value)
            except ValueError:
                print(f"🚧 입력 오류: {min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            if number < min_value or number > max_value:
                print(f"🚧 입력 오류: {min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            return number

    def show_menu(self):
        """
        메인 메뉴를 출력한다.
        """
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("        ✨ Python Quest Lab ✨")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  1) 퀴즈 도전")
        print("  2) 새 문제 등록")
        print("  3) 문제 보관함")
        print("  4) 기록 확인")
        print("  5) 게임 종료")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def run(self):
        """
        게임 실행 메서드
        """
        while self.running:
            try:
                self.show_menu()
                choice = self.input_int("👉 번호 입력 > ", 1, 5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.show_quiz_list()
                elif choice == 4:
                    self.show_best_score()
                elif choice == 5:
                    self.exit_game()

            except InputCancelled:
                self.running = False

        self.save_state()
        print("✅ 프로그램을 안전하게 종료했습니다.")

    def play_quiz(self):
        """
        저장된 퀴즈를 출제하고 점수를 계산한다.
        """
        if not self.quizzes:
            print("\n🚧 아직 등록된 문제가 없습니다.")
            return

        score = 0
        total = len(self.quizzes)

        print()
        print("╔══════════════════════════════════════╗")
        print("        🚀 퀴즈 도전을 시작합니다")
        print("╚══════════════════════════════════════╝")
        print(f"총 {total}개의 문제가 준비되어 있습니다.")

        for index, quiz in enumerate(self.quizzes, start=1):
            print()
            print("────────────────────────────────────────")
            print(f"Q{index}. {quiz.question}")
            print("────────────────────────────────────────")

            for choice_index, choice in enumerate(quiz.choices, start=1):
                print(f"   {choice_index}) {choice}")

            print()
            user_answer = self.input_int("정답 번호 선택 > ", 1, 4)

            if quiz.check_answer(user_answer):
                print("🟢 맞았습니다!")
                score += 1
            else:
                print(f"🔴 아쉽습니다. 정답은 {quiz.answer}번입니다.")

        percent = self.get_score_percent(score, total)

        print()
        print("╔══════════════════════════════════════╗")
        print("              🎯 도전 결과")
        print("╠══════════════════════════════════════╣")
        print(f"   정답 수    : {score} / {total}")
        print(f"   환산 점수  : {percent}점")

        first_play = self.played_count == 0
        self.played_count += 1

        if first_play or score > self.best_score:
            self.best_score = score
            self.best_total = total
            print("   기록 상태  : 새로운 최고 기록입니다!")
        else:
            best_percent = self.get_score_percent(self.best_score, self.best_total)
            print(f"   기록 상태  : 최고 기록은 {best_percent}점입니다.")

        print("╚══════════════════════════════════════╝")

        self.save_state()

    def add_quiz(self):
        """
        새로운 퀴즈를 추가한다.
        """
        print()
        print("╭──────────────────────────────────────╮")
        print("        🧩 새 문제 등록")
        print("╰──────────────────────────────────────╯")

        question = self.input_text("문제 입력 > ")

        choices = []
        for index in range(1, 5):
            choice = self.input_text(f"선택지 {index} 입력 > ")
            choices.append(choice)

        answer = self.input_int("정답 번호 입력 (1-4) > ", 1, 4)

        new_quiz = Quiz(question, choices, answer)
        self.quizzes.append(new_quiz)

        self.save_state()

        print()
        print("✅ 새 문제가 문제 보관함에 저장되었습니다.")

    def show_quiz_list(self):
        """
        저장된 퀴즈 목록을 출력한다.
        """
        print()

        if not self.quizzes:
            print("🚧 문제 보관함이 비어 있습니다.")
            return

        print("╭──────────────────────────────────────╮")
        print("        📚 문제 보관함")
        print("╰──────────────────────────────────────╯")
        print(f"현재 저장된 문제 수: {len(self.quizzes)}개")
        print()

        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"{index:>2}. {quiz.question}")

        print()
        print("────────────────────────────────────────")

    def show_best_score(self):
        """
        최고 점수를 출력한다.
        """
        print()

        if self.played_count == 0:
            print("📊 아직 퀴즈 도전 기록이 없습니다.")
            return

        percent = self.get_score_percent(self.best_score, self.best_total)

        print("╭──────────────────────────────────────╮")
        print("        📊 나의 최고 기록")
        print("╰──────────────────────────────────────╯")
        print(f"최고 점수   : {percent}점")
        print(f"정답 개수   : {self.best_score} / {self.best_total}")
        print(f"도전 횟수   : {self.played_count}회")
        print("────────────────────────────────────────")

    def exit_game(self):
        """
        게임 종료 전 데이터를 저장한다.
        """
        print()
        print("👋 Python Quest Lab을 종료합니다.")
        self.save_state()
        self.running = False