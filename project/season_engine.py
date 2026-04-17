"""
season_engine.py
----------------
Classifies a user into one of 16 seasonal tones based on:
  - Questionnaire answers (skin undertone, hair, eyes, lips, veins)
  - Wrist photo analysis results (from WristColorAnalyzer)

The 16 tones are: 4 base seasons × 4 sub-types each
  Spring: True Spring, Light Spring, Bright Spring, Warm Spring
  Summer: True Summer, Light Summer, Soft Summer, Cool Summer
  Autumn: True Autumn, Deep Autumn, Soft Autumn, Warm Autumn
  Winter: True Winter, Deep Winter, Bright Winter, Cool Winter
"""

# ─────────────────────────────────────────────
# DATA: All 16 seasonal tones with descriptions
# and their best matching color palettes
# ─────────────────────────────────────────────

SEASON_INFO = {
    # ── SPRING ──────────────────────────────────────────────────
    "True Spring": {
        "season": "Spring",
        "tone": "True",
        "description": "Warm, clear, and medium-bright. Golden undertone, fresh and vibrant look.",
        "keywords": ["warm", "clear", "medium contrast"],
        "best_colors": ["#F4A460", "#FFD700", "#FFA500", "#FF6347", "#90EE90",
                        "#7CFC00", "#FFDAB9", "#FFE4B5", "#FFF8DC", "#FF8C00",
                        "#DAA520", "#B8860B", "#CD853F", "#DEB887", "#F5DEB3"],
    },
    "Light Spring": {
        "season": "Spring",
        "tone": "Light",
        "description": "Warm and delicate. Light, soft features with a peachy or golden glow.",
        "keywords": ["warm", "light", "delicate"],
        "best_colors": ["#FFDAB9", "#FFE4C4", "#FAFAD2", "#FFFACD", "#FFF0F5",
                        "#FFB6C1", "#FFEFD5", "#FFF5EE", "#FFFFE0", "#98FB98",
                        "#AFEEEE", "#E0FFFF", "#F0FFF0", "#FFFAF0", "#FAF0E6"],
    },
    "Bright Spring": {
        "season": "Spring",
        "tone": "Bright",
        "description": "Warm and vivid. High contrast, bright eyes, clear and bold features.",
        "keywords": ["warm", "bright", "high contrast"],
        "best_colors": ["#FF4500", "#FF6347", "#FFA500", "#FFD700", "#ADFF2F",
                        "#00FF7F", "#00CED1", "#FF1493", "#FF69B4", "#FF8C00",
                        "#FFFF00", "#7FFF00", "#00FA9A", "#20B2AA", "#FF00FF"],
    },
    "Warm Spring": {
        "season": "Spring",
        "tone": "Warm",
        "description": "Deeply warm. Golden-amber undertones, peachy or terracotta coloring.",
        "keywords": ["warm", "golden", "peachy"],
        "best_colors": ["#D2691E", "#CD853F", "#A0522D", "#8B4513", "#DAA520",
                        "#B8860B", "#FF8C00", "#FFA500", "#FF7F50", "#F4A460",
                        "#DEB887", "#D2B48C", "#BC8F8F", "#F08080", "#E9967A"],
    },

    # ── SUMMER ──────────────────────────────────────────────────
    "True Summer": {
        "season": "Summer",
        "tone": "True",
        "description": "Cool, muted, and soft. Ash-toned hair, pinkish skin, dusty colors.",
        "keywords": ["cool", "muted", "soft"],
        "best_colors": ["#B0C4DE", "#ADD8E6", "#87CEEB", "#778899", "#708090",
                        "#C0C0C0", "#D8BFD8", "#DDA0DD", "#EE82EE", "#9370DB",
                        "#8A2BE2", "#6A5ACD", "#7B68EE", "#4169E1", "#5F9EA0"],
    },
    "Light Summer": {
        "season": "Summer",
        "tone": "Light",
        "description": "Cool and very light. Pale, delicate features with cool pink undertones.",
        "keywords": ["cool", "light", "pale"],
        "best_colors": ["#E6E6FA", "#F0F8FF", "#E0FFFF", "#F5F5F5", "#FFF0F5",
                        "#FFE4E1", "#FFEFD5", "#F8F8FF", "#F0FFFF", "#F5FFFA",
                        "#DCDCDC", "#D3D3D3", "#C0C0C0", "#B0C4DE", "#AFEEEE"],
    },
    "Soft Summer": {
        "season": "Summer",
        "tone": "Soft",
        "description": "Cool and muted. The softest seasonal type — dusty, greyed tones.",
        "keywords": ["cool", "muted", "greyed"],
        "best_colors": ["#9E8FAD", "#8FADB0", "#9E8FAD", "#A0A0A0", "#8B7D82",
                        "#96816E", "#9B8EA0", "#888FAD", "#8DA88F", "#AD9688",
                        "#B0A0B0", "#A8B0A0", "#9098A8", "#A09090", "#888098"],
    },
    "Cool Summer": {
        "season": "Summer",
        "tone": "Cool",
        "description": "Strongly cool. Icy undertones, pink or blue-tinted skin, high cool contrast.",
        "keywords": ["cool", "icy", "pink tones"],
        "best_colors": ["#E8D0E8", "#D0D8E8", "#D8E0F0", "#C8D0E8", "#E0D0F0",
                        "#D8C8E0", "#C8E0E8", "#E0C8E0", "#D0E8D8", "#C8D8F0",
                        "#C8C0D8", "#D8D0E8", "#C0C8E0", "#D0C8D8", "#C8D0D8"],
    },

    # ── AUTUMN ──────────────────────────────────────────────────
    "True Autumn": {
        "season": "Autumn",
        "tone": "True",
        "description": "Rich and warm. Golden or olive skin, earthy deep coloring.",
        "keywords": ["warm", "earthy", "medium-deep"],
        "best_colors": ["#8B4513", "#A0522D", "#6B4226", "#CD853F", "#D2691E",
                        "#B8860B", "#DAA520", "#808000", "#556B2F", "#6B8E23",
                        "#8FBC8F", "#2E8B57", "#228B22", "#006400", "#8B0000"],
    },
    "Deep Autumn": {
        "season": "Autumn",
        "tone": "Deep",
        "description": "Very rich and dark. Deep, warm features with high contrast and depth.",
        "keywords": ["warm", "deep", "high contrast"],
        "best_colors": ["#4A0000", "#800000", "#8B0000", "#A52A2A", "#6B0000",
                        "#3B1005", "#4B2200", "#5B3300", "#2D4A00", "#1A3A00",
                        "#4A3000", "#3A2000", "#2A1500", "#1A0A00", "#0A0500"],
    },
    "Soft Autumn": {
        "season": "Autumn",
        "tone": "Soft",
        "description": "Warm and muted. Softer earthy tones, medium contrast.",
        "keywords": ["warm", "muted", "earthy-soft"],
        "best_colors": ["#C4A882", "#B89870", "#A08860", "#BC9A7A", "#AA8870",
                        "#988060", "#8A9870", "#9A8878", "#8A9080", "#9A8870",
                        "#B8A890", "#A89880", "#908880", "#988890", "#A09080"],
    },
    "Warm Autumn": {
        "season": "Autumn",
        "tone": "Warm",
        "description": "Intensely warm. Orange and golden undertones dominate.",
        "keywords": ["warm", "orange", "golden-deep"],
        "best_colors": ["#FF6600", "#FF4500", "#FF7F50", "#FF8C00", "#FFA500",
                        "#CC5500", "#AA4400", "#993300", "#882200", "#771100",
                        "#CC7700", "#AA6600", "#885500", "#664400", "#443300"],
    },

    # ── WINTER ──────────────────────────────────────────────────
    "True Winter": {
        "season": "Winter",
        "tone": "True",
        "description": "Cool and high contrast. Sharp, vivid coloring with clear cool undertones.",
        "keywords": ["cool", "high contrast", "vivid"],
        "best_colors": ["#000000", "#FFFFFF", "#FF0000", "#0000FF", "#FF00FF",
                        "#00FFFF", "#800080", "#008000", "#000080", "#800000",
                        "#C0C0C0", "#808080", "#FF1493", "#00FF00", "#8A2BE2"],
    },
    "Deep Winter": {
        "season": "Winter",
        "tone": "Deep",
        "description": "Dark, cool and rich. Very deep features with cool undertones.",
        "keywords": ["cool", "deep", "dark"],
        "best_colors": ["#1C1C2E", "#000033", "#000066", "#330033", "#003300",
                        "#660000", "#003333", "#330000", "#1A001A", "#001A1A",
                        "#2D0A2D", "#0A2D2D", "#2D0A0A", "#0A0A2D", "#000000"],
    },
    "Bright Winter": {
        "season": "Winter",
        "tone": "Bright",
        "description": "Cool and very clear. Icy and vivid colors, striking contrast.",
        "keywords": ["cool", "bright", "icy-vivid"],
        "best_colors": ["#00FFFF", "#FF00FF", "#FFFFFF", "#0000FF", "#FF0000",
                        "#00FF00", "#FFD700", "#FF1493", "#00CED1", "#7B68EE",
                        "#FF4500", "#9400D3", "#00BFFF", "#FF69B4", "#1E90FF"],
    },
    "Cool Winter": {
        "season": "Winter",
        "tone": "Cool",
        "description": "Purely cool. Blue-pink undertones, icy and refined coloring.",
        "keywords": ["cool", "icy", "blue-pink"],
        "best_colors": ["#E8E8F8", "#D8D8F0", "#C8C8E8", "#B8B8E0", "#A8A8D8",
                        "#F0E8F8", "#E8D8F8", "#D8C8F0", "#C8B8E8", "#B8A8E0",
                        "#E8F0F8", "#D8E8F0", "#C8D8E8", "#B8C8E0", "#A8B8D8"],
    },
}


