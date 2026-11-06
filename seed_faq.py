
import sqlite3

DATABASE_FILE = "claro.db"


# ============================================================
# FAQ DATA
# Format:
# (category, question, answer, keywords)
# No URLs are stored.
# ============================================================

FAQ_DATA = [

    # ========================================================
    # CLARO
    # ========================================================

    (
        "CLARO",
        "What is CLARO?",
        "CLARO stands for Claro, Your Intelligent Campus Companion. "
        "It is a campus assistance robot designed to help students "
        "find information about Busan International College and "
        "Tongmyong University.",
        "claro, robot, campus companion, introduction, about"
    ),

    (
        "CLARO",
        "What can CLARO do?",
        "CLARO can listen to student questions, recognize speech, "
        "search its locally stored campus knowledge, and respond "
        "using speech. It is designed to provide information about "
        "BIC, academic programs, professors, and student services.",
        "claro, features, functions, capabilities, voice, speech, robot"
    ),

    (
        "CLARO",
        "Does CLARO need an internet connection?",
        "CLARO V1 is designed to retrieve answers from locally stored "
        "information using its SQLite database. Its knowledge database "
        "does not require an internet connection. Speech recognition "
        "and speech generation must also be configured with local tools "
        "for the complete system to operate offline.",
        "offline, internet, wifi, connection, database, local"
    ),

    # ========================================================
    # BUSAN INTERNATIONAL COLLEGE
    # ========================================================

    (
        "BIC",
        "What is BIC?",
        "BIC stands for Busan International College. It is an "
        "international college at Tongmyong University in Busan, "
        "South Korea.",
        "bic, busan international college, international college, tongmyong"
    ),

    (
        "BIC",
        "What is the vision of BIC?",
        "The vision of Busan International College is "
        "Educating The Next Global Innovators.",
        "bic, vision, global innovators, future"
    ),

    (
        "BIC",
        "What is the mission of BIC?",
        "BIC focuses on three main mission areas: Management, "
        "Technology, and Contents. Its educational approach aims "
        "to develop students who can contribute to a global society.",
        "bic, mission, management, technology, contents"
    ),

    (
        "BIC",
        "What teaching methods does BIC use?",
        "BIC uses active learning approaches including Action Learning, "
        "Flipped Learning, and Project-Based Learning. These approaches "
        "emphasize participation, practical activities, collaboration, "
        "and project experience.",
        "bic, teaching, learning, action learning, flipped learning, "
        "project based learning, education"
    ),

    (
        "BIC",
        "Where is Busan International College located?",
        "Busan International College is located at Building 19, "
        "428 Sinseon-ro, Nam-gu, Busan 48520, Republic of Korea.",
        "bic, location, address, campus, building, busan"
    ),

    (
        "BIC",
        "How can I contact Busan International College?",
        "The official BIC contact number listed for general inquiries "
        "is +82-51-629-3065. The college is located in Building 19 "
        "at Tongmyong University, Busan.",
        "bic, contact, phone, telephone, help, inquiry"
    ),

    (
        "BIC",
        "What language is used for BIC courses?",
        "BIC describes its curriculum as 100 percent English-taught. "
        "Students should check individual course information and "
        "official academic announcements for any course-specific details.",
        "bic, language, english, courses, curriculum, international students"
    ),

    (
        "BIC",
        "What are the core competencies of BIC?",
        "BIC emphasizes global and practical competencies, including "
        "critical and creative thinking, global leadership and "
        "collaboration, cross-cultural communication, global citizenship, "
        "sustainability, Korean language, mentoring, and IT fundamentals.",
        "bic, competencies, skills, critical thinking, creativity, "
        "leadership, communication, global citizenship"
    ),

    # ========================================================
    # UNDERGRADUATE PROGRAMS
    # ========================================================

    (
        "PROGRAMS",
        "What undergraduate programs are available at BIC?",
        "Busan International College lists seven undergraduate programs: "
        "1. BA in Global Business. "
        "2. BS in AI and Computer Engineering. "
        "3. BS in Information System and Security. "
        "4. BS in Mechanical and Automotive Engineering. "
        "5. BA in Global Korean Studies. "
        "6. BA in Tech Management and Innovation. "
        "7. BA in Digital Design and Marketing.",
        "bic, programs, departments, majors, undergraduate, degree, courses"
    ),

    (
        "PROGRAMS",
        "What is AI and Computer Engineering about?",
        "The AI and Computer Engineering program covers computer "
        "hardware and software, artificial intelligence, and big data. "
        "Students study areas such as programming, computer architecture, "
        "algorithms, data structures, machine learning, data mining, "
        "natural language processing, and computer vision.",
        "ai, computer engineering, program, major, machine learning, "
        "big data, programming"
    ),

    (
        "PROGRAMS",
        "What subjects are studied in AI and Computer Engineering?",
        "Students study programming languages, algorithms, data structures, "
        "digital systems, computer architecture, machine learning, "
        "data mining, natural language processing, and computer vision. "
        "Practical learning may involve Python, TensorFlow, PyTorch, "
        "laboratory work, and projects.",
        "ai, subjects, curriculum, python, tensorflow, pytorch, "
        "computer vision, nlp, algorithms, data structures"
    ),

    (
        "PROGRAMS",
        "What is Global Business?",
        "The Global Business program covers business-related areas "
        "including human resource management, finance, accounting, "
        "and management information systems.",
        "global business, business, finance, accounting, management, HR"
    ),

    (
        "PROGRAMS",
        "What is Information System and Security?",
        "The Information System and Security program covers areas "
        "including Linux, databases, web and cloud technologies, "
        "open-source software, Internet of Things, computer networks, "
        "cryptography, malware, and network and system security.",
        "information system, security, cybersecurity, linux, database, "
        "network, cloud, cryptography, malware, iot"
    ),

    # ========================================================
    # AI & COMPUTER ENGINEERING FACULTY
    # ========================================================

    (
        "PROFESSORS",
        "Who are the professors in AI and Computer Engineering?",
        "The faculty directory lists Jun Mo Jo, Dong Hoon Lee, "
        "Jack Charles Turvin Jr., Kouayep Sonia Carole, "
        "Rodgers Agil Jato Ochieng, Sinshaw Yenewondim Biadgie, "
        "and Zhang Ruyang.",
        "professors, faculty, teachers, instructors, ai, computer engineering"
    ),

    (
        "PROFESSORS",
        "Who is Professor Jun Mo Jo?",
        "Professor Jun Mo Jo is listed in the AI and Computer "
        "Engineering faculty directory. His office is in Information "
        "Communication Building 1, Room 507. His university contact "
        "number is 051-629-1152 and his university email is jun@tu.ac.kr.",
        "jun mo jo, jun jo, professor, faculty, office, contact"
    ),

    (
        "PROFESSORS",
        "Who is Professor Dong Hoon Lee?",
        "Professor Dong Hoon Lee is listed in the AI and Computer "
        "Engineering faculty directory. His office is in Building 1, "
        "Room 315. His university contact number is 051-629-1342 "
        "and his university email is ldh5522@tu.ac.kr.",
        "dong hoon lee, professor lee, faculty, office, contact"
    ),

    (
        "PROFESSORS",
        "Who is Professor Jack Charles Turvin Jr.?",
        "Professor Jack Charles Turvin Jr. is listed in the AI and "
        "Computer Engineering faculty directory. His office is in "
        "Building 17, Room 413. His university contact number is "
        "051-629-3093 and his university email is jack@tu.ac.kr.",
        "jack charles turvin, jack turvin, professor, faculty, office"
    ),

    (
        "PROFESSORS",
        "Who is Professor Kouayep Sonia Carole?",
        "Kouayep Sonia Carole is listed in the AI and Computer "
        "Engineering faculty directory. Contact the university "
        "through its official academic channels for assistance.",
        "kouayep sonia carole, professor, faculty, teacher"
    ),

    (
        "PROFESSORS",
        "Who is Professor Rodgers Agil Jato Ochieng?",
        "Professor Rodgers Agil Jato Ochieng is listed in the AI and "
        "Computer Engineering faculty directory. His office is in "
        "Building 11, Room 330. His university contact number is "
        "051-629-3179 and his university email is "
        "rodgers.ochieng@tu.ac.kr.",
        "rodgers agil jato ochieng, rodgers ochieng, professor, faculty"
    ),

    (
        "PROFESSORS",
        "Who is Professor Sinshaw Yenewondim Biadgie?",
        "Professor Sinshaw Yenewondim Biadgie is listed in the AI and "
        "Computer Engineering faculty directory. His office is in "
        "Building 11, Room 316. His university email is "
        "wondim2026@tu.ac.kr.",
        "sinshaw yenewondim biadgie, sinshaw, professor, faculty, office"
    ),

    (
        "PROFESSORS",
        "Who is Professor Zhang Ruyang?",
        "Professor Zhang Ruyang is listed in the AI and Computer "
        "Engineering faculty directory. His office is in Building 17, "
        "Room 406. His university email is ruyangz@tu.ac.kr.",
        "zhang ruyang, zhang, professor, faculty, office"
    ),

    # ========================================================
    # ACADEMIC INFORMATION
    # ========================================================

    (
        "ACADEMIC",
        "How can I register for courses?",
        "Students can register for courses through the Tongmyong "
        "University student portal at sg.tu.ac.kr. The student ID "
        "is used as the login ID, and the password is the same as "
        "the my.tu.ac.kr portal password. Students should check "
        "semester announcements and their department's graduation "
        "requirements before registering.",
        "course registration, register, courses, subject, sg.tu.ac.kr, portal"
    ),

    (
        "ACADEMIC",
        "How can I change the language in LearningX?",
        "To change the language in LearningX, change the e-Campus "
        "language setting and log in to LearningX again. The attendance "
        "application may also require a second authentication step.",
        "learningx, language, english, korean, ecampus, attendance, app"
    ),

    (
        "ACADEMIC",
        "Where can I get an enrollment certificate?",
        "Students can use the university certificate kiosks. "
        "The listed locations include Building 17, third floor; "
        "Building 8, first floor; and Building 1, second floor. "
        "Certificates may be available in Korean or English.",
        "certificate, enrollment, transcript, academic record, kiosk, document"
    ),

    (
        "ACADEMIC",
        "Are makeup classes required?",
        "Students are expected to attend scheduled makeup classes. "
        "They should follow the course instructor's announcements "
        "and the university's attendance policy.",
        "makeup class, make up, attendance, absence, class"
    ),

    (
        "ACADEMIC",
        "Can I apply for a double major at BIC?",
        "Students may apply for a double major through the My Portal "
        "during the designated application period. The published "
        "BIC guidance describes a credit structure of 36 credits "
        "for the primary major, 36 credits for the secondary major, "
        "and 30 general education credits. Students should confirm "
        "the current requirements with the academic support team.",
        "double major, second major, credits, application, my portal"
    ),

    (
        "ACADEMIC",
        "How can I check my tuition invoice?",
        "Students can check their tuition invoice through the university "
        "student services portal under Registered Information and "
        "View Tuition Invoice. Tuition payment periods and payment "
        "instructions are announced each semester. Students should "
        "check the latest university announcement for the current "
        "payment deadline.",
        "tuition, invoice, payment, fee, semester, registered information"
    ),

    (
        "ACADEMIC",
        "Can I pay tuition in installments?",
        "BIC guidance indicates that students can ask the BIC Education "
        "Support Team about tuition installment applications. "
        "Availability and application conditions may depend on the "
        "student's circumstances and visa schedule.",
        "tuition, installment, payment, fee, education support team"
    ),

    (
        "ACADEMIC",
        "How can I change my major?",
        "The published BIC guidance says students must have completed "
        "at least one semester before applying to change their major. "
        "Applications are submitted through my.tu.ac.kr during the "
        "designated summer or winter application period. Students "
        "should confirm the current schedule with academic support.",
        "change major, major change, department transfer, application"
    ),

]


# ============================================================
# DATABASE SETUP
# ============================================================

def setup_database():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # Create FAQ table if it does not exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            keywords TEXT
        )
    """)

    # Remove previous sample FAQ records.
    # This does not delete the knowledge table.
    cursor.execute("DELETE FROM faq")

    # Store actual information in SQLite.
    cursor.executemany("""
        INSERT INTO faq (
            category,
            question,
            answer,
            keywords
        )
        VALUES (?, ?, ?, ?)
    """, FAQ_DATA)

    connection.commit()

    # Verify the number of stored records.
    cursor.execute("SELECT COUNT(*) FROM faq")
    total = cursor.fetchone()[0]

    connection.close()

    print("=" * 50)
    print("CLARO OFFLINE FAQ DATABASE")
    print("=" * 50)
    print("Database:", DATABASE_FILE)
    print("Successfully stored:", total, "FAQs")
    print("Website URLs stored: 0")
    print("Database setup completed.")
    print("=" * 50)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    setup_database()
