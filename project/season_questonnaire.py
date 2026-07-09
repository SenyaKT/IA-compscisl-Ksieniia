QUESTIONS=[
    { 
        "key": "skin_undertone",
        "text": "What is your skin undertone?",
        "options":[
                ("Warm (yellow / golden / peachy)", "warm"), 
                ("Cool (pink / blue / rosy)", "cool"),
                ("Neutral (a mix / unsure)", "neutral")
                    ]
    }
    { 
        "key": "skin_depth",
        "text": "What is your skin depth?",
        "options":[
                ("Light", "light"), 
                ("Medium", "medium"),
                ("Deep", "deep")
                ]            
    }
    { 
        "key": "hair_color",
        "text": "What is your hair color?",
        "options":[
                ("Blonde", "blonde"), 
                ("Light Brown", "light_brown"),
                ("Medium Brown", "medium_brown"),
                ("Dark Brown", "dark_brown"),
                ("Black", "black"),
                ("Red", "red"),
                ("Auburn", "auburn"),
                ("Grey", "grey")
                ]
    }
    { 
        "key": "eye_color",
        "text": "What is your eye color?",
        "options":[
                ("Light blue", "light_blue"), 
                ("Light green", "light_green"),
                ("Green", "green"),
                ("Hazel", "hazel"),
                ("Medium brown", "medium_brown"),
                ("Dark brown", "dark_brown"),
                ("Black", "black")
                ]
    }
    { 
        "key": "lip_color",
        "text": "What is your lip color?",
        "options":[
                ("Cool pink", "cool_pink"), 
                ("Neutral", "neutral"),
                ("Warm peach", "warm_peach"),
                ("Warm brown", "warm_brown")
                ]
    }
    { 
        "key": "vein_color",
        "text": "What is your vein color?",
        "options":[
                ("Blue or purple", "blue_purple"), 
                ("Green", "green"),
                ("Mixed", "mixed")
                ]
    } 
    { 
        "key": "contrast_level",
        "text": "What is your appearance contrast level?",
        "options":[
                ("Low", "blue_purple"), 
                ("Medium", "medium"),
                ("High", "high")
                ]
    }
    { 
        "key": "skin_clarity",
        "text": "What is your skin clarity and freshness?",
        "options":[
                ("Bright", "bright"), 
                ("Muted", "muted"),
                ("Mixed", "mixed")
                ]
    }
             
]

def all_answered(answers):
    for q in QUESTIONS:
        if not answers.get(q["key"]):
            return False
    return True