# ─────────────────────────────────────────────
# SCORING SYSTEM
# Each question answer gives points to certain seasons
# Higher score = better match
# ─────────────────────────────────────────────

def classify_season(answers: dict, wrist_data: dict = None) -> dict:
    """
    answers = {
        "skin_undertone": "warm" | "cool" | "neutral",
        "skin_depth":     "light" | "medium" | "deep",
        "hair_color":     "blonde" | "light_brown" | "medium_brown" |
                          "dark_brown" | "black" | "red" | "auburn" | "grey",
        "eye_color":      "light_blue" | "light_grey" | "green" | "hazel" |
                          "medium_brown" | "dark_brown" | "black",
        "lip_color":      "cool_pink" | "neutral" | "warm_peach" | "warm_brown",
        "vein_color":     "blue_purple" | "green" | "mixed",
        "contrast_level": "low" | "medium" | "high",
        "skin_clarity":   "clear" | "muted" | "bright",
    }

    wrist_data = output of WristColorAnalyzer.get_results() (optional)

    Returns the best-matching season name + full info.
    """

    scores = {name: 0 for name in SEASON_INFO}

    # ── UNDERTONE (most important factor, weight ×3) ──────────
    undertone = answers.get("skin_undertone", "neutral")
    if wrist_data:
        # Combine questionnaire + image analysis
        wrist_undertone = wrist_data.get("undertone", "Neutral").lower()
        if wrist_undertone == undertone:
            weight = 4  # strong agreement
        else:
            weight = 2  # disagreement — use average
        undertone = undertone  # keep questionnaire as primary
    else:
        weight = 3

    warm_seasons  = ["True Spring","Light Spring","Bright Spring","Warm Spring",
                     "True Autumn","Deep Autumn","Soft Autumn","Warm Autumn"]
    cool_seasons  = ["True Summer","Light Summer","Soft Summer","Cool Summer",
                     "True Winter","Deep Winter","Bright Winter","Cool Winter"]

    if undertone == "warm":
        for s in warm_seasons:  scores[s] += weight
    elif undertone == "cool":
        for s in cool_seasons:  scores[s] += weight
    else:  # neutral
        for s in warm_seasons:  scores[s] += 1
        for s in cool_seasons:  scores[s] += 1

    # ── SKIN DEPTH (light vs deep) ────────────────────────────
    depth = answers.get("skin_depth", "medium")
    light_seasons = ["Light Spring","Light Summer","True Spring","True Summer",
                     "Soft Spring","Soft Summer","Bright Spring","Cool Summer"]
    deep_seasons  = ["Deep Autumn","Deep Winter","True Autumn","True Winter",
                     "Warm Autumn","Cool Winter","Bright Winter"]
    if depth == "light":
        for s in light_seasons:
            if s in scores: scores[s] += 2
    elif depth == "deep":
        for s in deep_seasons:
            if s in scores: scores[s] += 2

    # ── HAIR COLOR ────────────────────────────────────────────
    hair = answers.get("hair_color", "medium_brown")
    hair_map = {
        "blonde":        ["Light Spring","True Spring","Bright Spring"],
        "light_brown":   ["True Spring","Warm Spring","Light Summer","Soft Summer"],
        "medium_brown":  ["True Autumn","Soft Autumn","Warm Autumn","True Summer"],
        "dark_brown":    ["Deep Autumn","True Winter","Deep Winter","True Autumn"],
        "black":         ["True Winter","Deep Winter","Bright Winter","Cool Winter"],
        "red":           ["True Autumn","Warm Autumn","Warm Spring"],
        "auburn":        ["True Autumn","Deep Autumn","Warm Autumn","Warm Spring"],
        "grey":          ["Cool Summer","True Summer","Soft Summer"],
    }
    for s in hair_map.get(hair, []):
        if s in scores: scores[s] += 2

    # ── EYE COLOR ────────────────────────────────────────────
    eye = answers.get("eye_color", "medium_brown")
    eye_map = {
        "light_blue":    ["True Summer","Light Summer","Cool Summer","Cool Winter"],
        "light_grey":    ["True Summer","Soft Summer","Light Summer"],
        "green":         ["True Spring","Bright Spring","Soft Autumn","True Autumn"],
        "hazel":         ["True Autumn","Soft Autumn","Warm Autumn","Warm Spring"],
        "medium_brown":  ["True Autumn","Soft Autumn","Soft Summer","True Summer"],
        "dark_brown":    ["Deep Autumn","True Winter","Deep Winter","Warm Autumn"],
        "black":         ["True Winter","Deep Winter","Bright Winter","Cool Winter"],
    }
    for s in eye_map.get(eye, []):
        if s in scores: scores[s] += 2

    # ── LIP COLOR ────────────────────────────────────────────
    lip = answers.get("lip_color", "neutral")
    lip_map = {
        "cool_pink":   ["True Summer","Cool Summer","True Winter","Cool Winter","Bright Winter"],
        "neutral":     ["Soft Summer","Soft Autumn","Light Summer","Light Spring"],
        "warm_peach":  ["True Spring","Light Spring","Warm Spring","Bright Spring"],
        "warm_brown":  ["True Autumn","Deep Autumn","Warm Autumn","Warm Spring"],
    }
    for s in lip_map.get(lip, []):
        if s in scores: scores[s] += 1

    # ── VEIN COLOR ────────────────────────────────────────────
    vein = answers.get("vein_color", "mixed")
    # Also include wrist photo vein data if available
    if wrist_data:
        photo_vein = wrist_data.get("vein_color", "Mixed")
        if photo_vein == "Blue/Purple" and vein != "green":
            vein = "blue_purple"
        elif photo_vein == "Green" and vein != "blue_purple":
            vein = "green"

    if vein == "blue_purple":
        for s in cool_seasons: scores[s] += 2
    elif vein == "green":
        for s in warm_seasons: scores[s] += 2
    # mixed = no extra points

    # ── CONTRAST LEVEL ────────────────────────────────────────
    contrast = answers.get("contrast_level", "medium")
    high_contrast = ["True Winter","Bright Winter","Deep Winter","Bright Spring",
                     "Deep Autumn","Cool Winter"]
    low_contrast  = ["Light Spring","Light Summer","Soft Summer","Soft Autumn"]
    if contrast == "high":
        for s in high_contrast:
            if s in scores: scores[s] += 2
    elif contrast == "low":
        for s in low_contrast:
            if s in scores: scores[s] += 2

    # ── CLARITY ─────────────────────────────────────────────
    clarity = answers.get("skin_clarity", "muted")
    if clarity == "bright":
        for s in ["Bright Spring","Bright Winter","True Spring","True Winter"]:
            if s in scores: scores[s] += 2
    elif clarity == "muted":
        for s in ["Soft Summer","Soft Autumn","True Summer","True Autumn"]:
            if s in scores: scores[s] += 2

    # ── FIND WINNER ──────────────────────────────────────────
    best = max(scores, key=lambda k: scores[k])
    top3 = sorted(scores, key=lambda k: scores[k], reverse=True)[:3]

    result = dict(SEASON_INFO[best])
    result["season_name"] = best
    result["score"] = scores[best]
    result["all_scores"] = scores
    result["top3"] = [(s, scores[s]) for s in top3]

    return result


