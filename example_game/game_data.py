from __future__ import annotations

GAME_TITLE = "달빛 기록관: 망각의 층"

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

MAP = {
    "lobby": {
        "name": "은빛 로비",
        "level": 1,
        "description": "천장에는 멈춘 별자리 시계가 걸려 있고, 바닥의 물자국은 북쪽 서가로 이어진다.",
        "exits": {"북": "west_stacks", "동": "clock_hall"},
        "items": ["성냥갑"],
        "characters": ["sia"],
        "puzzle": None,
    },
    "west_stacks": {
        "name": "서쪽 서가",
        "level": 1,
        "description": "젖은 책들이 스스로 페이지를 넘긴다. 책등 사이에서 푸른 금속 조각이 반짝인다.",
        "exits": {"남": "lobby", "동": "clock_hall", "북": "mirror_archive"},
        "items": ["청동 톱니"],
        "characters": ["mook"],
        "puzzle": None,
    },
    "clock_hall": {
        "name": "시계 복도",
        "level": 2,
        "description": "벽시계 수십 개가 서로 다른 어제를 가리킨다. 중앙 장치에는 톱니가 하나 비어 있다.",
        "exits": {"서": "lobby", "동": "garden"},
        "items": [],
        "characters": [],
        "puzzle": "clockwork",
    },
    "garden": {
        "name": "실내 달빛정원",
        "level": 2,
        "description": "유리 천장 아래 은색 풀이 흔들린다. 하린이 접힌 우산을 들고 달빛을 재고 있다.",
        "exits": {"서": "clock_hall", "북": "mirror_archive"},
        "items": ["달유리 조각"],
        "characters": ["harin"],
        "puzzle": None,
    },
    "mirror_archive": {
        "name": "거울 기록실",
        "level": 3,
        "description": "거울마다 다른 기억이 비친다. 가운데 봉인문에는 세 글자 수수께끼가 새겨져 있다.",
        "exits": {"남": "west_stacks", "동": "garden", "북": "observatory"},
        "items": [],
        "characters": ["sia"],
        "puzzle": "rune_door",
    },
    "observatory": {
        "name": "검은 별 관측소",
        "level": 4,
        "description": "무너진 돔 사이로 검은 별이 내려다본다. 망각 서기관이 마지막 기록장을 움켜쥐고 있다.",
        "exits": {"남": "mirror_archive"},
        "items": [],
        "characters": [],
        "puzzle": None,
        "battle": "forgotten_scribe",
    },
}

CHARACTERS = {
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
    "harin": {
        "name": "하린",
        "role": "달빛을 측정하는 정원사",
        "emoji": "🌙",
        "accent": "#bda7ff",
        "personality": "농담을 섞어 긴장을 풀어 주지만 관찰력이 날카롭다.",
        "context": "전투 중 달빛 물약을 만들 수 있다. 호감도가 높으면 회복 아이템을 준다.",
        "dialogue": {
            "default": "달빛은 거짓말을 못 해요. 대신 너무 솔직해서 문제가 되죠.",
            "gift": "당신 표정이 너무 창백해요. 달빛 물약 하나 가져가요.",
            "bond": "달빛 측정값이 당신 곁에서만 흔들려요. 이런 건 처음이에요. …농담이 아니라요.",
        },
    },
    "mook": {
        "name": "묵",
        "role": "말하는 색인 카드",
        "emoji": "📇",
        "accent": "#e7bc68",
        "personality": "건방진 말투지만 규칙과 지도에는 누구보다 정확하다.",
        "context": "지도, 퍼즐 조건, 전투 약점을 알려 주는 지원 캐릭터.",
        "dialogue": {
            "default": "흠. 또 길 잃은 인간인가. 좋아, 이번엔 색인 순서대로 설명해 주지.",
            "weakness": "서기관은 빛에 약해. 성냥, 달유리, 시아의 기억. 이런 것들을 엮어 봐.",
            "bond": "…너 같은 인간은 색인에 없었어. 새 항목을 만들어 주지. '믿을 만한 자' 라고.",
        },
    },
}

# examine 도구가 사용하는 사물·장소·인물의 묘사. 게임 세계를 더 풍성하게 한다.
LORE = {
    "낡은 열쇠": "동생이 쓰던 일기장 자물쇠와 똑같은 무늬가 새겨져 있다. 어디엔가 맞는 자물쇠가 있을 것이다.",
    "회복 사탕": "달빛에 절인 박하 사탕. 입에 물면 상처가 천천히 아문다.",
    "성냥갑": "축축한데도 불이 잘 붙는다. 종이로 된 적에게 특히 효과가 있을 것 같다.",
    "청동 톱니": "시계 복도의 빈 장치에 꼭 맞아 보인다. 표면에 별자리가 음각되어 있다.",
    "달유리 조각": "달빛을 머금으면 스스로 빛난다. 어둠을 두려워하는 존재에게 치명적이다.",
    "별자리 바늘": "시계를 고치면 얻는 바늘. 가리키는 방향마다 다른 기억이 떠오른다.",
    "검은 별 열쇠": "관측소의 마지막 문을 여는 열쇠. 만지면 손끝이 시리다.",
    "별자리 시계": "멈춰 있다. 톱니를 끼우고 '새벽 3시'에 맞추면 무언가 깨어날 것 같다.",
    "거울 봉인문": "세 글자 수수께끼가 새겨져 있다. '잃어도 너를 너로 남기는 세 글자는?'",
    "동생": "초대장에 적힌 이름의 주인. 이 기록관 어딘가에 기억이 책으로 묶여 있다.",
}

PUZZLES = {
    "clockwork": {
        "name": "별자리 시계",
        "description": "비어 있는 장치에 청동 톱니를 끼우고 시간을 '새벽 3시'로 맞춰야 한다.",
        "required_item": "청동 톱니",
        "answer_keywords": ["새벽 3시", "3시", "세시"],
        "reward_items": ["별자리 바늘"],
        "flag": "clock_fixed",
        "journal": "별자리 시계를 고치자 거울 기록실의 봉인문이 약해졌다.",
    },
    "rune_door": {
        "name": "거울 봉인문",
        "description": "문장은 '잃어도 너를 너로 남기는 세 글자는?' 이라고 묻는다.",
        "required_flag": "clock_fixed",
        "answer_keywords": ["기억"],
        "reward_items": ["검은 별 열쇠"],
        "flag": "rune_answered",
        "opens_flag": "boss_open",
        "journal": "거울 봉인문에 '기억'이라 답하자 관측소로 가는 길이 열렸다.",
    },
}

ENEMIES = {
    "paper_moth": {
        "name": "종이 나방",
        "hp": 12,
        "attack": 3,
        "xp": 4,
        "weakness": "성냥갑",
        "loot": ["찢어진 색인표"],
    },
    "forgotten_scribe": {
        "name": "망각 서기관",
        "hp": 30,
        "attack": 6,
        "xp": 20,
        "weakness": "달유리 조각",
        "loot": ["동생의 마지막 기록"],
    },
}
