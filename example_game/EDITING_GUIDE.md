# 학생용 게임 수정 안내서

이 문서는 `example_game` 폴더의 텍스트 RPG를 나만의 게임으로 바꾸고 싶을 때 참고하는 안내서입니다.

이 게임은 플레이어가 채팅창에 행동을 입력하면, LLM이 그 문장을 읽고 알맞은 Python 함수를 호출해서 게임 상태를 바꾸는 구조입니다. 그래서 게임을 수정할 때는 보통 다음 순서로 보면 됩니다.

1. 세계관, 방, 아이템, 캐릭터, 퍼즐, 적을 바꾸고 싶다: `game_data.py`
2. 이동, 줍기, 대화, 전투 같은 규칙을 바꾸고 싶다: `game_tools.py`
3. 저장 데이터의 모양을 바꾸고 싶다: `state.py`
4. LLM이 게임을 진행하는 말투와 규칙을 바꾸고 싶다: `llm_engine.py`
5. 화면에 보이는 UI를 바꾸고 싶다: `templates/index.html`, `static/app.js`, `static/style.css`
6. 웹 서버 주소와 API를 바꾸고 싶다: `app.py`, `run_game.py`

처음에는 `game_data.py`만 수정하는 것을 추천합니다. 대부분의 게임 내용은 그 파일 안에 있습니다.

## 전체 파일 구조

`example_game` 폴더 안의 주요 파일은 다음 역할을 합니다.

| 파일 | 역할 | 학생들이 자주 수정할 가능성 |
| --- | --- | --- |
| `game_data.py` | 게임의 내용 데이터가 들어 있습니다. 제목, 시작 상태, 지도, 캐릭터, 아이템 설명, 퍼즐, 적을 정의합니다. | 매우 높음 |
| `game_tools.py` | LLM이 호출할 수 있는 실제 행동 함수가 들어 있습니다. 이동, 아이템 줍기, 대화, 퍼즐 풀이, 전투 처리 등이 있습니다. | 중간 |
| `state.py` | 저장 파일을 만들고 읽습니다. 현재 위치, 체력, 인벤토리, 전투 상태 등을 저장합니다. | 중간 |
| `llm_engine.py` | OpenAI API에 보내는 게임 마스터 규칙과 tool 호출 흐름이 들어 있습니다. | 중간 |
| `schema.py` | Python 함수를 OpenAI tool schema로 바꾸는 도우미입니다. 보통 수정하지 않습니다. | 낮음 |
| `app.py` | Flask 웹 서버입니다. `/api/chat`, `/api/state` 같은 API를 제공합니다. | 낮음 |
| `templates/index.html` | 화면의 큰 뼈대입니다. 왼쪽 상태창, 가운데 채팅창, 오른쪽 기록창의 HTML이 있습니다. | 중간 |
| `static/app.js` | 브라우저에서 상태를 받아 화면에 그립니다. 말풍선, 캐릭터 대사, 도구 호출 로그, 전투 버튼을 처리합니다. | 중간 |
| `static/style.css` | 화면의 색, 크기, 배치, 애니메이션 같은 디자인을 담당합니다. | 중간 |
| `saves/progress.json` | 현재 플레이 진행 상황 저장 파일입니다. 게임 데이터를 크게 바꾼 뒤에는 새 게임을 누르거나 이 파일을 초기화해야 할 수 있습니다. | 필요할 때만 |

## 실행 흐름 이해하기

플레이어가 채팅에 `북쪽으로 간다`라고 입력하면 대략 이런 일이 일어납니다.

1. 브라우저의 `static/app.js`가 입력 내용을 `/api/chat`으로 보냅니다.
2. `app.py`의 `chat()` 함수가 요청을 받습니다.
3. `llm_engine.py`의 `ask_game_master()`가 LLM에게 플레이어 입력을 전달합니다.
4. LLM은 `move`, `take_item`, `talk_to`, `battle_action` 같은 tool 중 하나를 고릅니다.
5. 선택된 함수는 `game_tools.py`에 있습니다.
6. 함수는 `state.py`를 통해 현재 저장 상태를 읽고 바꾼 뒤 다시 저장합니다.
7. 결과가 브라우저로 돌아가고, `static/app.js`가 화면을 업데이트합니다.

즉, 게임의 내용은 `game_data.py`, 게임의 규칙은 `game_tools.py`, 현재 진행 상황은 `state.py`, 화면 표시는 `static/app.js`와 `static/style.css`가 담당한다고 생각하면 됩니다.

## 가장 먼저 볼 파일: `game_data.py`

`game_data.py`는 게임의 설정집입니다. Python 코드처럼 보이지만, 대부분은 딕셔너리 데이터입니다.

### `GAME_TITLE`

```python
GAME_TITLE = "달빛 기록관: 망각의 층"
```

게임 제목입니다.

바꾸면 브라우저 제목과 게임 화면 제목에 반영됩니다.

예시:

```python
GAME_TITLE = "별빛 학교: 사라진 동아리실"
```

### `START_STATE`

`START_STATE`는 새 게임을 시작할 때의 초기 상태입니다.

```python
START_STATE = {
    "player": {"name": "방문자", "hp": 34, "max_hp": 34, "level": 1, "xp": 0},
    "location": "lobby",
    "inventory": ["낡은 열쇠", "회복 사탕"],
    "flags": {"met_sia": False, "clock_fixed": False, "rune_answered": False, "boss_open": False},
    "affection": {"sia": 0, "harin": 0, "mook": 0},
    "battle": None,
    "journal": ["비 오는 밤, 사라진 동생의 이름이 적힌 초대장을 따라 기록관에 들어왔다."],
    "character_history": {"sia": [], "harin": [], "mook": []},
    "turn": 0,
}
```

각 항목의 뜻은 다음과 같습니다.

