"""
QUESTIONS DATA
--------------
This is the ONLY file you should need to edit to change what's in the quiz.

Each question is a dict with:
    title        short name shown as the stage label
    prompt       the question text
    snippet      optional code/table block shown above the question
                 (use "\n" for line breaks, "" to omit)
    hint         optional help text, only shown if the player taps "Hint"
    answers      list of accepted answers (case-insensitive, spaces ignored)
    points       points earned for a correct answer

Add, remove, or edit questions freely -- app.py does not need to change.
"""

QUESTIONS = [
    {
        "title": "The First Vault",
        "prompt": (
            "A stack starts empty. The following operations run in order:\n"
            "push(1), push(2), push(3), pop(), push(4), pop()\n\n"
            "What single value now sits on top of the stack?"
        ),
        "snippet": "",
        "hint": "Trace it step by step: after the two pops, only two values remain. Which one was pushed most recently?",
        "answers": ["2"],
        "points": 100,
    },
    {
        "title": "The Query Room",
        "prompt": "A table called Students is shown below. How many students scored above 80?",
        "snippet": (
            "id | name  | marks\n"
            "---+-------+------\n"
            " 1 | Aria  |  92\n"
            " 2 | Kabir |  76\n"
            " 3 | Zara  |  85\n"
            " 4 | Dev   |  60\n"
            " 5 | Mira  |  81"
        ),
        "hint": "List only the marks strictly greater than 80: 92, 85, 81. Count them.",
        "answers": ["3", "three"],
        "points": 100,
    },
    {
        "title": "Between the Networks",
        "prompt": "Which OSI layer is responsible for routing data between different networks using logical addresses like IP?",
        "snippet": "",
        "hint": "This is the layer where IP addresses and routers operate.",
        "answers": ["network", "network layer"],
        "points": 100,
    },
    {
        "title": "Department of Averages",
        "prompt": (
            "Table Employees(dept, salary) is shown below. Run:\n"
            "SELECT dept FROM Employees GROUP BY dept HAVING AVG(salary) > 50000;\n\n"
            "How many departments appear in the result?"
        ),
        "snippet": (
            "dept  | salary\n"
            "------+-------\n"
            "Eng   | 60000\n"
            "Eng   | 55000\n"
            "Sales | 40000\n"
            "Sales | 45000\n"
            "HR    | 70000"
        ),
        "hint": "Eng average = 57,500. Sales average = 42,500. HR average = 70,000. Which cross the 50,000 line?",
        "answers": ["2", "two"],
        "points": 150,
    },
    {
        "title": "The Recursive Passage",
        "prompt": (
            "def mystery(n):\n"
            "    if n <= 1: return n\n"
            "    return mystery(n-1) + mystery(n-2)\n\n"
            "print(mystery(6))\n\n"
            "What gets printed?"
        ),
        "snippet": "",
        "hint": "This is the Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8 ... mystery(6) is the 7th term.",
        "answers": ["8", "eight"],
        "points": 150,
    },
]

CONFIG = {
    "event_name": "ENGINEERING DAY 2026",
    "game_title": "Tech Treasure Hunt",
    "tagline": "Think. Solve. Decode. Unlock.",
    "hint_penalty": 20,
    "wrong_attempt_penalty": 10,
    "completion_bonus": 100,
}
