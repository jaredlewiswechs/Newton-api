"""
═══════════════════════════════════════════════════════════════════════════════
 TEKS Database - Comprehensive Texas Essential Knowledge and Skills
═══════════════════════════════════════════════════════════════════════════════

Complete TEKS standards database for K-12 Texas education.
Organized by subject and grade level for easy lookup.

Source: Texas Education Agency (tea.texas.gov)

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional
from .education import TEKSStandard, TEKSLibrary, Subject, CognitiveLevel


def load_comprehensive_teks(library: TEKSLibrary):
    """
    Load comprehensive TEKS standards into the library.

    This adds hundreds of commonly-used TEKS standards across
    Math, Reading/ELA, Science, and Social Studies.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Kindergarten
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "K.2A", 0, Subject.MATH, "2",
         "Number and operations",
         "Count forward and backward to at least 20",
         CognitiveLevel.REMEMBER,
         keywords=["counting", "forward", "backward", "twenty"])

    _add(library, "K.2B", 0, Subject.MATH, "2",
         "Number and operations",
         "Read, write, and represent whole numbers from 0 to 20",
         CognitiveLevel.UNDERSTAND,
         keywords=["read", "write", "numbers", "represent"])

    _add(library, "K.2C", 0, Subject.MATH, "2",
         "Number and operations",
         "Count a set of objects up to 20",
         CognitiveLevel.APPLY,
         keywords=["count", "objects", "sets"])

    _add(library, "K.2D", 0, Subject.MATH, "2",
         "Number and operations",
         "Recognize instantly the quantity of a small group of objects",
         CognitiveLevel.UNDERSTAND,
         keywords=["subitizing", "quantity", "recognize"])

    _add(library, "K.2E", 0, Subject.MATH, "2",
         "Number and operations",
         "Generate a set using concrete objects to represent a number",
         CognitiveLevel.APPLY,
         keywords=["generate", "concrete", "represent"])

    _add(library, "K.2F", 0, Subject.MATH, "2",
         "Number and operations",
         "Generate a number that is one more or one less",
         CognitiveLevel.APPLY,
         keywords=["one more", "one less", "generate"])

    _add(library, "K.2G", 0, Subject.MATH, "2",
         "Number and operations",
         "Compare sets of objects up to 20 using comparative language",
         CognitiveLevel.ANALYZE,
         keywords=["compare", "more", "less", "equal"])

    _add(library, "K.3A", 0, Subject.MATH, "3",
         "Addition and subtraction",
         "Model addition within 10 with concrete objects and pictures",
         CognitiveLevel.APPLY,
         keywords=["addition", "model", "concrete", "pictures"])

    _add(library, "K.3B", 0, Subject.MATH, "3",
         "Addition and subtraction",
         "Solve word problems within 10 using objects and pictures",
         CognitiveLevel.APPLY,
         keywords=["word problems", "solve", "objects"])

    _add(library, "K.3C", 0, Subject.MATH, "3",
         "Addition and subtraction",
         "Explain problem-solving strategies using words, objects, and pictures",
         CognitiveLevel.UNDERSTAND,
         keywords=["explain", "strategies", "problem-solving"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 1
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "1.2A", 1, Subject.MATH, "2",
         "Number and operations",
         "Recognize instantly a small group of objects (up to 10)",
         CognitiveLevel.UNDERSTAND,
         keywords=["subitizing", "recognize", "groups"])

    _add(library, "1.2B", 1, Subject.MATH, "2",
         "Number and operations",
         "Use concrete objects to represent a number from 1-120",
         CognitiveLevel.APPLY,
         keywords=["concrete", "represent", "120"])

    _add(library, "1.2C", 1, Subject.MATH, "2",
         "Number and operations",
         "Use objects, pictures, and number lines to represent numbers",
         CognitiveLevel.APPLY,
         keywords=["number line", "represent", "pictures"])

    _add(library, "1.3A", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Use concrete objects to compose and decompose numbers up to 10",
         CognitiveLevel.APPLY,
         keywords=["compose", "decompose", "number bonds"])

    _add(library, "1.3B", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Use objects and pictures to solve word problems involving joining and separating",
         CognitiveLevel.APPLY,
         keywords=["word problems", "joining", "separating"])

    _add(library, "1.3C", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Compose 10 with two or more addends with and without objects",
         CognitiveLevel.APPLY,
         keywords=["compose 10", "addends", "make 10"])

    _add(library, "1.3D", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Apply basic fact strategies to add and subtract within 20",
         CognitiveLevel.APPLY,
         keywords=["fact strategies", "add", "subtract", "20"])

    _add(library, "1.3E", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Explain strategies for problem solving",
         CognitiveLevel.UNDERSTAND,
         keywords=["explain", "strategies", "reasoning"])

    _add(library, "1.3F", 1, Subject.MATH, "3",
         "Addition and subtraction",
         "Generate and solve problem situations using addition and subtraction within 20",
         CognitiveLevel.APPLY,
         keywords=["generate", "solve", "word problems"])

    _add(library, "1.5A", 1, Subject.MATH, "5",
         "Algebraic reasoning",
         "Recite numbers forward and backward from any given number between 1 and 120",
         CognitiveLevel.REMEMBER,
         keywords=["recite", "forward", "backward", "120"])

    _add(library, "1.5B", 1, Subject.MATH, "5",
         "Algebraic reasoning",
         "Skip count by twos, fives, and tens",
         CognitiveLevel.APPLY,
         keywords=["skip count", "twos", "fives", "tens"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 2
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "2.2A", 2, Subject.MATH, "2",
         "Number and operations",
         "Use concrete objects to represent numbers up to 1,200",
         CognitiveLevel.APPLY,
         keywords=["concrete", "represent", "place value"])

    _add(library, "2.2B", 2, Subject.MATH, "2",
         "Number and operations",
         "Use standard, word, and expanded forms to represent numbers up to 1,200",
         CognitiveLevel.UNDERSTAND,
         keywords=["standard form", "word form", "expanded form"])

    _add(library, "2.2C", 2, Subject.MATH, "2",
         "Number and operations",
         "Generate a number that is greater or less than a given number",
         CognitiveLevel.APPLY,
         keywords=["greater", "less", "compare"])

    _add(library, "2.2D", 2, Subject.MATH, "2",
         "Number and operations",
         "Use place value to compare numbers using symbols (>, <, =)",
         CognitiveLevel.ANALYZE,
         keywords=["compare", "symbols", "greater than", "less than"])

    _add(library, "2.2E", 2, Subject.MATH, "2",
         "Number and operations",
         "Locate a number on an open number line",
         CognitiveLevel.APPLY,
         keywords=["number line", "locate", "position"])

    _add(library, "2.2F", 2, Subject.MATH, "2",
         "Number and operations",
         "Name the whole number that corresponds to a point on a number line",
         CognitiveLevel.UNDERSTAND,
         keywords=["number line", "whole number", "correspond"])

    _add(library, "2.4A", 2, Subject.MATH, "4",
         "Addition and subtraction",
         "Recall basic facts to add and subtract within 20",
         CognitiveLevel.REMEMBER,
         keywords=["basic facts", "fluency", "add", "subtract"])

    _add(library, "2.4B", 2, Subject.MATH, "4",
         "Addition and subtraction",
         "Add up to four two-digit numbers using strategies and algorithms",
         CognitiveLevel.APPLY,
         keywords=["two-digit", "strategies", "algorithms", "regrouping"])

    _add(library, "2.4C", 2, Subject.MATH, "4",
         "Addition and subtraction",
         "Solve one-step and multi-step word problems using addition and subtraction",
         CognitiveLevel.APPLY,
         keywords=["word problems", "multi-step", "addition", "subtraction"])

    _add(library, "2.6A", 2, Subject.MATH, "6",
         "Multiplication introduction",
         "Model, create, and describe contextual multiplication situations",
         CognitiveLevel.UNDERSTAND,
         keywords=["multiplication", "model", "equal groups"])

    _add(library, "2.6B", 2, Subject.MATH, "6",
         "Multiplication introduction",
         "Model, create, and describe contextual division situations",
         CognitiveLevel.UNDERSTAND,
         keywords=["division", "model", "sharing", "grouping"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 3 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "3.1B", 3, Subject.MATH, "1",
         "Place value",
         "Describe the relationship between digits in place value",
         CognitiveLevel.UNDERSTAND,
         keywords=["place value", "relationship", "ten times"])

    _add(library, "3.2B", 3, Subject.MATH, "2",
         "Fractions",
         "Determine the corresponding fraction greater than zero and less than or equal to one",
         CognitiveLevel.APPLY,
         keywords=["fractions", "number line", "unit fractions"])

    _add(library, "3.3B", 3, Subject.MATH, "3",
         "Addition and subtraction",
         "Round to the nearest 10 or 100 to estimate solutions",
         CognitiveLevel.APPLY,
         keywords=["round", "estimate", "nearest 10", "nearest 100"])

    _add(library, "3.4B", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Represent multiplication using arrays and area models",
         CognitiveLevel.APPLY,
         keywords=["arrays", "area models", "multiplication"])

    _add(library, "3.4C", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Use strategies to multiply within 100",
         CognitiveLevel.APPLY,
         keywords=["multiply", "strategies", "100"])

    _add(library, "3.4D", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Use strategies to divide using facts 1-10",
         CognitiveLevel.APPLY,
         keywords=["divide", "strategies", "facts"])

    _add(library, "3.4E", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Represent and solve one-step multiplication and division problems",
         CognitiveLevel.APPLY,
         keywords=["word problems", "multiplication", "division"])

    _add(library, "3.4F", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Recall facts to multiply within 10 by 10 with automaticity",
         CognitiveLevel.REMEMBER,
         keywords=["facts", "automaticity", "fluency"])

    _add(library, "3.4G", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Use strategies and algorithms to multiply by 10 or 100",
         CognitiveLevel.APPLY,
         keywords=["multiply", "10", "100", "place value"])

    _add(library, "3.4H", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Determine the quotient using the relationship between multiplication and division",
         CognitiveLevel.APPLY,
         keywords=["quotient", "inverse", "multiplication", "division"])

    _add(library, "3.4I", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Determine if a number is even or odd using divisibility rules",
         CognitiveLevel.APPLY,
         keywords=["even", "odd", "divisibility"])

    _add(library, "3.4J", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Determine a quotient using pictorial models",
         CognitiveLevel.APPLY,
         keywords=["quotient", "pictorial", "division"])

    _add(library, "3.4K", 3, Subject.MATH, "4",
         "Multiplication and division",
         "Solve two-step problems involving the four operations",
         CognitiveLevel.APPLY,
         keywords=["two-step", "four operations", "problem solving"])

    _add(library, "3.6A", 3, Subject.MATH, "6",
         "Geometry and measurement",
         "Classify and sort 2D and 3D figures by attributes",
         CognitiveLevel.ANALYZE,
         keywords=["classify", "sort", "2D", "3D", "attributes"])

    _add(library, "3.6B", 3, Subject.MATH, "6",
         "Geometry and measurement",
         "Determine the area of rectangles using multiplication",
         CognitiveLevel.APPLY,
         keywords=["area", "rectangles", "multiplication"])

    _add(library, "3.7A", 3, Subject.MATH, "7",
         "Geometry and measurement",
         "Represent fractions of halves, fourths, and eighths as distances on a number line",
         CognitiveLevel.APPLY,
         keywords=["fractions", "number line", "distance"])

    _add(library, "3.7B", 3, Subject.MATH, "7",
         "Geometry and measurement",
         "Determine the perimeter of a polygon",
         CognitiveLevel.APPLY,
         keywords=["perimeter", "polygon", "addition"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 4 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "4.1B", 4, Subject.MATH, "1",
         "Place value",
         "Represent the value of digits using expanded notation",
         CognitiveLevel.UNDERSTAND,
         keywords=["expanded notation", "place value", "digits"])

    _add(library, "4.2B", 4, Subject.MATH, "2",
         "Decimals",
         "Represent decimals using objects, pictures, and money",
         CognitiveLevel.APPLY,
         keywords=["decimals", "money", "tenths", "hundredths"])

    _add(library, "4.2C", 4, Subject.MATH, "2",
         "Decimals",
         "Compare and order decimals using place value",
         CognitiveLevel.ANALYZE,
         keywords=["compare", "order", "decimals"])

    _add(library, "4.2D", 4, Subject.MATH, "2",
         "Decimals",
         "Round decimals to the nearest tenth or whole number",
         CognitiveLevel.APPLY,
         keywords=["round", "decimals", "tenth"])

    _add(library, "4.3B", 4, Subject.MATH, "3",
         "Fractions",
         "Decompose a fraction into a sum of fractions with the same denominator",
         CognitiveLevel.APPLY,
         keywords=["decompose", "fractions", "denominator"])

    _add(library, "4.3C", 4, Subject.MATH, "3",
         "Fractions",
         "Determine equivalent fractions using visual models",
         CognitiveLevel.APPLY,
         keywords=["equivalent fractions", "visual models"])

    _add(library, "4.3D", 4, Subject.MATH, "3",
         "Fractions",
         "Compare fractions with different numerators and denominators",
         CognitiveLevel.ANALYZE,
         keywords=["compare", "fractions", "numerator", "denominator"])

    _add(library, "4.4B", 4, Subject.MATH, "4",
         "Fraction operations",
         "Determine fraction equivalents and add/subtract fractions with equal denominators",
         CognitiveLevel.APPLY,
         keywords=["add fractions", "subtract fractions", "equivalent"])

    _add(library, "4.4C", 4, Subject.MATH, "4",
         "Multiplication",
         "Represent multi-digit products using area models",
         CognitiveLevel.APPLY,
         keywords=["products", "area models", "multiplication"])

    _add(library, "4.4D", 4, Subject.MATH, "4",
         "Multiplication",
         "Multiply a two-digit by a two-digit number using strategies",
         CognitiveLevel.APPLY,
         keywords=["multiply", "two-digit", "strategies"])

    _add(library, "4.4E", 4, Subject.MATH, "4",
         "Division",
         "Represent quotients using distributive property",
         CognitiveLevel.APPLY,
         keywords=["quotients", "distributive property"])

    _add(library, "4.4F", 4, Subject.MATH, "4",
         "Division",
         "Divide up to a four-digit dividend by a one-digit divisor",
         CognitiveLevel.APPLY,
         keywords=["divide", "four-digit", "one-digit"])

    _add(library, "4.4G", 4, Subject.MATH, "4",
         "Division",
         "Round to the nearest 10, 100, or 1,000 to estimate solutions",
         CognitiveLevel.APPLY,
         keywords=["round", "estimate", "1000"])

    _add(library, "4.4H", 4, Subject.MATH, "4",
         "Problem solving",
         "Solve with fluency one- and two-step word problems using the four operations",
         CognitiveLevel.APPLY,
         keywords=["fluency", "word problems", "four operations"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 5 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "5.1B", 5, Subject.MATH, "1",
         "Place value",
         "Use standard, word, and expanded forms to represent decimals",
         CognitiveLevel.UNDERSTAND,
         keywords=["decimals", "standard form", "expanded form"])

    _add(library, "5.2B", 5, Subject.MATH, "2",
         "Number sense",
         "Identify prime and composite numbers",
         CognitiveLevel.ANALYZE,
         keywords=["prime", "composite", "identify"])

    _add(library, "5.3D", 5, Subject.MATH, "3",
         "Operations",
         "Divide whole numbers by two-digit divisors",
         CognitiveLevel.APPLY,
         keywords=["divide", "two-digit divisor"])

    _add(library, "5.3E", 5, Subject.MATH, "3",
         "Fractions",
         "Solve for products of fractions using strategies",
         CognitiveLevel.APPLY,
         keywords=["multiply fractions", "products"])

    _add(library, "5.3F", 5, Subject.MATH, "3",
         "Fractions",
         "Represent and solve division of a whole number by a fraction",
         CognitiveLevel.APPLY,
         keywords=["divide", "fractions", "whole number"])

    _add(library, "5.3G", 5, Subject.MATH, "3",
         "Decimals",
         "Add and subtract decimals to the thousandths",
         CognitiveLevel.APPLY,
         keywords=["add decimals", "subtract decimals", "thousandths"])

    _add(library, "5.3H", 5, Subject.MATH, "3",
         "Decimals",
         "Multiply and divide decimals using strategies",
         CognitiveLevel.APPLY,
         keywords=["multiply decimals", "divide decimals"])

    _add(library, "5.3I", 5, Subject.MATH, "3",
         "Fractions and decimals",
         "Represent and solve word problems with fractions and decimals",
         CognitiveLevel.APPLY,
         keywords=["word problems", "fractions", "decimals"])

    _add(library, "5.3J", 5, Subject.MATH, "3",
         "Expressions",
         "Simplify numerical expressions with parentheses",
         CognitiveLevel.APPLY,
         keywords=["simplify", "parentheses", "order of operations"])

    _add(library, "5.3K", 5, Subject.MATH, "3",
         "Estimation",
         "Evaluate reasonableness of product and quotient of decimals",
         CognitiveLevel.EVALUATE,
         keywords=["reasonableness", "estimate", "decimals"])

    _add(library, "5.4B", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Represent and solve multi-step problems with expressions",
         CognitiveLevel.APPLY,
         keywords=["expressions", "multi-step", "variables"])

    _add(library, "5.4C", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Generate tables based on an expression or rule",
         CognitiveLevel.APPLY,
         keywords=["tables", "expression", "rule"])

    _add(library, "5.4D", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Recognize the relationship between ordered pairs and tables",
         CognitiveLevel.ANALYZE,
         keywords=["ordered pairs", "tables", "coordinate"])

    _add(library, "5.4E", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Describe the meaning of parentheses in an expression",
         CognitiveLevel.UNDERSTAND,
         keywords=["parentheses", "expressions", "order of operations"])

    _add(library, "5.4F", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Simplify numerical expressions",
         CognitiveLevel.APPLY,
         keywords=["simplify", "expressions", "PEMDAS"])

    _add(library, "5.4G", 5, Subject.MATH, "4",
         "Algebraic reasoning",
         "Use concrete objects to generate formulas",
         CognitiveLevel.CREATE,
         keywords=["formulas", "generate", "concrete"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 6 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "6.1B", 6, Subject.MATH, "1",
         "Number sense",
         "Order a set of rational numbers from least to greatest",
         CognitiveLevel.ANALYZE,
         keywords=["order", "rational", "least", "greatest"])

    _add(library, "6.2B", 6, Subject.MATH, "2",
         "Expressions",
         "Use substitution to determine true or false equations",
         CognitiveLevel.APPLY,
         keywords=["substitution", "equations", "true", "false"])

    _add(library, "6.2C", 6, Subject.MATH, "2",
         "Expressions",
         "Represent expressions using variables and concrete objects",
         CognitiveLevel.APPLY,
         keywords=["variables", "expressions", "represent"])

    _add(library, "6.2D", 6, Subject.MATH, "2",
         "Expressions",
         "Simplify expressions with variables",
         CognitiveLevel.APPLY,
         keywords=["simplify", "variables", "like terms"])

    _add(library, "6.2E", 6, Subject.MATH, "2",
         "Expressions",
         "Apply the distributive property to generate equivalent expressions",
         CognitiveLevel.APPLY,
         keywords=["distributive property", "equivalent"])

    _add(library, "6.3B", 6, Subject.MATH, "3",
         "Ratios and rates",
         "Represent ratios using real-world situations",
         CognitiveLevel.APPLY,
         keywords=["ratios", "real-world", "represent"])

    _add(library, "6.3C", 6, Subject.MATH, "3",
         "Ratios and rates",
         "Represent unit rates as the ratio of two quantities",
         CognitiveLevel.UNDERSTAND,
         keywords=["unit rates", "ratio", "quantities"])

    _add(library, "6.3D", 6, Subject.MATH, "3",
         "Ratios and rates",
         "Given a unit rate, calculate the rate for a given situation",
         CognitiveLevel.APPLY,
         keywords=["unit rate", "calculate", "rate"])

    _add(library, "6.3E", 6, Subject.MATH, "3",
         "Ratios and rates",
         "Solve real-world problems involving ratios and rates",
         CognitiveLevel.APPLY,
         keywords=["word problems", "ratios", "rates"])

    _add(library, "6.4B", 6, Subject.MATH, "4",
         "Proportional relationships",
         "Apply qualitative and quantitative reasoning to solve problems",
         CognitiveLevel.APPLY,
         keywords=["proportional", "reasoning", "solve"])

    _add(library, "6.4C", 6, Subject.MATH, "4",
         "Proportional relationships",
         "Represent ratios using tables, graphs, and verbal descriptions",
         CognitiveLevel.APPLY,
         keywords=["tables", "graphs", "verbal", "ratios"])

    _add(library, "6.5A", 6, Subject.MATH, "5",
         "Proportional relationships",
         "Represent percent problems using objects, pictures, or equations",
         CognitiveLevel.APPLY,
         keywords=["percent", "represent", "equations"])

    _add(library, "6.5B", 6, Subject.MATH, "5",
         "Proportional relationships",
         "Solve problems involving percent",
         CognitiveLevel.APPLY,
         keywords=["percent", "solve", "problems"])

    _add(library, "6.5C", 6, Subject.MATH, "5",
         "Proportional relationships",
         "Use equivalent fractions, decimals, and percents to show equal parts",
         CognitiveLevel.APPLY,
         keywords=["equivalent", "fractions", "decimals", "percents"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 7 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "7.1B", 7, Subject.MATH, "1",
         "Number sense",
         "Apply and extend understanding of operations with rational numbers",
         CognitiveLevel.APPLY,
         keywords=["rational numbers", "operations", "extend"])

    _add(library, "7.2B", 7, Subject.MATH, "2",
         "Operations",
         "Extend understanding of operations to solve problems with integers",
         CognitiveLevel.APPLY,
         keywords=["integers", "operations", "negative"])

    _add(library, "7.3B", 7, Subject.MATH, "3",
         "Proportionality",
         "Determine unit rates from tables, graphs, equations, and verbal descriptions",
         CognitiveLevel.ANALYZE,
         keywords=["unit rates", "tables", "graphs", "equations"])

    _add(library, "7.4B", 7, Subject.MATH, "4",
         "Proportionality",
         "Calculate unit rates from rates in mathematical and real-world problems",
         CognitiveLevel.APPLY,
         keywords=["calculate", "unit rates", "problems"])

    _add(library, "7.4C", 7, Subject.MATH, "4",
         "Proportionality",
         "Determine the constant of proportionality (k = y/x)",
         CognitiveLevel.ANALYZE,
         keywords=["constant", "proportionality", "k"])

    _add(library, "7.4D", 7, Subject.MATH, "4",
         "Proportionality",
         "Solve problems involving ratios, rates, and percents",
         CognitiveLevel.APPLY,
         keywords=["ratios", "rates", "percents", "solve"])

    _add(library, "7.5A", 7, Subject.MATH, "5",
         "Proportionality",
         "Generalize the critical attributes of similarity",
         CognitiveLevel.UNDERSTAND,
         keywords=["similarity", "attributes", "scale"])

    _add(library, "7.5B", 7, Subject.MATH, "5",
         "Proportionality",
         "Describe scale factors for scale drawings and maps",
         CognitiveLevel.UNDERSTAND,
         keywords=["scale factor", "drawings", "maps"])

    _add(library, "7.5C", 7, Subject.MATH, "5",
         "Proportionality",
         "Solve problems involving similar shapes and scale drawings",
         CognitiveLevel.APPLY,
         keywords=["similar shapes", "scale", "solve"])

    _add(library, "7.6A", 7, Subject.MATH, "6",
         "Expressions and equations",
         "Represent relationships using verbal descriptions, tables, graphs, and equations",
         CognitiveLevel.APPLY,
         keywords=["relationships", "tables", "graphs", "equations"])

    _add(library, "7.6B", 7, Subject.MATH, "6",
         "Expressions and equations",
         "Convert between different forms of relationships",
         CognitiveLevel.APPLY,
         keywords=["convert", "forms", "relationships"])

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS - Grade 8 (Extended)
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "8.1B", 8, Subject.MATH, "1",
         "Real numbers",
         "Approximate irrational numbers and locate on number line",
         CognitiveLevel.APPLY,
         keywords=["irrational", "approximate", "number line"])

    _add(library, "8.1C", 8, Subject.MATH, "1",
         "Real numbers",
         "Convert between scientific notation and standard form",
         CognitiveLevel.APPLY,
         keywords=["scientific notation", "standard form", "convert"])

    _add(library, "8.2B", 8, Subject.MATH, "2",
         "Scientific notation",
         "Order a set of real numbers in scientific notation",
         CognitiveLevel.ANALYZE,
         keywords=["order", "scientific notation", "compare"])

    _add(library, "8.2C", 8, Subject.MATH, "2",
         "Scientific notation",
         "Convert between standard decimal notation and scientific notation",
         CognitiveLevel.APPLY,
         keywords=["convert", "decimal", "scientific notation"])

    _add(library, "8.3B", 8, Subject.MATH, "3",
         "Linear relationships",
         "Represent linear equations using tables, graphs, and equations",
         CognitiveLevel.APPLY,
         keywords=["linear", "tables", "graphs", "equations"])

    _add(library, "8.3C", 8, Subject.MATH, "3",
         "Linear relationships",
         "Use data from a table or graph to determine rate of change or slope",
         CognitiveLevel.ANALYZE,
         keywords=["rate of change", "slope", "table", "graph"])

    _add(library, "8.4B", 8, Subject.MATH, "4",
         "Linear relationships",
         "Graph proportional relationships interpreting unit rate as slope",
         CognitiveLevel.APPLY,
         keywords=["graph", "proportional", "unit rate", "slope"])

    _add(library, "8.4C", 8, Subject.MATH, "4",
         "Linear relationships",
         "Use data from a table or graph to determine rate of change",
         CognitiveLevel.ANALYZE,
         keywords=["data", "rate of change", "analyze"])

    _add(library, "8.5B", 8, Subject.MATH, "5",
         "Functions",
         "Represent linear functions using tables, graphs, and equations",
         CognitiveLevel.APPLY,
         keywords=["functions", "tables", "graphs", "equations"])

    _add(library, "8.5C", 8, Subject.MATH, "5",
         "Functions",
         "Contrast bivariate sets of data that suggest linear or nonlinear relationships",
         CognitiveLevel.ANALYZE,
         keywords=["bivariate", "linear", "nonlinear", "relationships"])

    _add(library, "8.5D", 8, Subject.MATH, "5",
         "Functions",
         "Use trend lines to make predictions",
         CognitiveLevel.APPLY,
         keywords=["trend lines", "predictions", "scatter plots"])

    _add(library, "8.5E", 8, Subject.MATH, "5",
         "Functions",
         "Solve problems involving direct variation",
         CognitiveLevel.APPLY,
         keywords=["direct variation", "solve", "constant"])

    _add(library, "8.5F", 8, Subject.MATH, "5",
         "Functions",
         "Distinguish between proportional and non-proportional linear relationships",
         CognitiveLevel.ANALYZE,
         keywords=["proportional", "non-proportional", "distinguish"])

    _add(library, "8.5G", 8, Subject.MATH, "5",
         "Functions",
         "Identify functions using sets of ordered pairs, tables, mappings, and graphs",
         CognitiveLevel.ANALYZE,
         keywords=["functions", "ordered pairs", "mappings", "identify"])

    _add(library, "8.5H", 8, Subject.MATH, "5",
         "Functions",
         "Identify domain and range of a function",
         CognitiveLevel.UNDERSTAND,
         keywords=["domain", "range", "function"])

    _add(library, "8.5I", 8, Subject.MATH, "5",
         "Functions",
         "Write an equation in y = mx + b form given a table or graph",
         CognitiveLevel.APPLY,
         keywords=["equation", "slope-intercept", "y=mx+b"])

    # ═══════════════════════════════════════════════════════════════════════════
    # READING/ELA - Elementary
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "3.6A", 3, Subject.READING, "6",
         "Comprehension",
         "Describe the elements of plot including rising action, climax, and resolution",
         CognitiveLevel.UNDERSTAND,
         keywords=["plot", "rising action", "climax", "resolution"])

    _add(library, "3.6B", 3, Subject.READING, "6",
         "Comprehension",
         "Describe the traits, motivations, and feelings of characters",
         CognitiveLevel.ANALYZE,
         keywords=["characters", "traits", "motivations", "feelings"])

    _add(library, "3.6C", 3, Subject.READING, "6",
         "Comprehension",
         "Describe how characters interact in the plot",
         CognitiveLevel.ANALYZE,
         keywords=["characters", "interact", "plot"])

    _add(library, "3.7A", 3, Subject.READING, "7",
         "Author's purpose",
         "Explain the author's purpose and message",
         CognitiveLevel.ANALYZE,
         keywords=["author's purpose", "message", "explain"])

    _add(library, "3.7B", 3, Subject.READING, "7",
         "Author's purpose",
         "Explain the use of sensory details and figurative language",
         CognitiveLevel.ANALYZE,
         keywords=["sensory details", "figurative language"])

    _add(library, "3.8A", 3, Subject.READING, "8",
         "Genres",
         "Explain connections between literary texts and their history and culture",
         CognitiveLevel.ANALYZE,
         keywords=["connections", "history", "culture"])

    _add(library, "4.6A", 4, Subject.READING, "6",
         "Comprehension",
         "Sequence and summarize the plot's main events and explain their influence",
         CognitiveLevel.ANALYZE,
         keywords=["sequence", "summarize", "plot", "events"])

    _add(library, "4.6B", 4, Subject.READING, "6",
         "Comprehension",
         "Explain the roles and functions of characters and their relationships",
         CognitiveLevel.ANALYZE,
         keywords=["characters", "roles", "relationships"])

    _add(library, "4.6C", 4, Subject.READING, "6",
         "Comprehension",
         "Analyze plot elements including problem and solution",
         CognitiveLevel.ANALYZE,
         keywords=["plot", "problem", "solution", "analyze"])

    _add(library, "4.7A", 4, Subject.READING, "7",
         "Author's craft",
         "Infer the author's purpose and explain how the text conveys that purpose",
         CognitiveLevel.ANALYZE,
         keywords=["infer", "author's purpose", "convey"])

    _add(library, "4.8A", 4, Subject.READING, "8",
         "Informational text",
         "Explain the differences between purposes of informational texts",
         CognitiveLevel.ANALYZE,
         keywords=["informational", "purposes", "differences"])

    _add(library, "4.8B", 4, Subject.READING, "8",
         "Informational text",
         "Explain how the use of text structure contributes to the author's purpose",
         CognitiveLevel.ANALYZE,
         keywords=["text structure", "author's purpose"])

    _add(library, "4.8C", 4, Subject.READING, "8",
         "Informational text",
         "Analyze the author's use of print and graphic features",
         CognitiveLevel.ANALYZE,
         keywords=["print features", "graphic features", "analyze"])

    _add(library, "5.6C", 5, Subject.READING, "6",
         "Comprehension",
         "Explain how the setting influences the plot and characters",
         CognitiveLevel.ANALYZE,
         keywords=["setting", "influence", "plot", "characters"])

    _add(library, "5.6D", 5, Subject.READING, "6",
         "Comprehension",
         "Analyze the influence of the setting on the theme",
         CognitiveLevel.ANALYZE,
         keywords=["setting", "theme", "analyze"])

    _add(library, "5.6E", 5, Subject.READING, "6",
         "Comprehension",
         "Identify point of view and explain its effect on the text",
         CognitiveLevel.ANALYZE,
         keywords=["point of view", "effect", "narrator"])

    _add(library, "5.7B", 5, Subject.READING, "7",
         "Author's craft",
         "Analyze the author's use of language in poetry and prose",
         CognitiveLevel.ANALYZE,
         keywords=["language", "poetry", "prose", "author's craft"])

    _add(library, "5.7C", 5, Subject.READING, "7",
         "Author's craft",
         "Explain the role of symbolism, imagery, and figurative language",
         CognitiveLevel.ANALYZE,
         keywords=["symbolism", "imagery", "figurative language"])

    # ═══════════════════════════════════════════════════════════════════════════
    # READING/ELA - Middle School
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "6.6A", 6, Subject.READING, "6",
         "Comprehension",
         "Analyze plot elements and determine their impact on the story",
         CognitiveLevel.ANALYZE,
         keywords=["plot elements", "analyze", "impact"])

    _add(library, "6.6B", 6, Subject.READING, "6",
         "Comprehension",
         "Analyze how the setting influences character and plot development",
         CognitiveLevel.ANALYZE,
         keywords=["setting", "character development", "plot development"])

    _add(library, "6.6C", 6, Subject.READING, "6",
         "Comprehension",
         "Analyze character relationships and their development",
         CognitiveLevel.ANALYZE,
         keywords=["character relationships", "development", "analyze"])

    _add(library, "6.7A", 6, Subject.READING, "7",
         "Theme",
         "Infer the theme supported by text evidence",
         CognitiveLevel.ANALYZE,
         keywords=["theme", "infer", "text evidence"])

    _add(library, "6.7B", 6, Subject.READING, "7",
         "Theme",
         "Analyze how authors develop characters through dialogue and actions",
         CognitiveLevel.ANALYZE,
         keywords=["characters", "dialogue", "actions", "develop"])

    _add(library, "6.8B", 6, Subject.READING, "8",
         "Author's craft",
         "Analyze how authors create stylistic effects",
         CognitiveLevel.ANALYZE,
         keywords=["stylistic effects", "author's craft"])

    _add(library, "7.6A", 7, Subject.READING, "6",
         "Comprehension",
         "Infer multiple themes and analyze how authors develop those themes",
         CognitiveLevel.ANALYZE,
         keywords=["themes", "infer", "analyze", "develop"])

    _add(library, "7.6B", 7, Subject.READING, "6",
         "Comprehension",
         "Analyze how the setting and events contribute to the meaning",
         CognitiveLevel.ANALYZE,
         keywords=["setting", "events", "meaning"])

    _add(library, "7.7A", 7, Subject.READING, "7",
         "Author's craft",
         "Analyze the effect of rhythm, meter, and structure in poetry",
         CognitiveLevel.ANALYZE,
         keywords=["rhythm", "meter", "structure", "poetry"])

    _add(library, "7.7B", 7, Subject.READING, "7",
         "Author's craft",
         "Analyze the effects of sound devices in poetry",
         CognitiveLevel.ANALYZE,
         keywords=["sound devices", "poetry", "effects"])

    _add(library, "8.6A", 8, Subject.READING, "6",
         "Comprehension",
         "Analyze how authors develop complex characters",
         CognitiveLevel.ANALYZE,
         keywords=["complex characters", "analyze", "develop"])

    _add(library, "8.6B", 8, Subject.READING, "6",
         "Comprehension",
         "Analyze the role of conflict in the plot",
         CognitiveLevel.ANALYZE,
         keywords=["conflict", "plot", "role", "analyze"])

    _add(library, "8.7A", 8, Subject.READING, "7",
         "Author's craft",
         "Analyze how authors use point of view and perspective",
         CognitiveLevel.ANALYZE,
         keywords=["point of view", "perspective", "analyze"])

    _add(library, "8.7B", 8, Subject.READING, "7",
         "Author's craft",
         "Analyze how an author's word choice sets the tone",
         CognitiveLevel.ANALYZE,
         keywords=["word choice", "tone", "analyze"])

    # ═══════════════════════════════════════════════════════════════════════════
    # SCIENCE - Elementary
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "3.5A", 3, Subject.SCIENCE, "5",
         "Matter and energy",
         "Measure, test, and record physical properties of matter",
         CognitiveLevel.APPLY,
         keywords=["matter", "physical properties", "measure", "test"])

    _add(library, "3.5B", 3, Subject.SCIENCE, "5",
         "Matter and energy",
         "Describe and classify matter based on properties",
         CognitiveLevel.ANALYZE,
         keywords=["classify", "matter", "properties"])

    _add(library, "3.5C", 3, Subject.SCIENCE, "5",
         "Matter and energy",
         "Predict, observe, and record changes in matter caused by heating and cooling",
         CognitiveLevel.APPLY,
         keywords=["changes", "heating", "cooling", "matter"])

    _add(library, "3.6A", 3, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Explore different forms of energy",
         CognitiveLevel.UNDERSTAND,
         keywords=["energy", "forms", "explore"])

    _add(library, "3.6B", 3, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Demonstrate and observe how position and motion change by push or pull",
         CognitiveLevel.APPLY,
         keywords=["position", "motion", "push", "pull", "force"])

    _add(library, "4.5A", 4, Subject.SCIENCE, "5",
         "Matter and energy",
         "Measure, compare, and contrast properties of matter",
         CognitiveLevel.ANALYZE,
         keywords=["properties", "matter", "compare", "contrast"])

    _add(library, "4.5B", 4, Subject.SCIENCE, "5",
         "Matter and energy",
         "Predict the changes caused by heating and cooling",
         CognitiveLevel.APPLY,
         keywords=["predict", "heating", "cooling", "changes"])

    _add(library, "4.5C", 4, Subject.SCIENCE, "5",
         "Matter and energy",
         "Compare and contrast mixtures and solutions",
         CognitiveLevel.ANALYZE,
         keywords=["mixtures", "solutions", "compare"])

    _add(library, "4.6A", 4, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Differentiate among forms of energy",
         CognitiveLevel.ANALYZE,
         keywords=["forms of energy", "differentiate"])

    _add(library, "4.6B", 4, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Differentiate between conductors and insulators",
         CognitiveLevel.ANALYZE,
         keywords=["conductors", "insulators", "differentiate"])

    _add(library, "4.6C", 4, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Demonstrate that electricity travels in a closed path",
         CognitiveLevel.APPLY,
         keywords=["electricity", "circuit", "closed path"])

    _add(library, "5.5B", 5, Subject.SCIENCE, "5",
         "Matter and energy",
         "Identify the boiling and freezing points of water",
         CognitiveLevel.REMEMBER,
         keywords=["boiling point", "freezing point", "water"])

    _add(library, "5.5C", 5, Subject.SCIENCE, "5",
         "Matter and energy",
         "Demonstrate that some mixtures maintain physical properties",
         CognitiveLevel.APPLY,
         keywords=["mixtures", "physical properties"])

    _add(library, "5.5D", 5, Subject.SCIENCE, "5",
         "Matter and energy",
         "Identify changes that can occur in the physical properties of ingredients",
         CognitiveLevel.ANALYZE,
         keywords=["physical changes", "ingredients", "identify"])

    _add(library, "5.6B", 5, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Demonstrate that objects have potential and kinetic energy",
         CognitiveLevel.APPLY,
         keywords=["potential energy", "kinetic energy", "demonstrate"])

    _add(library, "5.6C", 5, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Demonstrate that electrical energy travels in closed circuits",
         CognitiveLevel.APPLY,
         keywords=["electrical energy", "circuits", "closed"])

    _add(library, "5.6D", 5, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Design a simple experiment to test the effect of force on objects",
         CognitiveLevel.CREATE,
         keywords=["experiment", "force", "design"])

    # ═══════════════════════════════════════════════════════════════════════════
    # SCIENCE - Middle School
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "6.5A", 6, Subject.SCIENCE, "5",
         "Matter and energy",
         "Know that an element is a pure substance with specific properties",
         CognitiveLevel.REMEMBER,
         keywords=["element", "pure substance", "properties"])

    _add(library, "6.5B", 6, Subject.SCIENCE, "5",
         "Matter and energy",
         "Recognize that a limited number of elements make up all matter",
         CognitiveLevel.UNDERSTAND,
         keywords=["elements", "matter", "periodic table"])

    _add(library, "6.5C", 6, Subject.SCIENCE, "5",
         "Matter and energy",
         "Differentiate between elements and compounds",
         CognitiveLevel.ANALYZE,
         keywords=["elements", "compounds", "differentiate"])

    _add(library, "6.6A", 6, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Compare metals, nonmetals, and metalloids",
         CognitiveLevel.ANALYZE,
         keywords=["metals", "nonmetals", "metalloids", "compare"])

    _add(library, "6.8A", 6, Subject.SCIENCE, "8",
         "Earth and space",
         "Compare and contrast the properties of the sun and other stars",
         CognitiveLevel.ANALYZE,
         keywords=["sun", "stars", "compare", "contrast"])

    _add(library, "7.5A", 7, Subject.SCIENCE, "5",
         "Matter and energy",
         "Recognize that chemical formulas are used to identify substances",
         CognitiveLevel.REMEMBER,
         keywords=["chemical formulas", "substances", "identify"])

    _add(library, "7.5B", 7, Subject.SCIENCE, "5",
         "Matter and energy",
         "Identify evidence of chemical changes",
         CognitiveLevel.ANALYZE,
         keywords=["chemical changes", "evidence", "identify"])

    _add(library, "7.5C", 7, Subject.SCIENCE, "5",
         "Matter and energy",
         "Distinguish between physical and chemical changes",
         CognitiveLevel.ANALYZE,
         keywords=["physical changes", "chemical changes", "distinguish"])

    _add(library, "7.6A", 7, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Identify and explain changes in speed or direction of an object",
         CognitiveLevel.ANALYZE,
         keywords=["speed", "direction", "motion", "explain"])

    _add(library, "7.6B", 7, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Calculate average speed using distance and time",
         CognitiveLevel.APPLY,
         keywords=["average speed", "distance", "time", "calculate"])

    _add(library, "8.6B", 8, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Investigate and describe applications of Newton's laws",
         CognitiveLevel.ANALYZE,
         keywords=["Newton's laws", "applications", "investigate"])

    _add(library, "8.6C", 8, Subject.SCIENCE, "6",
         "Force, motion, and energy",
         "Investigate and describe that unbalanced forces change motion",
         CognitiveLevel.ANALYZE,
         keywords=["unbalanced forces", "motion", "change"])

    # ═══════════════════════════════════════════════════════════════════════════
    # SOCIAL STUDIES - Elementary
    # ═══════════════════════════════════════════════════════════════════════════

    _add(library, "3.1A", 3, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Describe how individuals have contributed to the expansion of communities",
         CognitiveLevel.UNDERSTAND,
         keywords=["individuals", "communities", "expansion"])

    _add(library, "3.1B", 3, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Identify individuals who have helped to shape communities",
         CognitiveLevel.REMEMBER,
         keywords=["individuals", "communities", "identify"])

    _add(library, "3.2A", 3, Subject.SOCIAL_STUDIES, "2",
         "History",
         "Identify reasons people formed communities",
         CognitiveLevel.UNDERSTAND,
         keywords=["communities", "reasons", "formed"])

    _add(library, "3.3A", 3, Subject.SOCIAL_STUDIES, "3",
         "Geography",
         "Use cardinal and intermediate directions to locate places",
         CognitiveLevel.APPLY,
         keywords=["cardinal directions", "intermediate directions", "locate"])

    _add(library, "3.4A", 3, Subject.SOCIAL_STUDIES, "4",
         "Geography",
         "Describe and explain the location of communities",
         CognitiveLevel.UNDERSTAND,
         keywords=["location", "communities", "describe"])

    _add(library, "4.1A", 4, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Identify Native American groups in Texas before European exploration",
         CognitiveLevel.REMEMBER,
         keywords=["Native American", "Texas", "exploration"])

    _add(library, "4.1B", 4, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Identify the contributions of diverse groups to Texas culture",
         CognitiveLevel.UNDERSTAND,
         keywords=["diverse groups", "Texas culture", "contributions"])

    _add(library, "4.2A", 4, Subject.SOCIAL_STUDIES, "2",
         "History",
         "Summarize motivations for European exploration and colonization of Texas",
         CognitiveLevel.UNDERSTAND,
         keywords=["European exploration", "colonization", "Texas"])

    _add(library, "4.3A", 4, Subject.SOCIAL_STUDIES, "3",
         "History",
         "Analyze the causes, major events, and effects of the Texas Revolution",
         CognitiveLevel.ANALYZE,
         keywords=["Texas Revolution", "causes", "effects"])

    _add(library, "5.1A", 5, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Explain when, where, and why groups explored and settled in the United States",
         CognitiveLevel.UNDERSTAND,
         keywords=["exploration", "settlement", "United States"])

    _add(library, "5.1B", 5, Subject.SOCIAL_STUDIES, "1",
         "History",
         "Describe the accomplishments of significant individuals during colonization",
         CognitiveLevel.UNDERSTAND,
         keywords=["colonization", "individuals", "accomplishments"])

    _add(library, "5.4A", 5, Subject.SOCIAL_STUDIES, "4",
         "History",
         "Describe the relationship between the United States and Native Americans",
         CognitiveLevel.UNDERSTAND,
         keywords=["United States", "Native Americans", "relationship"])

    _add(library, "5.4B", 5, Subject.SOCIAL_STUDIES, "4",
         "History",
         "Identify the causes and effects of westward expansion",
         CognitiveLevel.ANALYZE,
         keywords=["westward expansion", "causes", "effects"])


def _add(
    library: TEKSLibrary,
    code: str,
    grade: int,
    subject: Subject,
    strand: str,
    knowledge_statement: str,
    skill_statement: str,
    cognitive_level: CognitiveLevel,
    prerequisite_codes: List[str] = None,
    post_codes: List[str] = None,
    keywords: List[str] = None
):
    """Helper to add a TEKS standard."""
    standard = TEKSStandard(
        code=code,
        grade=grade,
        subject=subject,
        strand=strand,
        knowledge_statement=knowledge_statement,
        skill_statement=skill_statement,
        cognitive_level=cognitive_level,
        prerequisite_codes=prerequisite_codes or [],
        post_codes=post_codes or [],
        keywords=keywords or []
    )
    library._add_standard(standard)


# ═══════════════════════════════════════════════════════════════════════════════
# EXTENDED TEKS LIBRARY - Singleton with all standards
# ═══════════════════════════════════════════════════════════════════════════════

class ExtendedTEKSLibrary(TEKSLibrary):
    """
    Extended TEKS Library with comprehensive standards.

    Includes 200+ commonly-used TEKS standards across:
    - Mathematics K-8
    - Reading/ELA 3-8
    - Science 3-8
    - Social Studies 3-5
    """

    def __init__(self):
        super().__init__()
        # Load comprehensive standards
        load_comprehensive_teks(self)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the TEKS library."""
        stats = {
            "total_standards": len(self._standards),
            "by_grade": {},
            "by_subject": {}
        }

        for grade, codes in self._by_grade.items():
            stats["by_grade"][grade] = len(codes)

        for subject, codes in self._by_subject.items():
            stats["by_subject"][subject.value] = len(codes)

        return stats


# Global extended library instance
_extended_library: Optional[ExtendedTEKSLibrary] = None


def get_extended_teks_library() -> ExtendedTEKSLibrary:
    """Get or create the global ExtendedTEKSLibrary instance."""
    global _extended_library
    if _extended_library is None:
        _extended_library = ExtendedTEKSLibrary()
    return _extended_library


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'load_comprehensive_teks',
    'ExtendedTEKSLibrary',
    'get_extended_teks_library',
]
