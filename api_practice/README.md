# API Practice

학생들이 직접 손으로 채워 보면서 배우는 실습 묶음입니다.

이 폴더에서 다루는 내용:
- OpenAI API로 기본 텍스트 생성
- reasoning effort 실험
- temperature 실험
- OpenAI web search tool 사용
- 나만의 custom tool 연결
- OpenRouter에서 Qwen thinking 켜기
- 터미널 연속 대화 챗봇 만들기
- ChatGPT 느낌의 웹 챗봇 만들기

## 시작하기

1. `api_practice` 폴더로 이동합니다.
2. 가상환경을 만들고 활성화합니다.
3. 패키지를 설치합니다.
4. `.env.example` 을 복사해 `.env` 파일을 만듭니다.
5. `python 00_setup_check.py` 로 환경을 점검합니다.

예시 명령어:

```bash
cd api_practice
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python 00_setup_check.py
```

## 추천 실습 순서

1. `00_setup_check.py`
2. `01_openai_basic_response.py`
3. `02_openai_reasoning_effort_lab.py`
4. `03_openai_temperature_lab.py`
5. `04_openai_web_search_tool.py`
6. `05_openai_custom_tool.py`
7. `06_openrouter_qwen_enable_thinking.py`
8. `07_terminal_chatbot_basic.py`
9. `08_terminal_chatbot_with_commands.py`
10. `09_terminal_chatbot_streaming.py`
11. `web_chatbot/app.py`

## 수업 운영 팁

- 처음 30분은 `01`, `02`, `03` 으로 모델 파라미터 감각 익히기
- 다음 40분은 `04`, `05`, `06` 으로 도구와 다른 API 제공자 경험하기
- 다음 50분은 `07`, `08`, `09` 로 터미널 챗봇 완성하기
- 마지막 60분은 `web_chatbot` 을 구현하고 꾸미기

## 웹 챗봇 실행

`api_practice` 폴더에서 아래처럼 실행하세요.

```bash
python web_chatbot/app.py
```

브라우저에서 `http://127.0.0.1:5000` 으로 접속하면 됩니다.

## 파일의 TODO 설계 방식

- 일부 파일은 상수만 채우면 돌아갑니다.
- 일부 파일은 함수 1개 또는 2개를 직접 구현해야 합니다.
- 구현 전에도 실행은 되며, 어디가 비어 있는지 안내 문구가 나옵니다.

## 참고 메모

- OpenAI 예제는 최신 Python SDK 스타일에 맞춰 `OpenAI()` 클라이언트를 사용하도록 구성했습니다.
- web search 예제는 Responses API 스타일을 사용합니다.
- 터미널 챗봇은 학생들이 대화 기록 구조를 이해하기 쉽게 chat completions 스타일을 사용합니다.
- OpenRouter 예제는 HTTP 요청 구조를 직접 보게 하려고 `requests` 기반으로 만들었습니다.

## 추가 문제

더 많은 문제는 `MISSIONS.md` 에 정리되어 있습니다.
