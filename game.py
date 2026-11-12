import json
import random
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

from quiz import Quiz


STATE_FILE = Path(__file__).resolve().parent / "state.json"
BACKUP_FILE = STATE_FILE.with_name("state.json.bak")
TEMP_FILE = STATE_FILE.with_name("state.json.tmp")


class InputCancelled(Exception):
    pass


class QuizGame:
    def __init__(self):
        self.quizzes = []
        self.best_score = 0
        self.best_total = 0
        self.played_count = 0
        self.history = []
        self.running = True
        self.load_state()

    def get_default_quizzes(self):
        return [
            Quiz(
                "Python에서 문자열을 나타내는 자료형은 무엇인가요?",
                ["int", "str", "bool", "list"],
                2,
                "문자열은 문자나 문장을 저장하는 자료형입니다. 보통 따옴표로 감싸서 표현합니다."
            ),
            Quiz(
                "조건에 따라 다른 코드를 실행할 때 사용하는 문법은 무엇인가요?",
                ["for", "if", "def", "class"],
                2,
                "조건이 참일 때 특정 코드를 실행하게 만드는 문법입니다."
            ),
            Quiz(
                "여러 값을 순서대로 저장할 수 있는 자료형은 무엇인가요?",
                ["list", "bool", "int", "None"],
                1,
                "대괄호 []를 사용하며, 여러 값을 순서대로 저장할 수 있습니다."
            ),
            Quiz(
                "함수를 정의할 때 사용하는 키워드는 무엇인가요?",
                ["function", "def", "make", "return"],
                2,
                "함수를 만들 때 사용하는 키워드이며, define의 줄임말처럼 보입니다."
            ),
            Quiz(
                "클래스 내부에서 객체 자신을 가리킬 때 주로 사용하는 이름은 무엇인가요?",
                ["this", "me", "self", "object"],
                3,
                "파이썬 클래스의 메서드에서 첫 번째 매개변수로 자주 사용되며, 객체 자기 자신을 의미합니다."
            ),
            Quiz(
                "Python에서 반복문을 만들 때 사용하는 키워드는 무엇인가요?",
                ["repeat", "loop", "for", "again"],
                3,
                "리스트나 문자열처럼 여러 값을 하나씩 꺼내서 처리할 때 자주 사용하는 키워드입니다."
            ),
            Quiz(
                "Python에서 참(True) 또는 거짓(False)을 나타내는 자료형은 무엇인가요?",
                ["str", "bool", "int", "list"],
                2,
                "조건문의 결과처럼 참과 거짓을 표현할 때 사용하는 자료형입니다."
            )
        ]

    def get_score_percent(self, score, total):
        if total == 0:
            return 0
        return round((score / total) * 100)

    def load_state(self):
        if not STATE_FILE.exists():
            print("🗂️ 저장 파일이 없어 기본 문제 세트로 시작합니다.")
            self.quizzes = self.get_default_quizzes()
            self.save_state()
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("저장 파일의 최상위 구조가 올바르지 않습니다.")

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
            self.best_score = float(data.get("best_score", 0))
            self.best_total = int(data.get("best_total", 0))
            self.played_count = int(data.get("played_count", 0))
            self.history = [
                record for record in data.get("history", [])
                if isinstance(record, dict)
            ]

            best_percent = self.get_score_percent(self.best_score, self.best_total)

            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🔄 이전 진행 기록을 불러왔습니다.")
            print(f"   저장된 문제 : {len(self.quizzes)}개")
            print(f"   최고 기록   : {best_percent}점")
            print(f"   전체 기록   : {len(self.history)}개")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        except (JSONDecodeError, ValueError, TypeError, AttributeError):
            # JSON 문법 오류, UTF-8이 아닌 파일, 잘못된 값/구조를 모두 손상으로 처리
            print("🚧 저장 파일이 손상되어 기본 문제 세트로 복구합니다.")
            self.backup_broken_state()
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.best_total = 0
            self.played_count = 0
            self.history = []
            self.save_state()

        except OSError:
            print("🚧 저장 파일을 읽는 중 문제가 발생했습니다.")
            self.quizzes = self.get_default_quizzes()

    def backup_broken_state(self):
        """
        손상된 저장 파일을 기본 데이터로 덮어쓰기 전에
        원본을 state.json.bak으로 복사해 둔다.
        """
        try:
            BACKUP_FILE.write_bytes(STATE_FILE.read_bytes())
            print(f"💾 손상된 원본 파일을 {BACKUP_FILE.name}(으)로 백업했습니다.")
        except OSError:
            print("🚧 손상된 원본 파일을 백업하지 못했습니다.")

    def save_state(self):
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_total": self.best_total,
            "played_count": self.played_count,
            "history": self.history
        }

        try:
            # 임시 파일에 먼저 끝까지 저장한 뒤, 성공하면 state.json과 교체한다.
            # 저장 도중 문제가 생겨도 기존 state.json은 망가지지 않는다.
            with open(TEMP_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            TEMP_FILE.replace(STATE_FILE)
        except OSError:
            print("🚧 데이터 저장 중 오류가 발생했습니다. 기존 저장 파일은 그대로 유지됩니다.")

    def input_text(self, message):
        while True:
            try:
                value = input(message).strip()

                if value == "":
                    print("🚧 빈 입력은 사용할 수 없습니다.")
                    continue

                return value

            except KeyboardInterrupt:
                print("\n🚧 입력이 중단되었습니다.")
                raise InputCancelled

            except EOFError:
                print("\n🚧 입력 스트림이 종료되었습니다.")
                raise InputCancelled

    def input_int(self, message, min_value, max_value):
        while True:
            raw_value = self.input_text(message)

            try:
                number = int(raw_value)
            except ValueError:
                print(f"🚧 {min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            if number < min_value or number > max_value:
                print(f"🚧 {min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            return number

    def input_yes_no(self, message):
        while True:
            answer = self.input_text(message).lower()

            if answer in ["y", "yes"]:
                return True

            if answer in ["n", "no"]:
                return False

            print("🚧 y 또는 n으로 입력해주세요.")

    def show_menu(self):
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("        ✨ Python Quest Lab ✨")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  1) 퀴즈 도전")
        print("  2) 새 문제 등록")
        print("  3) 문제 보관함 (힌트 수정 / 삭제)")
        print("  4) 기록 확인")
        print("  5) 게임 종료")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def run(self):
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
                    self.show_records()
                elif choice == 5:
                    self.exit_game()

            except InputCancelled:
                self.running = False

        self.save_state()
        print("✅ 프로그램을 안전하게 종료했습니다.")

    def play_quiz(self):
        if not self.quizzes:
            print("\n🚧 아직 등록된 문제가 없습니다.")
            return

        total_available = len(self.quizzes)

        print()
        print("╔══════════════════════════════════════╗")
        print("        🚀 퀴즈 도전을 시작합니다")
        print("╚══════════════════════════════════════╝")
        print(f"총 {total_available}개의 문제가 준비되어 있습니다.")

        question_count = self.input_int(
            f"몇 문제를 풀까요? (1-{total_available}) > ",
            1,
            total_available
        )

        selected_quizzes = random.sample(self.quizzes, question_count)

        score = 0
        correct_count = 0
        hint_count = 0
        wrong_answers = []

        for index, quiz in enumerate(selected_quizzes, start=1):
            hint_used = False

            quiz.display(index)
            print("   5) 힌트 보기")

            while True:
                user_answer = self.input_int("정답 번호 선택 또는 힌트 보기 > ", 1, 5)

                if user_answer == 5:
                    if hint_used:
                        print("🚧 이미 힌트를 사용했습니다.")
                    else:
                        print(f"💡 힌트: {quiz.hint}")
                        print("   힌트를 사용했으므로 맞히면 0.5점만 획득합니다.")
                        hint_used = True
                        hint_count += 1
                    continue

                break

            if quiz.check_answer(user_answer):
                print("🟢 맞았습니다!")
                correct_count += 1

                if hint_used:
                    score += 0.5
                else:
                    score += 1
            else:
                print(f"🔴 아쉽습니다. 정답은 {quiz.answer}번입니다.")
                wrong_answers.append((quiz, user_answer))

        percent = self.get_score_percent(score, question_count)

        print()
        print("╔══════════════════════════════════════╗")
        print("              🎯 도전 결과")
        print("╠══════════════════════════════════════╣")
        print(f"   정답 수       : {correct_count} / {question_count}")
        print(f"   획득 점수     : {score} / {question_count}")
        print(f"   환산 점수     : {percent}점")
        print(f"   힌트 사용 수  : {hint_count}회")
        
        first_play = self.played_count == 0
        self.played_count += 1

        current_best_percent = self.get_score_percent(
            self.best_score,
            self.best_total
        )

        if first_play or percent > current_best_percent:
            self.best_score = score
            self.best_total = question_count
            print("   기록 상태     : 새로운 최고 기록입니다!")
        else:
            print(f"   기록 상태     : 최고 기록은 {current_best_percent}점입니다.")

        print("╚══════════════════════════════════════╝")

        if wrong_answers:
            self.show_wrong_answers(wrong_answers)

        record = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question_count": question_count,
            "correct_count": correct_count,
            "score": score,
            "total": question_count,
            "percent": percent,
            "hint_count": hint_count
        }

        self.history.append(record)
        self.save_state()

    def show_wrong_answers(self, wrong_answers):
        """
        퀴즈가 끝난 뒤 틀린 문제와 정답을 다시 보여준다.
        wrong_answers: (Quiz 객체, 사용자가 고른 번호) 묶음의 리스트
        """
        print()
        print("📝 틀린 문제 다시 보기")
        print("────────────────────────────────────────")

        for quiz, user_answer in wrong_answers:
            print(f"Q. {quiz.question}")
            print(f"   내가 고른 답 : {user_answer}) {quiz.choices[user_answer - 1]}")
            print(f"   정답         : {quiz.answer}) {quiz.choices[quiz.answer - 1]}")
            print("────────────────────────────────────────")

    def add_quiz(self):
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
        hint = self.input_text("힌트 입력 > ")

        new_quiz = Quiz(question, choices, answer, hint)
        self.quizzes.append(new_quiz)
        self.save_state()

        print()
        print("✅ 새 문제가 문제 보관함에 저장되었습니다.")

    def show_quiz_list(self):
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
            print(f"    💡 힌트: {quiz.hint}")

        print()
        print("────────────────────────────────────────")
        print("  1) 힌트 등록 / 수정")
        print("  2) 문제 삭제")
        print("  0) 메인 메뉴로 돌아가기")
        print("────────────────────────────────────────")

        action = self.input_int("👉 번호 입력 > ", 0, 2)

        if action == 0:
            print("✅ 메인 메뉴로 돌아갑니다.")
            return

        quiz_number = self.input_int(
            f"대상 문제 번호 선택 (취소: 0, 1-{len(self.quizzes)}) > ",
            0,
            len(self.quizzes)
        )

        if quiz_number == 0:
            print("✅ 선택을 취소했습니다.")
            return

        if action == 1:
            self.edit_hint(quiz_number)
        else:
            self.delete_quiz(quiz_number)

    def edit_hint(self, quiz_number):
        target_quiz = self.quizzes[quiz_number - 1]

        print()
        print("힌트를 수정할 문제:")
        print(f"Q. {target_quiz.question}")
        print(f"현재 힌트: {target_quiz.hint}")

        new_hint = self.input_text("새 힌트 입력 > ")
        target_quiz.update_hint(new_hint)
        self.save_state()

        print()
        print("✅ 힌트가 저장되었습니다.")

    def delete_quiz(self, quiz_number):
        quiz_index = quiz_number - 1
        target_quiz = self.quizzes[quiz_index]

        print()
        print("삭제할 문제:")
        print(f"Q. {target_quiz.question}")

        confirm = self.input_yes_no("정말 삭제할까요? (y/n) > ")

        if not confirm:
            print("✅ 삭제를 취소했습니다.")
            return

        removed_quiz = self.quizzes.pop(quiz_index)
        self.save_state()

        print()
        print(f"🗑️ 삭제 완료: {removed_quiz.question}")

    def show_records(self):
        print()

        if self.played_count == 0:
            print("📊 아직 퀴즈 도전 기록이 없습니다.")
            return

        best_percent = self.get_score_percent(
            self.best_score,
            self.best_total
        )

        print("╭──────────────────────────────────────╮")
        print("        📊 나의 기록")
        print("╰──────────────────────────────────────╯")
        print(f"최고 점수   : {best_percent}점")
        print(f"최고 기록   : {self.best_score} / {self.best_total}")
        print(f"도전 횟수   : {self.played_count}회")
        print("────────────────────────────────────────")

        print()
        print("최근 기록")
        print("────────────────────────────────────────")

        recent_history = self.history[-10:]

        for index, record in enumerate(recent_history, start=1):
            print(f"{index}. 날짜       : {record.get('datetime', '알 수 없음')}")
            print(f"   문제 수    : {record.get('question_count', 0)}개")
            print(f"   정답 수    : {record.get('correct_count', 0)}개")
            print(f"   획득 점수  : {record.get('score', 0)} / {record.get('total', 0)}")
            print(f"   환산 점수  : {record.get('percent', 0)}점")
            print(f"   힌트 사용  : {record.get('hint_count', 0)}회")
            print("────────────────────────────────────────")

    def exit_game(self):
        self.save_state()
        self.running = False
        print()
        print("👋 게임을 종료합니다. 다음에 또 도전해보세요!")


if __name__ == "__main__":
    game = QuizGame()
    game.run()