| 이름 | 뜻 |
| --- | --- |
| `player` | 플레이어의 이름, 체력, 최대 체력, 레벨, 경험치입니다. |
| `location` | 시작 위치입니다. 이 값은 `MAP`에 있는 방 ID여야 합니다. |
| `inventory` | 처음부터 가지고 있는 아이템 목록입니다. |
| `flags` | 퍼즐 해결 여부, 문 개방 여부 같은 진행 체크용 값입니다. |
| `affection` | 캐릭터별 호감도입니다. 캐릭터 ID를 키로 씁니다. |
| `battle` | 현재 전투 중인지 저장합니다. 새 게임에서는 보통 `None`입니다. |
| `journal` | 오른쪽 진행 기록에 보이는 문장입니다. |
| `character_history` | 캐릭터별 대화 기록입니다. |
| `turn` | 플레이어가 행동한 횟수입니다. |

주의할 점:

- `location`은 반드시 `MAP`에 있는 방 ID여야 합니다.
- 새 캐릭터를 추가하면 `affection`과 `character_history`에도 캐릭터 ID를 추가하는 것이 좋습니다.
- 새 퍼즐이나 문 잠금 조건을 추가하면 `flags`에 진행 상태를 저장할 이름을 추가하는 것이 좋습니다.

### `MAP`

`MAP`은 게임의 지도입니다. 방 하나가 딕셔너리 하나입니다.

```python
"lobby": {
    "name": "은빛 로비",
    "level": 1,
    "description": "천장에는 멈춘 별자리 시계가 걸려 있고, 바닥의 물자국은 북쪽 서가로 이어진다.",
    "exits": {"북": "west_stacks", "동": "clock_hall"},
    "items": ["성냥갑"],
    "characters": ["sia"],
    "puzzle": None,
},
```

방 ID는 `"lobby"` 같은 영어 이름입니다. 코드가 이 이름으로 방을 찾습니다. 화면에 보이는 이름은 `"name"`입니다.

각 항목의 뜻은 다음과 같습니다.

| 이름 | 형태 | 뜻 |
| --- | --- | --- |
| `name` | 문자열 | 화면에 보이는 방 이름입니다. |
| `level` | 숫자 | 방의 난이도나 진행 단계입니다. 현재 코드에서는 표시용 성격이 강합니다. |
| `description` | 문자열 | 방 설명입니다. 주변을 살피거나 화면 상태에 사용됩니다. |
| `exits` | 딕셔너리 | 어느 방향으로 어느 방에 갈 수 있는지 나타냅니다. |
| `items` | 문자열 리스트 | 처음 그 방에 놓여 있는 아이템입니다. |
| `characters` | 문자열 리스트 | 그 방에 있는 캐릭터 ID입니다. |
| `puzzle` | 문자열 또는 `None` | 그 방에 있는 퍼즐 ID입니다. 없으면 `None`입니다. |
| `battle` | 문자열 | 그 방에 들어갔을 때 등장할 적 ID입니다. 필요한 방에만 넣습니다. |

`exits` 예시:

```python
"exits": {"북": "west_stacks", "동": "clock_hall"}
```

뜻은 `북쪽으로 가면 west_stacks 방으로 이동`, `동쪽으로 가면 clock_hall 방으로 이동`입니다.

새 방을 추가하는 예시:

```python
"secret_classroom": {
    "name": "비밀 교실",
    "level": 2,
    "description": "칠판에는 누군가 지우다 만 공식이 희미하게 남아 있다.",
    "exits": {"남": "lobby"},
    "items": ["분필 조각"],
    "characters": [],
    "puzzle": None,
},
```

방을 추가한 뒤에는 기존 방의 `exits`에도 연결을 만들어야 실제로 갈 수 있습니다.

예를 들어 로비에서 북쪽으로 비밀 교실에 가게 하려면:

```python
"lobby": {
    ...
    "exits": {"북": "secret_classroom", "동": "clock_hall"},
    ...
}
```

주의할 점:

- 방 ID는 중복되면 안 됩니다.
- `exits`의 목적지 ID는 반드시 `MAP` 안에 실제로 있어야 합니다.
- 현재 `move()` 함수의 방향 타입은 `Direction = Literal["북", "남", "동", "서"]`입니다. 다른 방향, 예를 들어 `"위"`나 `"아래"`를 쓰려면 `game_tools.py`의 `Direction`도 수정해야 합니다.

### `CHARACTERS`

`CHARACTERS`는 캐릭터 설정입니다.

```python
"sia": {
    "name": "시아",
    "role": "기억을 잃은 견습 사서",
    "emoji": "🕯️",
    "accent": "#d8f3ff",
    "personality": "조심스럽지만 진실 앞에서는 무모할 정도로 용감하다.",
    "context": "동생의 이름을 알고 있을지 모른다. 신뢰가 높아지면 봉인문의 힌트를 준다.",
    "dialogue": {
        "default": "제 이름은 시아예요. 이 기록관은 사람의 기억을 책으로 묶어 두죠.",
        "hint": "거울문은 잃어버린 것을 묻지 않아요. 끝까지 남는 것을 묻죠. 답은 '기억'에 가까워요.",
        "bond": "당신을 보면… 잊은 줄 알았던 이름이 혀끝에서 맴돌아요. 함께라면 끝까지 갈 수 있을 것 같아요.",
    },
},
```

각 항목의 뜻은 다음과 같습니다.

| 이름 | 뜻 |
| --- | --- |
| 캐릭터 ID | `"sia"` 같은 내부 이름입니다. 방의 `characters`, 호감도, 대화 기록에서 사용합니다. |
| `name` | 화면에 보이는 이름입니다. |
| `role` | 캐릭터의 역할입니다. 화면과 대화 생성에 사용됩니다. |
| `emoji` | 캐릭터 말풍선에 보이는 표시입니다. |
| `accent` | 캐릭터 카드 색상입니다. CSS 색상값을 씁니다. |
| `personality` | 캐릭터의 성격입니다. LLM 캐릭터 대사 생성에 사용됩니다. |
| `context` | 캐릭터가 게임에서 어떤 역할을 하는지 설명하는 메모입니다. |
| `dialogue.default` | API 키가 없거나 대화 생성에 실패했을 때 나오는 기본 대사입니다. |
| `dialogue.hint` | 특정 조건에서 줄 수 있는 힌트입니다. |
| `dialogue.bond` | 호감도가 높을 때 사용할 수 있는 대사입니다. |

