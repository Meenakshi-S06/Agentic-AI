import os
import sqlite3

from langchain.tools import tool
from langchain.agents import create_agent as langchain_create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# 1. CREATE SQLITE DATABASE
# ============================================================

def create_database():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            department TEXT,
            python INTEGER,
            database INTEGER,
            ai INTEGER,
            web INTEGER
        )
    """)

    students = [
        ("22CS045", "Dhanushya", "Computer Science", 85, 72, 90, 78),
        ("22CS046", "Rahul", "Computer Science", 65, 70, 68, 72),
        ("22CS047", "Priya", "Information Technology", 92, 88, 95, 90),
        ("22CS048", "Arun", "Information Technology", 55, 60, 58, 62),
        ("22CS049", "Meena", "Computer Science", 78, 85, 80, 88)
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO students
        (
            student_id,
            name,
            department,
            python,
            database,
            ai,
            web
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, students)

    conn.commit()
    conn.close()

    print("Database created successfully.")


# ============================================================
# 2. TOOL - GET STUDENT INFORMATION
# ============================================================

@tool
def get_student_info(student_id: str) -> str:
    """
    Get the student's name and department using the student ID.
    Use this tool when the user asks for a student's name,
    department, or basic student information.
    """

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, department
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return f"No student found with ID {student_id}"

    name, department = result

    return f"Name: {name}, Department: {department}"


# ============================================================
# 3. TOOL - GET STUDENT MARKS
# ============================================================

@tool
def get_student_marks(student_id: str) -> str:
    """
    Get the student's marks in Python, Database, AI, and Web.
    Use this tool when the user asks for marks, total marks,
    average marks, or pass eligibility.
    """

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT python, database, ai, web
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return f"No student found with ID {student_id}"

    python_mark, database_mark, ai_mark, web_mark = result

    return (
        f"Python: {python_mark}, "
        f"Database: {database_mark}, "
        f"AI: {ai_mark}, "
        f"Web: {web_mark}"
    )


# ============================================================
# 4. TOOL - CALCULATOR
# ============================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.
    Use this tool to calculate total marks, average marks,
    or other numerical calculations.
    """

    try:

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return f"Result: {result}"

    except Exception as e:

        return f"Calculation error: {str(e)}"


# ============================================================
# 5. TOOL - GET PASSING RULES
# ============================================================

@tool
def get_passing_rules() -> str:
    """
    Get the university passing rules.
    The minimum overall average is 40 percent.
    The minimum mark in each subject is 35 percent.
    Use this tool when determining whether a student
    satisfies the university passing requirements.
    """

    return (
        "University Passing Rules: "
        "Minimum overall average = 40%. "
        "Minimum mark in each subject = 35%."
    )


# ============================================================
# 6. ALL TOOLS
# ============================================================

tools = [
    get_student_info,
    get_student_marks,
    calculator,
    get_passing_rules
]


# ============================================================
# 7. CREATE LANGCHAIN AGENT
# ============================================================

agent = None


def initialize_agent():

    global agent

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0
    )

    agent = langchain_create_agent(
        model=llm,
        tools=tools
    )


# ============================================================
# 8. CLEAN FINAL ANSWER
# ============================================================

def clean_answer(answer):

    if isinstance(answer, list):

        text_parts = []

        for item in answer:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text_parts.append(
                        item.get("text", "")
                    )

            elif isinstance(item, str):

                text_parts.append(item)

        answer = " ".join(text_parts)

    answer = str(answer)

    # Remove Markdown bold
    answer = answer.replace("**", "")

    # Remove Markdown italic
    answer = answer.replace("__", "")

    return answer.strip()


# ============================================================
# 9. ASK QUESTION TO AGENT
# ============================================================

def ask_agent(question):

    if agent is None:
        raise RuntimeError(
            "Agent is not initialized. "
            "Run initialize_agent() first."
        )

    print("\n" + "=" * 70)
    print("USER QUESTION")
    print("=" * 70)

    print(question)

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    # --------------------------------------------------------
    # SHOW TOOLS USED
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TOOLS USED")
    print("=" * 70)

    tools_used = False

    for message in result["messages"]:

        if hasattr(message, "tool_calls"):

            if message.tool_calls:

                tools_used = True

                for call in message.tool_calls:

                    print(
                        f"{call['name']} -> {call['args']}"
                    )

    if not tools_used:
        print("No tools used.")

    # --------------------------------------------------------
    # SHOW FINAL ANSWER
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    final_answer = result["messages"][-1].content

    print(clean_answer(final_answer))


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # Ask for API key ONLY when running the actual application.
    # Pytest will import this file without asking for the key.

    if "GOOGLE_API_KEY" not in os.environ:

        os.environ["GOOGLE_API_KEY"] = input(
            "Enter your Gemini API key: "
        )

    create_database()

    initialize_agent()

    print("\nStudent Agent is ready!")

    while True:

        question = input(
            "\nAsk a student-related question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":

            print("Agent stopped.")

            break

        ask_agent(question)