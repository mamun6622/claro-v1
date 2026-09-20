
import json
import re

DATABASE_FILE = "database/bic_knowledge.json"


# Words that usually don't help identify the topic.
STOP_WORDS = {
    "what", "where", "when", "who", "why", "how",
    "is", "are", "the", "a", "an", "of", "to",
    "in", "on", "for", "and", "or", "do", "does",
    "can", "i", "me", "tell", "about", "please",
    "there", "this", "that"
}


def load_knowledge():
    try:
        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        print("Knowledge database not found.")
        return []


def tokenize(text):
    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    }


def split_into_chunks(text):
    """
    Break a webpage into small searchable pieces.
    """

    # First split by common sentence boundaries.
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    chunks = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 20:
            continue

        chunks.append(sentence)

    return chunks


def search_knowledge(question, top_k=3):

    knowledge = load_knowledge()

    if not knowledge:
        return []

    question_words = tokenize(question)

    results = []

    for page in knowledge:

        title = page.get("title", "")
        url = page.get("url", "")
        text = page.get("text", "")

        chunks = split_into_chunks(text)

        for chunk in chunks:

            chunk_words = tokenize(
                title + " " + chunk
            )

            matching_words = (
                question_words & chunk_words
            )

            score = len(matching_words)

            # Give a small bonus when words
            # appear in the page title.
            title_words = tokenize(title)

            title_matches = (
                question_words & title_words
            )

            score += len(title_matches) * 2

            if score > 0:

                results.append({
                    "score": score,
                    "text": chunk,
                    "title": title,
                    "url": url
                })

    # Highest score first.
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


def make_answer(question):

    q = question.lower().strip()

    # Remove punctuation
    q = q.replace(".", "")
    q = q.replace(",", "")
    q = q.replace("!", "")
    q = q.replace("?", "")
    q = q.strip()

    # ==================================================
    # GREETINGS
    # ==================================================

    greetings = {
        "hi",
        "hello",
        "hey",
        "hi claro",
        "hello claro",
        "hey claro",
        "good morning",
        "good afternoon",
        "good evening"
    }

    if q in greetings:
        return (
            "Hello! I'm CLARO, your intelligent campus companion. "
            "How can I help you today?"
        )

    # ==================================================
    # WHO ARE YOU?
    # ==================================================

    identity_phrases = [
        "who are you",
        "who are you?",
        "what are you",
        "what is your name",
        "what's your name",
        "tell me about yourself"
    ]

    if any(
        phrase in q
        for phrase in identity_phrases
    ):
        return (
            "I'm CLARO, your intelligent campus companion. "
            "I can help you find information about Tongmyong University "
            "and BIC."
        )

    # ==================================================
    # WHAT CAN YOU DO?
    # ==================================================

    capability_phrases = [
        "what can you do",
        "what do you do",
        "how can you help",
        "what are your functions",
        "what are your features",
        "what can claro do",
        "how can claro help"
    ]

    if any(
        phrase in q
        for phrase in capability_phrases
    ):
        return (
            "I can help you find campus information, "
            "answer questions about BIC and Tongmyong University, "
            "and provide information about programs, admissions, "
            "campus facilities, and other university services."
        )

    # ==================================================
    # NORMAL CAMPUS QUESTION
    # ==================================================

    results = search_knowledge(
        question,
        top_k=3
    )

    if not results:
        return (
            "Sorry, I couldn't find that information "
            "in my campus database."
        )

    answer_parts = []

    for result in results:

        text = result["text"]

        if text not in answer_parts:
            answer_parts.append(text)

    answer = " ".join(
        answer_parts[:3]
    )

    words = answer.split()

    if len(words) > 70:
        answer = " ".join(
            words[:70]
        ) + "."

    return answer


if __name__ == "__main__":

    print("=" * 40)
    print("CLARO V1 SEARCH TEST")
    print("=" * 40)
    print("Type 'exit' to quit.")

    while True:

        question = input("\nYou: ").strip()

        if question.lower() in [
            "exit",
            "quit"
        ]:
            break

        results = search_knowledge(question)

        print("\nSearch results:")

        for result in results:

            print(
                f"\nScore: {result['score']}"
            )

            print(
                f"Page: {result['title']}"
            )

            print(
                f"Text: {result['text']}"
            )

        print("\nCLARO:")
        print(make_answer(question))