새 캐릭터를 추가하는 예시:

```python
"yuna": {
    "name": "유나",
    "role": "시간표를 잃어버린 학생회장",
    "emoji": "📘",
    "accent": "#c7e8ff",
    "personality": "침착하지만 친구가 위험하면 바로 뛰어든다.",
    "context": "학교 구조를 잘 알고 있어 잠긴 교실의 단서를 줄 수 있다.",
    "dialogue": {
        "default": "여기는 평범한 학교가 아니야. 복도가 종소리에 맞춰 바뀌고 있어.",
        "hint": "잠긴 문은 열쇠보다 시간표를 먼저 확인해야 해.",
        "bond": "네가 함께라면 이 이상한 학교도 빠져나갈 수 있을 것 같아.",
    },
},
```

새 캐릭터를 추가한 뒤 같이 확인할 곳:

- `START_STATE["affection"]`에 `"yuna": 0` 추가
- `START_STATE["character_history"]`에 `"yuna": []` 추가
- 어떤 방의 `characters`에 `"yuna"` 추가
- `state.py`의 `load_state()`에서 기존 캐릭터 목록을 보정하는 부분 확인
- `static/app.js`의 `CHAR_NAMES`에 `yuna: "유나"` 추가
- `game_tools.py`의 `CharacterId = Literal[...]`에 `"yuna"` 추가

마지막 항목이 중요합니다. `CharacterId`를 수정하지 않으면 OpenAI tool schema에 새 캐릭터 ID가 선택지로 들어가지 않을 수 있습니다.

### `LORE`

`LORE`는 플레이어가 무언가를 자세히 조사할 때 나오는 설명입니다.

```python
"성냥갑": "축축한데도 불이 잘 붙는다. 종이로 된 적에게 특히 효과가 있을 것 같다.",
```

플레이어가 `성냥갑을 조사한다`, `성냥갑을 살펴본다`처럼 입력하면 `examine()` tool이 이 설명을 찾을 수 있습니다.

아이템뿐 아니라 장소, 인물, 사물, 단서도 넣을 수 있습니다.

예시:

```python
"낡은 칠판": "분필 자국을 따라 읽으면 '첫 번째 종이 울릴 때 문이 열린다'고 적혀 있다.",
"분필 조각": "손에 쥐면 차갑다. 이상하게도 칠판에 글씨가 저절로 써진다.",
```

주의할 점:

- `LORE`에 넣었다고 자동으로 아이템이 생기지는 않습니다.
- 실제로 주울 수 있는 아이템은 `MAP`의 방 `items`에 있어야 합니다.
- 처음부터 가지고 있는 아이템은 `START_STATE["inventory"]`에 있어야 합니다.

### `PUZZLES`

`PUZZLES`는 퍼즐과 잠금 해제를 정의합니다.

```python
"clockwork": {
    "name": "별자리 시계",
    "description": "비어 있는 장치에 청동 톱니를 끼우고 시간을 '새벽 3시'로 맞춰야 한다.",
    "required_item": "청동 톱니",
    "answer_keywords": ["새벽 3시", "3시", "세시"],
    "reward_items": ["별자리 바늘"],
    "flag": "clock_fixed",
    "journal": "별자리 시계를 고치자 거울 기록실의 봉인문이 약해졌다.",
},
```

각 항목의 뜻은 다음과 같습니다.

| 이름 | 뜻 |
| --- | --- |
| 퍼즐 ID | `"clockwork"` 같은 내부 이름입니다. 방의 `puzzle`에서 사용합니다. |
| `name` | 화면과 결과에 보이는 퍼즐 이름입니다. |
| `description` | 플레이어가 보는 퍼즐 설명입니다. |
| `required_item` | 이 아이템이 있어야 풀 수 있습니다. 필요 없으면 생략할 수 있습니다. |
| `required_flag` | 다른 퍼즐이나 사건이 먼저 해결되어야 할 때 씁니다. |
| `answer_keywords` | 플레이어 답변에 이 단어 중 하나가 들어 있으면 정답 처리됩니다. |
| `reward_items` | 해결 후 인벤토리에 들어오는 아이템입니다. |
| `flag` | 해결되었음을 저장할 진행 플래그 이름입니다. |
| `opens_flag` | 해결 후 추가로 켤 플래그입니다. 보스방 개방 등에 씁니다. |
| `journal` | 해결 후 진행 기록에 남길 문장입니다. |

새 퍼즐을 추가하는 예시:

```python
"blackboard_code": {
    "name": "칠판 암호",
    "description": "칠판에는 '가장 먼저 울리는 소리'를 적으라고 쓰여 있다.",
    "required_item": "분필 조각",
    "answer_keywords": ["종", "종소리", "첫 종"],
    "reward_items": ["학생회 열쇠"],
    "flag": "blackboard_solved",
    "journal": "칠판 암호를 풀자 책상 서랍에서 학생회 열쇠가 나왔다.",
},
```

퍼즐을 추가한 뒤 같이 확인할 곳:

- 어느 방에 퍼즐이 있는지 `MAP`의 `"puzzle": "blackboard_code"`로 연결
- `START_STATE["flags"]`에 `"blackboard_solved": False` 추가
- `game_tools.py`의 `solve_puzzle()` 타입에 새 퍼즐 ID 추가

현재 `solve_puzzle()` 함수는 이렇게 되어 있습니다.

```python
def solve_puzzle(puzzle_id: Literal["clockwork", "rune_door"], answer: str) -> dict:
```

새 퍼즐을 추가하면 다음처럼 바꿔야 합니다.

```python
def solve_puzzle(puzzle_id: Literal["clockwork", "rune_door", "blackboard_code"], answer: str) -> dict:
```

### `ENEMIES`

`ENEMIES`는 전투에 등장하는 적입니다.

