
import sqlite3
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "claro.db"

FAQ_MATCH_THRESHOLD = 2
KNOWLEDGE_MATCH_THRESHOLD = 2

# Maximum length of each knowledge text section.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# ============================================================
# TEXT PROCESSING
# ============================================================

def tokenize(text):
    """
    Convert text into searchable words.

    Supports English, numbers, and Korean characters.
    """

    if not text:
        return []

    return re.findall(
        r"[a-zA-Z0-9가-힣]+",
        text.lower()
    )


def normalize(text):
    """
    Normalize text for comparison.
    """

    return " ".join(tokenize(text))


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Open the local SQLite database.
    """

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# FAQ SEARCH
# ============================================================

def search_faq(question):
    """
    Search the FAQ table first.

    Returns the best matching FAQ answer.
    Returns None when no sufficiently strong match exists.
    """

    query = normalize(question)

    if not query:
        return None

    query_tokens = set(tokenize(question))

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, category, question, answer, keywords
            FROM faq
        """)

        rows = cursor.fetchall()
        connection.close()

    except sqlite3.Error as error:
        print("FAQ database error:", error)
        return None

    best_match = None
    best_score = 0

    for row in rows:

        faq_question = row["question"] or ""
        faq_answer = row["answer"] or ""
        faq_keywords = row["keywords"] or ""

        normalized_faq_question = normalize(faq_question)

        faq_question_tokens = set(
            tokenize(faq_question)
        )

        keyword_tokens = set(
            tokenize(faq_keywords)
        )

        score = 0

        # Exact question match.
        if query == normalized_faq_question:
            score = 100

        # Full question phrase match.
        elif (
            normalized_faq_question
            and normalized_faq_question in query
        ):
            score = 50

        else:

            # Matching question words.
            question_matches = (
                query_tokens & faq_question_tokens
            )

            # Matching keywords.
            keyword_matches = (
                query_tokens & keyword_tokens
            )

            score += len(question_matches) * 2
            score += len(keyword_matches)

            # Reward matching the complete query phrase.
            if query and query in normalized_faq_question:
                score += 3

        if score > best_score:
            best_score = score

            best_match = {
                "id": row["id"],
                "category": row["category"],
                "question": faq_question,
                "answer": faq_answer,
                "score": score
            }

    if best_match and best_score >= FAQ_MATCH_THRESHOLD:

        print("\n[FAQ MATCH]")
        print("Category:", best_match["category"])
        print("Question:", best_match["question"])
        print("Score:", best_match["score"])

        return best_match

    return None


# ============================================================
# KNOWLEDGE DATABASE
# ============================================================