def get_color_combinations(season_name: str) -> list:
    """
    Returns suggested clothing color combinations for a season.
    Each combination is a list of 3 hex colors that work well together.
    """
    combos = {
        "True Spring":    [("#F4A460","#FFD700","#90EE90"), ("#FFA500","#FFDAB9","#CD853F")],
        "Light Spring":   [("#FFDAB9","#98FB98","#AFEEEE"), ("#FFE4C4","#E0FFFF","#FFEFD5")],
        "Bright Spring":  [("#FF4500","#FFD700","#00CED1"), ("#FF6347","#ADFF2F","#FF69B4")],
        "Warm Spring":    [("#D2691E","#DAA520","#F4A460"), ("#A0522D","#FF7F50","#DEB887")],
        "True Summer":    [("#B0C4DE","#DDA0DD","#778899"), ("#ADD8E6","#9370DB","#708090")],
        "Light Summer":   [("#E6E6FA","#AFEEEE","#FFE4E1"), ("#F0F8FF","#D8BFD8","#DCDCDC")],
        "Soft Summer":    [("#9E8FAD","#8DA88F","#A8B0A0"), ("#B0A0B0","#A09090","#908880")],
        "Cool Summer":    [("#C8D0E8","#D8C8F0","#E8D0E8"), ("#D0D8E8","#C8B8E0","#E8E8F8")],
        "True Autumn":    [("#8B4513","#DAA520","#556B2F"), ("#A0522D","#808000","#CD853F")],
        "Deep Autumn":    [("#4A0000","#003300","#330000"), ("#800000","#006400","#1C1C2E")],
        "Soft Autumn":    [("#C4A882","#8A9070","#A89880"), ("#B89870","#9A8878","#908880")],
        "Warm Autumn":    [("#FF6600","#CC5500","#884400"), ("#FF4500","#AA4400","#663300")],
        "True Winter":    [("#000000","#FF0000","#FFFFFF"), ("#000080","#FF00FF","#C0C0C0")],
        "Deep Winter":    [("#1C1C2E","#000066","#330033"), ("#000033","#003300","#660000")],
        "Bright Winter":  [("#00FFFF","#FF00FF","#FFFFFF"), ("#0000FF","#FF0000","#FFD700")],
        "Cool Winter":    [("#E8E8F8","#D8C8F0","#C8D8E8"), ("#F0E8F8","#C8B8E0","#B8C8E0")],
    }
    return combos.get(season_name, [])