```python
"paper_moth": {
    "name": "종이 나방",
    "hp": 12,
    "attack": 3,
    "xp": 4,
    "weakness": "성냥갑",
    "loot": ["찢어진 색인표"],
},
```

각 항목의 뜻은 다음과 같습니다.

| 이름 | 뜻 |
| --- | --- |
| 적 ID | `"paper_moth"` 같은 내부 이름입니다. |
| `name` | 화면에 보이는 적 이름입니다. |
| `hp` | 적 체력입니다. |
| `attack` | 적이 반격할 때 주는 피해입니다. |
| `xp` | 물리쳤을 때 얻는 경험치입니다. |
| `weakness` | 약점 아이템입니다. 인벤토리에 있으면 공격이 강해지거나 도구 사용으로 큰 피해를 줍니다. |
| `loot` | 물리쳤을 때 얻는 아이템입니다. |

새 적 예시:

```python
"shadow_monitor": {
    "name": "그림자 감독관",
    "hp": 18,
    "attack": 4,
    "xp": 8,
    "weakness": "학생회 열쇠",
    "loot": ["검은 출석부"],
},
```

적을 등장시키는 방법:

```python
"old_hallway": {
    "name": "낡은 복도",
    ...
    "battle": "shadow_monitor",
},
```

주의할 점:

- 방에 `"battle": "shadow_monitor"`를 넣어야 그 적이 등장할 수 있습니다.
- 현재 `move()`에는 서쪽 서가에 들어가면 `paper_moth`가 등장하는 특별 규칙이 따로 있습니다. 완전히 다른 게임으로 바꿀 때는 `game_tools.py`의 `move()`도 확인해야 합니다.

## 게임 규칙 파일: `game_tools.py`

`game_tools.py`에는 LLM이 실제로 호출할 수 있는 함수들이 있습니다. 이 함수들을 tool이라고 생각하면 됩니다.

맨 아래를 보면 다음 목록이 있습니다.

```python
TOOLS = [
    inspect_area,
    reset_game,
    move,
    take_item,
    use_item,
    present_enemy_choice,
    talk_to,
    solve_puzzle,
    battle_action,
    examine,
]
```

이 목록에 들어 있는 함수만 LLM에게 tool로 전달됩니다.

### 주요 tool 설명

| 함수 | 역할 |
| --- | --- |
| `inspect_area()` | 현재 위치, 출구, 인물, 퍼즐, 아이템을 확인합니다. |
| `reset_game()` | 저장 데이터를 초기화하고 새 게임을 시작합니다. |
| `move(direction)` | 북/남/동/서 방향으로 이동합니다. |
| `take_item(item_name)` | 현재 방에 있는 아이템을 인벤토리에 넣습니다. |
| `use_item(item_name, target="")` | 회복 아이템 사용, 전투 중 도구 사용 등을 처리합니다. |
| `present_enemy_choice()` | 전투가 시작됐을 때 브라우저에 싸운다/도망친다 버튼을 띄우게 합니다. |
| `talk_to(character_id, player_line="", topic="")` | 현재 방의 캐릭터와 대화합니다. |
| `solve_puzzle(puzzle_id, answer)` | 퍼즐 정답이나 해결 행동을 검사합니다. |
| `battle_action(action, item_name="")` | 공격, 방어, 도구, 도망을 처리합니다. |
| `examine(target)` | 사물, 아이템, 방, 인물을 자세히 조사합니다. |

### 함수 docstring의 중요성

각 함수 아래에는 이런 설명이 있습니다.

```python
def move(direction: Direction) -> dict:
    """지도에서 북/남/동/서 방향으로 이동한다. 잠긴 진행 조건과 전투 상태를 검사한다."""
```

따옴표 세 개 안의 문장을 docstring이라고 합니다.

이 설명은 사람만 읽는 주석이 아니라, OpenAI tool schema의 `description`으로도 들어갑니다. 즉, LLM이 이 함수를 언제 써야 하는지 판단하는 힌트입니다.

새 tool을 만들거나 기존 tool의 목적을 바꾸면 docstring도 친절하게 수정하는 것이 좋습니다.

### 타입 힌트의 중요성

이 게임은 함수의 타입 힌트를 보고 자동으로 tool schema를 만듭니다.

예시:

```python
Direction = Literal["북", "남", "동", "서"]
CharacterId = Literal["sia", "harin", "mook"]
BattleAction = Literal["공격", "방어", "도구", "도망"]
```

`Literal[...]`은 선택 가능한 값 목록입니다.

새 캐릭터를 추가하면:

```python
CharacterId = Literal["sia", "harin", "mook", "yuna"]
```

새 전투 행동을 추가하면:

```python
BattleAction = Literal["공격", "방어", "도구", "도망", "설득"]
```

처럼 바꿔야 합니다.

타입 힌트를 바꾸지 않으면 LLM이 새 값을 잘 선택하지 못하거나, tool schema에 새 선택지가 나오지 않을 수 있습니다.

### 이동 규칙 바꾸기

`move()` 함수는 다음 일을 합니다.

- 현재 전투 중이면 이동을 막습니다.
- 현재 방의 `exits`에 해당 방향이 있는지 확인합니다.
- 잠긴 장소 조건을 확인합니다.
- 위치를 바꿉니다.
- 특정 방에 들어가면 적을 등장시킵니다.
- 상태를 저장합니다.

관측소가 잠겨 있는 규칙은 다음 부분입니다.

```python
if target == "observatory" and not state["flags"].get("boss_open"):
    return {"ok": False, "message": "거울 봉인문이 아직 관측소 길을 막고 있다."}
```

다른 잠긴 방을 만들고 싶다면 비슷하게 추가할 수 있습니다.

예시:

```python
if target == "student_council_room" and "학생회 열쇠" not in state["inventory"]:
    return {"ok": False, "message": "학생회실 문은 잠겨 있다. 열쇠가 필요하다."}
```

### 아이템 규칙 바꾸기