def load_knowledge():
    """
    Load previously stored campus information
    from the knowledge table.
    """

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, url, title, content
            FROM knowledge
        """)

        rows = cursor.fetchall()
        connection.close()

        knowledge = []

        for row in rows:

            knowledge.append({
                "id": row["id"],
                "url": row["url"],
                "title": row["title"],
                "text": row["content"]
            })

        return knowledge

    except sqlite3.Error as error:

        print("Knowledge database error:", error)
        return []


# ============================================================
# SPLIT KNOWLEDGE INTO SMALL SECTIONS
# ============================================================

def split_into_chunks(text):
    """
    Divide long knowledge text into smaller sections.
    """

    if not text:
        return []

    words = text.split()

    if len(words) <= CHUNK_SIZE:
        return [text]

    chunks = []

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ============================================================
# KNOWLEDGE SEARCH
# ============================================================

def search_knowledge(question):
    """
    Search the knowledge table when no FAQ matches.
    """

    query_tokens = set(tokenize(question))

    if not query_tokens:
        return None

    knowledge_data = load_knowledge()

    best_match = None
    best_score = 0

    for item in knowledge_data:

        title = item["title"] or ""
        content = item["text"] or ""

        title_tokens = set(tokenize(title))

        chunks = split_into_chunks(content)

        for chunk in chunks:

            chunk_tokens = set(tokenize(chunk))

            score = 0

            # Content word matches.
            content_matches = (
                query_tokens & chunk_tokens
            )

            score += len(content_matches)

            # Title matches receive extra weight.
            title_matches = (
                query_tokens & title_tokens
            )

            score += len(title_matches) * 2

            if score > best_score:

                best_score = score

                best_match = {
                    "title": title,
                    "text": chunk,
                    "url": item["url"],
                    "score": score
                }

    if best_match and best_score >= KNOWLEDGE_MATCH_THRESHOLD:

        print("\n[KNOWLEDGE MATCH]")
        print("Title:", best_match["title"])
        print("Score:", best_match["score"])

        return best_match

    return None


# ============================================================
# BASIC INTENTS
# ============================================================

def is_greeting(question):

    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "hi claro",
        "hello claro"
    }

    normalized_question = normalize(question)

    return normalized_question in {
        normalize(item) for item in greetings
    }


def is_identity_question(question):

    patterns = [
        "who are you",
        "what are you",
        "introduce yourself",
        "what is your name",
        "your name"
    ]

    normalized_question = normalize(question)

    return any(
        pattern in normalized_question
        for pattern in patterns
    )


def is_capability_question(question):

    patterns = [
        "what can you do",
        "your features",
        "your capabilities",
        "how can you help",
        "what do you do"
    ]

    normalized_question = normalize(question)

    return any(
        pattern in normalized_question
        for pattern in patterns
    )


# ============================================================
# ANSWER GENERATION
# ============================================================

def make_answer(question):
    """
    Main CLARO question-answering function.

    Priority:
        1. Greeting
        2. CLARO identity
        3. CLARO capabilities
        4. SQLite FAQ
        5. SQLite knowledge
        6. Unknown question response
    """

    if not question or not question.strip():

        return (
            "I didn't hear a question. "
            "Could you please ask again?"
        )

    question = question.strip()

    print("\n" + "=" * 50)
    print("CLARO QUESTION:", question)
    print("=" * 50)

    # --------------------------------------------------------
    # 1. Greeting
    # --------------------------------------------------------

    if is_greeting(question):

        return (
            "Hello! I am CLARO, your intelligent campus companion. "
            "How can I help you today?"
        )

    # --------------------------------------------------------
    # 2. Identity
    # --------------------------------------------------------

    if is_identity_question(question):

        return (
            "I am CLARO, your intelligent campus companion. "
            "I am designed to help students find information "
            "about Busan International College and Tongmyong University."
        )

    # --------------------------------------------------------
    # 3. Capabilities
    # --------------------------------------------------------

    if is_capability_question(question):

        return (
            "I can help you find information about Busan International "
            "College, academic programs, professors, campus information, "
            "and student services. You can simply ask me a question."
        )

    # --------------------------------------------------------
    # 4. Search FAQ database first
    # --------------------------------------------------------

    faq_result = search_faq(question)

    if faq_result:

        return faq_result["answer"]

    # --------------------------------------------------------
    # 5. Search general knowledge database
    # --------------------------------------------------------

    knowledge_result = search_knowledge(question)

    if knowledge_result:

        return (
            f"According to the stored information about "
            f"{knowledge_result['title']}: "
            f"{knowledge_result['text']}"
        )

    # --------------------------------------------------------
    # 6. No answer found
    # --------------------------------------------------------

    return (
        "I am sorry, but I don't have enough stored information "
        "to answer that question. Please contact the BIC "
        "Education Support Team for further assistance."
    )


# ============================================================
# TERMINAL TESTING
# ============================================================

if __name__ == "__main__":

    print("\nCLARO OFFLINE QUESTION ANSWERING SYSTEM")
    print("Type 'exit' to stop.")

    while True:

        user_question = input("\nYou: ").strip()

        if user_question.lower() in ["exit", "quit"]:

            print("CLARO: Goodbye!")
            break

        answer = make_answer(user_question)

        print("\nCLARO:", answer)
