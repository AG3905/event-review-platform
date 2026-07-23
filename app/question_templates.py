SUGGESTED_QUESTIONS = {
    'Music': [
        {'text': 'How was the sound quality?', 'type': 'rating', 'required': True},
        {'text': 'Was the setlist/lineup good?', 'type': 'yes_no', 'required': False},
        {'text': 'How were the venue acoustics?', 'type': 'rating', 'required': False},
        {'text': 'Would you attend again?', 'type': 'yes_no', 'required': False},
    ],
    'Comedy': [
        {'text': 'How funny was the material?', 'type': 'rating', 'required': True},
        {'text': 'Was the venue comfortable?', 'type': 'rating', 'required': False},
        {'text': 'Did the show run on time?', 'type': 'yes_no', 'required': False},
    ],
    'Workshop': [
        {'text': 'Was the content clear?', 'type': 'rating', 'required': True},
        {'text': 'Was the pace right?', 'type': 'single_choice', 'options': ['Too slow', 'Just right', 'Too fast'], 'required': False},
        {'text': 'Would you recommend this workshop to a colleague?', 'type': 'yes_no', 'required': False},
    ],
    'Conference': [
        {'text': 'How was the speaker quality?', 'type': 'rating', 'required': True},
        {'text': 'How were the networking opportunities?', 'type': 'rating', 'required': False},
        {'text': 'Was registration/check-in smooth?', 'type': 'yes_no', 'required': False},
    ],
    'Sports': [
        {'text': 'How was the atmosphere/energy?', 'type': 'rating', 'required': True},
        {'text': 'How were the facilities/seating?', 'type': 'rating', 'required': False},
        {'text': 'Would you attend another match here?', 'type': 'yes_no', 'required': False},
    ],
    'Wedding': [
        {'text': 'Was the venue beautiful?', 'type': 'rating', 'required': False},
        {'text': 'Was the catering good?', 'type': 'rating', 'required': False},
        {'text': 'Any highlight moment you want to share?', 'type': 'text', 'required': False},
    ],
    'Corporate': [
        {'text': 'Was this event relevant to your work?', 'type': 'rating', 'required': True},
        {'text': 'Would you attend a follow-up event?', 'type': 'yes_no', 'required': False},
    ],
    'Other': [
        {'text': 'Overall, how would you rate this event?', 'type': 'rating', 'required': True},
        {'text': 'What did you enjoy most?', 'type': 'text', 'required': False},
        {'text': 'What could be improved?', 'type': 'text', 'required': False},
    ],
}

DEFAULT_LOCATION_QUESTIONS = [
    {'text': 'What town/city are you from?', 'type': 'text', 'required': False, 'key': 'reviewer_town'},
    {'text': 'What state/province are you from?', 'type': 'text', 'required': False, 'key': 'reviewer_state'},
]


def suggest_questions_for(category_text):
    if not category_text:
        return SUGGESTED_QUESTIONS['Other']
    
    text = str(category_text).strip().lower()
    
    # Exact match first
    for cat in SUGGESTED_QUESTIONS:
        if cat.lower() == text:
            return SUGGESTED_QUESTIONS[cat]
            
    # Keyword match
    for cat in SUGGESTED_QUESTIONS:
        if cat != 'Other' and cat.lower() in text:
            return SUGGESTED_QUESTIONS[cat]
            
    return SUGGESTED_QUESTIONS['Other']