`take_item()`은 방에 있는 아이템을 줍는 함수입니다. 보통 수정할 필요가 없습니다.

`use_item()`은 아이템을 사용할 때의 규칙입니다.

현재는 다음 아이템이 회복 아이템입니다.

```python
if item_name in {"회복 사탕", "달빛 물약"}:
```

새 회복 아이템을 추가하고 싶으면 여기에 이름과 회복량을 추가해야 합니다.

간단한 예시:

```python
if item_name in {"회복 사탕", "달빛 물약", "따뜻한 차"}:
    amount = 10 if item_name == "회복 사탕" else 16
```

아이템마다 회복량이 많아지면 딕셔너리로 바꾸는 편이 좋습니다.

```python
healing_items = {"회복 사탕": 10, "달빛 물약": 16, "따뜻한 차": 6}
if item_name in healing_items:
    amount = healing_items[item_name]
```

### 대화 규칙 바꾸기

캐릭터 대화는 `talk_to()`와 `_character_reply()`가 담당합니다.

중요한 흐름:

1. 플레이어가 캐릭터에게 말을 겁니다.
2. 현재 방에 그 캐릭터가 있는지 확인합니다.
3. 캐릭터 설정과 최근 대화 기록을 사용해 대사를 생성합니다.
4. 말투가 친절하거나 무례한지 보고 호감도를 조금 바꿉니다.
5. 특정 조건이면 보상을 줍니다.
6. 대화 기록을 저장합니다.

호감도 변화는 `_affection_delta()`에서 정합니다.

```python
positive = ("고마", "부탁", "괜찮", "미안", "걱정", "도와", "믿", "함께")
negative = ("꺼져", "닥쳐", "쓸모", "멍청", "거짓말", "협박")
```

플레이어 말에 긍정 단어가 있으면 `+1`, 부정 단어가 있으면 `-1`입니다.

특정 캐릭터가 특정 조건에서 아이템을 주는 규칙도 있습니다.

```python
if (
    character_id == "harin"
    and state["affection"].get(character_id, 0) >= 2
    and "달빛 물약" not in state["inventory"]
    and any(word in _topic_text(player_line, topic) for word in ("도와", "물약", "회복", "아파", "다쳤"))
):
    reward = "달빛 물약"
    state["inventory"].append(reward)
```

이런 부분을 바꾸면 캐릭터별 보상 이벤트를 만들 수 있습니다.

### 퍼즐 규칙 바꾸기

`solve_puzzle()`은 `PUZZLES` 데이터를 읽어서 다음을 자동 처리합니다.

- 현재 방의 퍼즐이 맞는지 확인
- 필요한 아이템이 있는지 확인
- 필요한 플래그가 켜져 있는지 확인
- 답변에 정답 키워드가 들어 있는지 확인
- 보상 아이템 지급
- 해결 플래그 저장
- 진행 기록 추가

그래서 단순한 퍼즐은 `game_data.py`의 `PUZZLES`만 바꿔도 됩니다.

복잡한 퍼즐, 예를 들어 숫자 순서, 여러 단계, 랜덤 암호 같은 것을 만들고 싶다면 `solve_puzzle()` 내부 로직을 수정해야 합니다.

### 전투 규칙 바꾸기

`battle_action()`은 전투 한 턴을 처리합니다.

현재 전투 행동은 네 가지입니다.

| 행동 | 효과 |
| --- | --- |
| `공격` | 기본 피해를 줍니다. 약점 아이템이 인벤토리에 있으면 추가 피해를 줍니다. |
| `방어` | 다음 적 공격 피해를 줄입니다. |
| `도구` | 약점 아이템이면 큰 피해, 회복 아이템이면 회복, 아니면 별 효과 없음입니다. |
| `도망` | 전투를 끝내고 로비로 돌아갑니다. |

기본 공격 피해:

```python
damage = 5 + player["level"] * 2
```

레벨업 규칙은 `_level_up_if_needed()`에 있습니다.

```python
while player["xp"] >= player["level"] * 10:
```

즉, 다음 레벨에 필요한 경험치는 `현재 레벨 * 10`입니다.

전투를 어렵게 하고 싶으면:

- `ENEMIES`의 `hp`와 `attack`을 올립니다.
- `battle_action()`의 기본 피해를 낮춥니다.
- 회복 아이템 회복량을 줄입니다.

전투를 쉽게 하고 싶으면:

- 적 `hp`와 `attack`을 낮춥니다.
- 플레이어 시작 `hp`를 올립니다.
- 약점 아이템 피해량을 올립니다.

## 상태 저장 파일: `state.py`

`state.py`는 현재 게임 상태를 `saves/progress.json`에 저장합니다.

### 중요한 함수

| 함수 | 역할 |
| --- | --- |
| `new_state()` | `START_STATE`를 복사해서 새 상태를 만듭니다. 각 방의 아이템 목록도 초기화합니다. |
| `load_state()` | 저장 파일을 읽습니다. 없으면 새로 만듭니다. |
| `save_state(state)` | 상태를 JSON 파일로 저장합니다. |
| `reset_state()` | 새 게임 상태를 만들고 저장합니다. |
| `public_state(state)` | 화면에 보여 줄 안전한 상태 정보만 골라서 반환합니다. |
| `public_battle(state)` | 전투 정보를 화면용으로 정리합니다. |
| `public_character_history(state)` | 캐릭터별 대화 기록을 화면용으로 정리합니다. |

### 저장 파일 때문에 헷갈릴 수 있는 점

게임 데이터를 바꿨는데 화면이 예전 상태처럼 보이면 저장 파일 때문일 수 있습니다.

예를 들어 `game_data.py`에서 로비의 아이템을 바꿨는데 이미 저장 파일에 예전 로비 아이템이 저장되어 있으면, 화면에는 저장 파일 기준으로 나올 수 있습니다.

이럴 때는 다음 중 하나를 하면 됩니다.

1. 화면에서 `새 게임` 버튼을 누릅니다.
2. `example_game/saves/progress.json` 파일을 지웁니다.
3. 코드에서 `reset_game()`을 실행합니다.

