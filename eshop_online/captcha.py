import random


def generate_captcha(request):
    """
    Generates a simple math question, stores the answer in the session,
    and returns the question text to display to the user.
    """
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    request.session['captcha_answer'] = a + b
    question = f'What is {a} + {b}?'
    request.session['captcha_question'] = question
    return question


def verify_captcha(request, user_answer):
    """
    Checks the submitted answer against the one stored in session.
    Clears the session value afterward so it can't be reused (replay protection).
    """
    expected = request.session.pop('captcha_answer', None)
    request.session.pop('captcha_question', None)

    if expected is None:
        return False

    try:
        return int(user_answer) == expected
    except (TypeError, ValueError):
        return False
