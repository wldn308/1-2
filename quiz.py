class Quiz:
    """
    개별 퀴즈 1개를 표현하는 클래스
    - question: 문제
    - choices: 선택지 4개
    - answer: 정답 번호, 1~4
    """

    def __init__(self, question, choices, answer):
        if not question:
            raise ValueError("문제는 비어 있을 수 없습니다.")

        if len(choices) != 4:
            raise ValueError("선택지는 반드시 4개여야 합니다.")

        if answer < 1 or answer > 4:
            raise ValueError("정답 번호는 1~4 사이여야 합니다.")

        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, number=None):
        """
        퀴즈를 화면에 출력하는 메서드
        """
        if number is not None:
            print(f"\n[{number}] {self.question}")
        else:
            print(f"\n{self.question}")

        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def check_answer(self, user_answer):
        """
        사용자의 답이 정답인지 확인하는 메서드
        """
        return self.answer == user_answer

    def to_dict(self):
        """
        Quiz 객체를 JSON 저장 가능한 dict 형태로 변환
        """
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }

    @classmethod
    def from_dict(cls, data):
        """
        dict 데이터를 Quiz 객체로 변환
        """
        question = str(data["question"])
        choices = list(data["choices"])
        answer = int(data["answer"])

        return cls(question, choices, answer)