수업 중에는 보통 `새 게임` 버튼을 누르는 방식이 가장 안전합니다.

### 새 캐릭터를 추가할 때 `state.py`도 확인하기

현재 `load_state()`에는 기존 캐릭터 대화 기록을 보정하는 코드가 있습니다.

```python
for character_id in ("sia", "harin", "mook"):
    history.setdefault(character_id, [])
```

새 캐릭터 `yuna`를 추가했다면 다음처럼 바꿔야 합니다.

```python
for character_id in ("sia", "harin", "mook", "yuna"):
    history.setdefault(character_id, [])
```

또는 더 좋은 방식으로 `CHARACTERS`를 기준으로 자동 처리하게 바꿀 수도 있습니다.

```python
for character_id in CHARACTERS:
    history.setdefault(character_id, [])
```

## LLM 진행 규칙: `llm_engine.py`

`llm_engine.py`는 게임 마스터 역할을 하는 LLM에게 어떤 규칙을 줄지 정합니다.

가장 중요한 부분은 `SYSTEM_PROMPT`입니다.

```python
SYSTEM_PROMPT = f"""
너는 한국어 텍스트 RPG '{GAME_TITLE}'의 환경 관찰자다.
...
""".strip()
```

여기에는 이런 규칙이 들어 있습니다.

- LLM은 세계를 마음대로 진행하지 않습니다.
- 플레이어가 입력한 단 하나의 행동만 tool로 처리합니다.
- 지도, 퍼즐, 목표, 캐릭터 속마음은 미리 말하지 않습니다.
- 다음 목표나 공략을 알려주지 않습니다.
- 캐릭터 대사는 `talk_to`가 처리합니다.
- 전투가 시작되면 버튼 UI를 띄우도록 `present_enemy_choice`를 호출합니다.

게임의 말투를 바꾸고 싶다면 이곳을 수정할 수 있습니다.

예를 들어 더 친절한 게임 마스터로 바꾸고 싶으면:

```text
- 최종 답변은 한국어 1~4문장으로, 플레이어가 방금 본 장면을 부드럽게 묘사한다.
```

하지만 너무 많은 힌트를 주지 않게 하려면 다음 규칙은 유지하는 것이 좋습니다.

```text
- 다음 목표, 선택지, 추천 행동, 공략, 숨은 정답을 말하지 않는다.
```

### 모델 이름

모델은 환경 변수에서 읽습니다.

```python
MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4")
```

환경 변수 `OPENAI_TEXT_MODEL`이 있으면 그 값을 쓰고, 없으면 기본값을 씁니다.

캐릭터 대사 생성은 `game_tools.py`의 `_character_reply()` 안에서 `OPENAI_CHARACTER_MODEL` 또는 `OPENAI_TEXT_MODEL`을 사용합니다.

## 화면 파일

화면은 세 파일이 함께 만듭니다.

| 파일 | 역할 |
| --- | --- |
| `templates/index.html` | 화면에 어떤 영역이 있는지 정합니다. |
| `static/app.js` | 서버에서 받은 데이터를 화면에 넣습니다. |
| `static/style.css` | 화면을 예쁘게 꾸미고 배치합니다. |

### `templates/index.html`

HTML에는 다음 영역이 있습니다.

| 영역 | 설명 |
| --- | --- |
| `left-panel` | 현재 상태, 체력, 위치, 출구, 인물, 인벤토리, 호감도 |
| `chat-panel` | 가운데 채팅창 |
| `right-panel` | 진행 기록, 적 정보, 대화 기록, 도구 호출 로그, tool schema |

새로운 정보 영역을 화면에 추가하고 싶으면 먼저 HTML에 공간을 만들고, 그 다음 `static/app.js`에서 값을 채우고, 마지막으로 `static/style.css`에서 스타일을 잡습니다.

### `static/app.js`

브라우저에서 실행되는 JavaScript입니다.

중요한 함수:

| 함수 | 역할 |
| --- | --- |
| `addMessage(role, text)` | 채팅 말풍선을 추가합니다. |
| `addCharacterMessage(character, line, emotion)` | 캐릭터 전용 말풍선을 추가합니다. |
| `addToolNotice(calls)` | 이번 턴에 어떤 tool이 호출됐는지 채팅에 표시합니다. |
| `renderEnemyChoices(calls)` | 적이 나타났을 때 싸운다/도망친다 버튼을 만듭니다. |
| `renderState(area)` | 현재 위치, 체력, 인벤토리, 호감도 등을 화면에 표시합니다. |
| `renderCharacterHistory(data)` | 캐릭터별 대화 기록을 표시합니다. |
| `renderToolCalls(calls)` | 오른쪽 tool 호출 로그를 표시합니다. |
| `sendText(text)` | 플레이어 입력을 서버로 보내고 결과를 받아 화면을 갱신합니다. |
| `loadState()` | 서버에서 현재 상태를 가져옵니다. |
| `loadTools()` | tool schema를 가져옵니다. |
| `loadHealth()` | API 키 연결 상태를 확인합니다. |

새 tool을 추가했다면 `TOOL_INFO`에도 표시 이름을 추가하면 좋습니다.

```javascript
const TOOL_INFO = {
  ...
  unlock_door: { icon: "🔓", label: "문을 연다" },
};
```

이것은 게임 기능에 꼭 필요한 것은 아니지만, 화면의 tool 호출 로그를 학생들이 읽기 쉽게 해 줍니다.

새 캐릭터를 추가했다면 `CHAR_NAMES`도 확인합니다.

```javascript
const CHAR_NAMES = { sia: "시아", harin: "하린", mook: "묵", yuna: "유나" };
```

### `static/style.css`

색, 배치, 간격, 말풍선 모양을 담당합니다.

자주 바꿀 만한 것:

- 배경색
- 패널 색
- 글꼴
- 말풍선 색
- 체력바 색
- 캐릭터 카드 모양
- 모바일 화면 배치

색상은 보통 파일 위쪽의 `:root`에 모여 있습니다.

