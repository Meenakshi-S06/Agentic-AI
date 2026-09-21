from student_agent import (
    create_database,
    get_student_info,
    get_student_marks,
    calculator,
    get_passing_rules
)


# ============================================================
# SETUP
# ============================================================

def setup_module():

    create_database()


# ============================================================
# TEST 1 - STUDENT INFORMATION
# ============================================================

def test_student_info():

    result = get_student_info.invoke({
        "student_id": "22CS045"
    })

    assert "Dhanushya" in result
    assert "Computer Science" in result


# ============================================================
# TEST 2 - STUDENT MARKS
# ============================================================

def test_student_marks():

    result = get_student_marks.invoke({
        "student_id": "22CS045"
    })

    assert "Python: 85" in result
    assert "Database: 72" in result
    assert "AI: 90" in result
    assert "Web: 78" in result


# ============================================================
# TEST 3 - CALCULATOR TOTAL
# ============================================================

def test_calculator_total():

    result = calculator.invoke({
        "expression": "85 + 72 + 90 + 78"
    })

    assert "325" in result


# ============================================================
# TEST 4 - CALCULATOR AVERAGE
# ============================================================

def test_calculator_average():

    result = calculator.invoke({
        "expression": "325 / 4"
    })

    assert "81.25" in result


# ============================================================
# TEST 5 - PASSING RULES
# ============================================================

def test_passing_rules():

    result = get_passing_rules.invoke({})

    assert "40%" in result
    assert "35%" in result


# ============================================================
# TEST 6 - UNKNOWN STUDENT
# ============================================================

def test_unknown_student():

    result = get_student_info.invoke({
        "student_id": "999999"
    })

    assert "No student found" in result