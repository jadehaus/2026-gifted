# Tool-Using LLM 실습

중학생이 직접 Python 함수를 만들고, 그 함수가 OpenAI API 의 tool 로 들어가는 과정을 눈으로 보는 실습입니다.

## 실행

```bash
cd tool_practice
pip install -r requirements.txt
python run_app.py
```

브라우저가 자동으로 열립니다.

## 학생이 주로 수정하는 파일

- `my_tools.py`: 내가 직접 새 tool 함수를 적는 빈 파일
- `tools_calculator.py`: 계산기 tool 실습 파일
- `tools_wikipedia.py`: 위키피디아 검색 tool 실습 파일
- `tools_store.py`: CSV 데이터 tool 실습 파일
- `tools_time.py`: 시간/날짜 tool placeholder 실습 파일
- `tools_random.py`: 랜덤/시뮬레이션 tool placeholder 실습 파일
- `tools_notes.py`: 파일 메모장 tool placeholder 실습 파일
- `tools_number_game.py`: 숫자 맞히기 게임 tool placeholder 실습 파일
- `class_store.csv`: 엑셀처럼 열어볼 수 있는 작은 데이터 파일
- `templates/page_text.html`: 브라우저에 보이는 제목과 문장을 바꾸는 곳

앱을 처음 실행하면 선택된 tool 이 없습니다. 브라우저 오른쪽의 `Tool 파일 선택`에서 원하는 파일을 고르면, 그 파일의 `TOOLS` 리스트만 LLM 에게 전달됩니다. 파일을 바꾸거나 `제거` 버튼을 누르면 대화 기록은 초기화됩니다.

## 5분 도입: 계산기 tool

큰 곱셈은 LLM 이 직접 계산하면 틀릴 수 있습니다. 그래서 `tools_calculator.py` 에 계산기 tool 을 넣어 두었습니다.

추천 질문:

```text
123456789 곱하기 987654321을 정확히 계산해줘.
```

수업 흐름:

1. 브라우저에서 `tool 없음` 상태로 질문합니다.
2. LLM 이 직접 계산하면 틀릴 수 있다는 점을 보여줍니다.
3. `tools_calculator.py` 를 선택하고 다시 질문합니다.
4. Python tool 이 계산한 정확한 답을 LLM 이 사용한다는 점을 확인합니다.

학생 확장 미션:

- `add` 함수 완성하기
- `subtract` 함수 완성하기
- `divide` 함수 완성하기
- 완성한 뒤 브라우저에서 `tools_calculator.py` 다시 적용하기

## 추가 placeholder 실습

아래 파일들은 일부러 정답 코드를 비워 둔 실습용 예제입니다.

- `tools_time.py`: `get_current_time`, `days_between`, `add_days`
- `tools_random.py`: `roll_dice`, `flip_coin`, `random_pick`
- `tools_notes.py`: `save_note`, `load_note`, `list_notes`
- `tools_number_game.py`: `start_game`, `guess`, `reset_game`

추천 흐름:

1. 브라우저에서 파일을 먼저 선택해 schema 를 봅니다.
2. 질문을 던져 tool 호출이 어떻게 생기는지 봅니다.
3. Python 파일의 TODO 를 하나씩 구현합니다.
4. 브라우저에서 같은 파일을 다시 `적용`합니다.
5. `제거` 버튼으로 tool 없는 상태와 비교합니다.

## 랜덤성 비교 실험

`randomness_experiment.py` 는 LLM 이 0부터 N 까지 숫자를 고르는 분포와 Python `random` 모듈의 분포를 비교합니다.

```bash
python randomness_experiment.py
```

실행 후 `randomness_result.csv` 파일이 만들어집니다. 엑셀이나 구글 시트에서 열어 막대그래프로 비교할 수 있습니다. 반복 횟수를 늘리면 API 호출도 그만큼 늘어나므로, 수업에서는 `TRIALS` 값을 작게 시작하는 것을 추천합니다.

## 진짜 같은 경험: 위키피디아 검색 tool

`tools_wikipedia.py` 의 `search_wikipedia(query)` 는 한국어 위키피디아를 검색한 뒤, 가장 관련 있는 문서의 요약을 가져옵니다. 무료이고 별도 API 키가 필요 없어서 검색 tool 실습에 좋습니다.

추천 질문:

```text
민족사관고등학교가 언제 개교했는지 위키피디아에서 찾아줘.
```

```text
이순신 장군이 태어난 해를 위키피디아에서 찾아서 알려줘.
```

핵심 아이디어:

1. LLM 이 혼자 알고 있는 답을 말하는 것이 아닙니다.
2. LLM 이 `search_wikipedia` tool 을 호출합니다.
3. Python 코드가 위키피디아 API에 접속해 정보를 가져옵니다.
4. LLM 이 tool 결과를 읽고 사용자에게 자연스럽게 답합니다.

## 선생님이 설명할 때 보기 좋은 파일

- `util.py`: Python 함수를 JSON tool schema 로 바꾸는 helper 모음
- `inference.py`: `client.responses.create(...)` 로 tool-using LLM 을 실행하는 핵심 코드
- `run_app.py`: 브라우저 UI 를 실행하는 entrypoint

## 새 tool 추가 예시

`my_tools.py` 또는 새 `tools_이름.py` 파일에 함수를 추가하고, 마지막 `TOOLS` 리스트에 넣으면 됩니다. 새 파일 이름은 `tools_` 로 시작해야 브라우저 선택 목록에 나타납니다.

```python
def repeat_text(text: str, count: int) -> str:
    """text 를 count 번 반복하는 tool 입니다."""
    return text * count


TOOLS = [
    repeat_text,
]
```