```css
:root {
  --bg: #0f172a;
  --panel: rgba(15, 23, 42, 0.78);
  --text: #f8fafc;
  ...
}
```

디자인만 바꾸고 싶다면 Python 파일보다 CSS를 먼저 보는 것이 좋습니다.

## 서버 파일

### `app.py`

Flask 서버입니다.

주요 API:

| 주소 | 역할 |
| --- | --- |
| `/` | 게임 화면을 보여 줍니다. |
| `/api/state` | 현재 게임 상태를 반환합니다. |
| `/api/characters/history` | 캐릭터별 대화 기록을 반환합니다. |
| `/api/tools` | LLM에게 전달되는 tool schema를 반환합니다. |
| `/api/health` | API 키가 있는지 확인합니다. |
| `/api/reset` | 새 게임으로 초기화합니다. |
| `/api/chat` | 플레이어 입력을 받아 게임을 진행합니다. |

일반적인 게임 내용 수정에서는 `app.py`를 바꿀 일이 거의 없습니다.

### `run_game.py`

게임을 실행하는 시작 파일입니다.

```python
from example_game.app import run

if __name__ == "__main__":
    run()
```

기본 실행 포트는 `example_game/app.py`의 `run()` 함수에 있습니다.

```python
def run(port: int = 5051, open_page: bool = True) -> None:
```

포트를 바꾸고 싶으면 이 값을 바꿀 수 있습니다.

## 새 방 추가 체크리스트

새 방을 추가할 때는 이 순서로 확인하세요.

1. `game_data.py`의 `MAP`에 새 방 ID를 추가합니다.
2. 새 방에 `name`, `level`, `description`, `exits`, `items`, `characters`, `puzzle`을 넣습니다.
3. 기존 방의 `exits`에서 새 방으로 가는 길을 연결합니다.
4. 새 방에서 다시 돌아올 수 있는 길도 필요한지 확인합니다.
5. 새 아이템이 있다면 `LORE`에도 설명을 추가합니다.
6. 새 캐릭터가 있다면 `CHARACTERS`, `START_STATE`, `state.py`, `game_tools.py`, `static/app.js`를 확인합니다.
7. 새 퍼즐이 있다면 `PUZZLES`, `START_STATE["flags"]`, `solve_puzzle()` 타입을 확인합니다.
8. 새 적이 있다면 `ENEMIES`와 방의 `battle` 값을 확인합니다.
9. 게임을 새로 시작해서 이동이 되는지 확인합니다.

## 새 캐릭터 추가 체크리스트

1. `game_data.py`의 `CHARACTERS`에 새 캐릭터를 추가합니다.
2. `MAP`의 원하는 방 `characters`에 캐릭터 ID를 추가합니다.
3. `START_STATE["affection"]`에 캐릭터 ID를 추가합니다.
4. `START_STATE["character_history"]`에 캐릭터 ID를 추가합니다.
5. `game_tools.py`의 `CharacterId = Literal[...]`에 캐릭터 ID를 추가합니다.
6. `state.py`의 캐릭터 히스토리 보정 코드를 확인합니다.
7. `static/app.js`의 `CHAR_NAMES`에 화면 표시 이름을 추가합니다.
8. 캐릭터가 특별한 힌트나 보상을 주게 하고 싶으면 `game_tools.py`의 `_available_character_facts()`나 `talk_to()`를 수정합니다.

## 새 퍼즐 추가 체크리스트

1. `game_data.py`의 `PUZZLES`에 새 퍼즐을 추가합니다.
2. 퍼즐을 배치할 방의 `puzzle`에 퍼즐 ID를 넣습니다.
3. `START_STATE["flags"]`에 퍼즐 해결 여부를 저장할 값을 추가합니다.
4. 필요한 아이템이 있다면 그 아이템을 얻을 수 있는 방을 만듭니다.
5. 정답으로 인정할 표현을 `answer_keywords`에 여러 개 넣습니다.
6. `game_tools.py`의 `solve_puzzle()` 타입에 퍼즐 ID를 추가합니다.
7. 퍼즐이 다른 문을 열어야 한다면 `opens_flag`를 사용하거나 `move()`의 잠금 규칙을 수정합니다.
8. 새 게임으로 시작해서 정답과 오답을 모두 테스트합니다.

## 새 적 추가 체크리스트

1. `game_data.py`의 `ENEMIES`에 새 적을 추가합니다.
2. 적이 등장할 방에 `"battle": "적_ID"`를 넣습니다.
3. 약점 아이템이 실제로 얻을 수 있는지 확인합니다.
4. 전투 보상 `loot`가 너무 강하거나 약하지 않은지 확인합니다.
5. `battle_action()`의 피해량 규칙이 새 적에게도 잘 맞는지 확인합니다.
6. 보스처럼 특별한 조건에서만 나오게 하려면 `move()`에 조건을 추가합니다.

## 새 tool 추가 방법

새로운 행동을 만들고 싶다면 `game_tools.py`에 함수를 추가합니다.

예시:

```python
def unlock_door(door_name: str, key_name: str) -> dict:
    """열쇠를 사용해 특정 문을 연다."""
    state = load_state()
    if key_name not in state["inventory"]:
        return {"ok": False, "message": f"{key_name}이 없다."}
    state["flags"][f"{door_name}_open"] = True
    state["turn"] += 1
    save_state(state)
    return {"ok": True, "message": f"{door_name}이 열렸다.", "state": public_state(state)}
```

그 다음 맨 아래 `TOOLS`에 추가합니다.

```python
TOOLS = [
    inspect_area,
    reset_game,
    move,
    ...
    unlock_door,
]
```

화면의 tool 호출 로그를 보기 좋게 하려면 `static/app.js`의 `TOOL_INFO`에도 추가합니다.

```javascript
unlock_door: { icon: "🔓", label: "문을 연다" },
```

새 tool을 만들 때 중요한 점:

- 함수 이름은 영어와 밑줄을 사용합니다.
- 매개변수에는 타입 힌트를 씁니다.
- docstring에 언제 쓰는 tool인지 친절하게 적습니다.
- 반환값은 딕셔너리로 만듭니다.
- 상태를 바꿨으면 `save_state(state)`를 호출합니다.
- 플레이어에게 보여 줄 결과 메시지를 넣습니다.

## 자주 생기는 오류와 해결 방법

### 게임 데이터는 바꿨는데 화면이 그대로예요

저장 파일 때문에 그럴 수 있습니다.

해결:

- 화면에서 `새 게임` 버튼을 누릅니다.
- 그래도 이상하면 `example_game/saves/progress.json`을 삭제하고 다시 실행합니다.

### 새 방으로 이동이 안 돼요

확인할 것:

- 새 방 ID가 `MAP`에 실제로 있나요?
- 기존 방의 `exits`에 새 방으로 가는 연결이 있나요?
- 방향이 `북`, `남`, `동`, `서` 중 하나인가요?
- 오타가 있나요? 예: `"secret_room"`과 `"secert_room"`은 서로 다릅니다.

### 새 캐릭터와 대화가 안 돼요

확인할 것:

- `CHARACTERS`에 캐릭터가 있나요?
- 현재 방의 `characters`에 캐릭터 ID가 들어 있나요?
- `CharacterId = Literal[...]`에 캐릭터 ID를 추가했나요?
- `START_STATE["affection"]`과 `START_STATE["character_history"]`에 추가했나요?
- 저장 파일을 초기화했나요?

### 새 퍼즐을 LLM이 잘 못 풀어요

확인할 것:

- 퍼즐 ID가 방의 `puzzle`에 연결되어 있나요?
- `solve_puzzle()`의 `Literal[...]`에 퍼즐 ID를 추가했나요?
- `answer_keywords`에 학생들이 입력할 만한 표현을 충분히 넣었나요?
- `description`이 너무 모호하지 않나요?
- 필요한 아이템이나 플래그 조건이 너무 복잡하지 않나요?

### 새 적이 등장하지 않아요

확인할 것:

- 방에 `"battle": "적_ID"`가 있나요?
- 적 ID가 `ENEMIES`에 있나요?
- 이미 저장 파일에서 그 적이 `defeated_enemies`에 들어가 있지는 않나요?
- 새 게임을 눌러 봤나요?
- `move()`에 특정 적만 등장시키는 특별 조건이 있지는 않나요?

### API 키가 없다고 나와요

OpenAI API 키가 필요합니다.

`llm_engine.py`는 다음 위치에서 `.env` 파일을 찾습니다.

- `api_practice/.env`
- `tool_practice/.env`
- 프로젝트 루트의 `.env`

파일 안에는 보통 다음처럼 씁니다.

```env
OPENAI_API_KEY=여기에_키를_넣기
```

## 수정할 때 좋은 습관

한 번에 너무 많이 바꾸면 어디서 문제가 생겼는지 찾기 어렵습니다.

추천 순서:

1. 방 하나 추가하기
2. 새 게임으로 확인하기
3. 아이템 하나 추가하기
4. 새 게임으로 확인하기
5. 캐릭터 하나 추가하기
6. 새 게임으로 확인하기
7. 퍼즐 하나 추가하기
8. 새 게임으로 확인하기

이렇게 작게 바꾸면 오류를 찾기 쉽습니다.

## 이름을 지을 때 규칙

코드 안에서 쓰는 ID는 영어 소문자와 밑줄을 추천합니다.

좋은 예:

```python
"secret_classroom"
"shadow_monitor"
"blackboard_code"
```

피하는 것이 좋은 예:

```python
"비밀교실"
"Secret Classroom"
"secret-classroom"
```

화면에 보이는 이름은 한국어로 마음껏 써도 됩니다.

```python
"name": "비밀 교실"
```

정리하면:

- 내부 ID: 영어 소문자와 밑줄
- 화면 이름: 한국어 가능
- 아이템 이름: 한국어 가능
- 캐릭터 이름: 한국어 가능

## 가장 안전한 수정 범위

처음 수정하는 학생에게 추천하는 범위:

- `GAME_TITLE`
- `MAP`의 방 이름과 설명
- `MAP`의 아이템 목록
- `CHARACTERS`의 이름, 역할, 성격, 기본 대사
- `LORE` 설명
- `ENEMIES`의 체력, 공격력, 보상
- `PUZZLES`의 설명과 정답 키워드
- `static/style.css`의 색상

조금 익숙해진 뒤 수정하면 좋은 범위:

- 새 방 추가
- 새 캐릭터 추가
- 새 퍼즐 추가
- 새 적 추가
- `move()`의 잠긴 문 규칙
- `talk_to()`의 캐릭터 보상 규칙
- `battle_action()`의 전투 밸런스

더 어려운 범위:

- 완전히 새로운 tool 추가
- 저장 상태 구조 변경
- 프론트엔드 UI 영역 추가
- LLM 진행 규칙 크게 변경
- 여러 단계로 이어지는 복잡한 퀘스트 만들기

## 마지막으로 기억할 것

이 게임은 단순히 채팅 답변만 만드는 프로그램이 아닙니다.

플레이어의 말은 LLM이 읽지만, 실제 게임 상태를 바꾸는 것은 `game_tools.py`의 함수입니다. 그리고 그 함수들이 사용하는 세계 설정은 대부분 `game_data.py`에 있습니다.

그래서 게임을 다듬을 때는 이렇게 생각하면 좋습니다.

- "무엇이 존재하는가?"는 `game_data.py`
- "무엇을 할 수 있는가?"는 `game_tools.py`
- "지금 어디까지 진행됐는가?"는 `state.py`
- "LLM이 어떤 태도로 진행하는가?"는 `llm_engine.py`
- "화면에 어떻게 보이는가?"는 `templates/index.html`, `static/app.js`, `static/style.css`

처음에는 `game_data.py`를 바꾸는 것만으로도 완전히 다른 분위기의 게임을 만들 수 있습니다.
