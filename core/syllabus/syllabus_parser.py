import re
import sqlite3


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SENTINEL = "\x00"
_UNIT_HEADER = re.compile(
    r'\b(?:Unit|Module)\s*[:\-]?\s*([0-9]+|[IVXLCDM]+)\b',
    re.IGNORECASE
)

# Segments (or trailing words) shorter than this with no internal spaces are
# treated as compound-name fragments and re-merged with the adjacent segment.
#   Preserves: Gram(4), Floyd(5), Human(5), AM(2), DSB(3), M(1), non(3),
#              big(3), Euler(5) ...
#   Leaves alone: decomposition(13), Gaussian(8), Matrices(8), Dijkstra(8) ...
_MIN_FRAG_LEN = 6
_HYPHEN_PLACEHOLDER = "__HYPHEN__"
_HYPHEN_PROTECTED_TERMS = {
    "object-oriented",
    "built-in",
    "multi-dimensional",
    "non-primitive",
}


# ---------------------------------------------------------------------------
# Stage 1 — Unit splitting
# ---------------------------------------------------------------------------

def _split_into_units(raw_text: str) -> dict[int, str]:
    """
    Split a raw multi-unit blob into {unit_number: unit_text}.
    Falls back to {1: raw_text} when no 'Unit N' headers are found.
    """
    matches = list(_UNIT_HEADER.finditer(raw_text))
    if not matches:
        return {1: raw_text.strip()}

    units: dict[int, str] = {}
    for i, m in enumerate(matches):
        unit_num = _parse_unit_number(m.group(1))
        if unit_num is None:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        units[unit_num] = raw_text[start:end].strip()
    return units or {1: raw_text.strip()}


def _parse_unit_number(token: str) -> int | None:
    """Parse either arabic digits or Roman numerals into an integer."""
    token = token.strip()
    if token.isdigit():
        return int(token)

    roman = token.upper()
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    if any(ch not in roman_values for ch in roman):
        return None

    total = 0
    prev = 0
    for ch in reversed(roman):
        val = roman_values[ch]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total if total > 0 else None


# ---------------------------------------------------------------------------
# Stage 2 — Pre-processing
# ---------------------------------------------------------------------------

def _normalize_whitespace(text: str) -> str:
    """
    Collapse newline variants to spaces, then squeeze multiple spaces to one.
    Handles copy-paste artefacts from indented triple-quoted strings, PDFs, etc.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _fix_broken_hyphens(text: str) -> str:
    """
    Rejoin "multi- dimensional" (hyphen + space + lowercase/digit) artefacts
    that appear when copy-pasting from PDFs or Word documents.

    Must run BEFORE sentinel injection so these hyphens are already fused
    and won't be mistaken for topic-separator hyphens.
    """
    return re.sub(r'-\s+(?=[a-z0-9])', '-', text)


def _protect_hyphenated_terms(text: str) -> str:
    """Protect common lexical compounds so split rules don't damage them."""
    for term in _HYPHEN_PROTECTED_TERMS:
        text = re.sub(
            re.escape(term),
            lambda m: m.group(0).replace('-', _HYPHEN_PLACEHOLDER),
            text,
            flags=re.IGNORECASE
        )
    return text


def _restore_hyphenated_terms(text: str) -> str:
    """Undo temporary hyphen protection markers."""
    return text.replace(_HYPHEN_PLACEHOLDER, "-")


# ---------------------------------------------------------------------------
# Stage 3 — Sentinel injection
# ---------------------------------------------------------------------------

def _inject_sentinels(text: str) -> str:
    """
    Replace unambiguous topic-boundary markers with a null sentinel.
    Runs AFTER _fix_broken_hyphens.

    Rules (most specific first):
      1. en-dash (U+2013) / em-dash (U+2014) — always separators
      2. ' - '  (space · hyphen · space)     — unambiguous separator
      3. hyphen (± trailing space) before a CAPITAL letter
         e.g. "Matrices- Special", "decomposition-Gram"
         Compound names this rule accidentally splits (Gram-Schmidt,
         Floyd-Warshall, Euler-Lagrange, big-Oh) are recovered in Stage 4.
    """
    text = re.sub(r'\s*[\u2013\u2014]\s*', _SENTINEL, text)   # Rule 1
    text = re.sub(r'\s+-\s+', _SENTINEL, text)                 # Rule 2
    text = re.sub(r'-\s*(?=[A-Z])', _SENTINEL, text)           # Rule 3
    return text


# ---------------------------------------------------------------------------
# Stage 4 — Short-fragment merge
# ---------------------------------------------------------------------------

def _is_fragment(s: str) -> bool:
    """
    True when a word or token is too short to be a standalone topic name.
    A fragment has no internal spaces (it is a single token) and is shorter
    than _MIN_FRAG_LEN characters.
    """
    return len(s) < _MIN_FRAG_LEN and ' ' not in s and bool(re.search(r'[A-Za-z]', s))


def _should_hold_fragment(seg: str, next_seg: str | None) -> bool:
    """
    Decide whether a short segment should be merged with the next segment.

    Guards against false merges for valid short standalone topics such as
    "Trees - Graphs - Arrays", while still preserving compounds where the
    right side contains additional phrase context (e.g. "Schmidt Orthogonalization").
    """
    if not _is_fragment(seg):
        return False
    if next_seg is None:
        return False

    nxt = next_seg.strip()
    if not nxt:
        return False

    # Require phrase-like continuation to reduce accidental topic joining.
    if ' ' not in nxt and not re.search(r'[,.;:()]', nxt):
        return False

    if seg.isupper():
        return True
    if seg[:1].isupper():
        return True
    return len(seg) <= 3


def _peel_trailing_fragment(seg: str) -> tuple[str, str | None]:
    """
    If a segment ends with a short word (a potential compound-name prefix
    that was split off its suffix), separate it out.

    Example
    -------
    "...Basics of Algorithm Analysis, big"  ->  ("...Basics of Algorithm Analysis,", "big")
    "...Dijkstra's algorithm, Floyd"        ->  ("...Dijkstra's algorithm,", "Floyd")
    "Gram-Schmidt Orthogonalization"        ->  (same, None)   -- suffix is long

    Single-word segments ("Gram", "Floyd") are handled by _is_fragment and
    never reach this function; rfind(' ') == -1 guards that path.
    """
    last_space = seg.rfind(' ')
    if last_space == -1:
        return seg, None   # single-word segment — let _is_fragment decide
    last_word = seg[last_space + 1:]
    if _is_fragment(last_word) and seg[:last_space].rstrip().endswith((',', ';', ':')):
        return seg[:last_space], last_word
    return seg, None


def _merge_fragments(parts: list[str]) -> list[str]:
    """
    Re-join compound-name fragments with the segment that should follow them.

    Two fragment patterns are detected:

    A) The ENTIRE segment is a fragment:
       ["QR decomposition", "Gram", "Schmidt Orthogonalization"]
        ->  ["QR decomposition", "Gram-Schmidt Orthogonalization"]

    B) The segment ENDS with a fragment word (the common case when the
       fragment sits in the middle of a longer comma-separated block):
       ["...Algorithm Analysis, big", "Oh notation, ..."]
        ->  ["...Algorithm Analysis,", "big-Oh notation, ..."]

       ["...BellmanFord algorithm, Floyd", "Warshall algorithm"]
        ->  ["...BellmanFord algorithm,", "Floyd-Warshall algorithm"]

    Accumulating chains ("AM", "DSB", "SC") also work because each short
    result re-triggers the check until it grows long enough.
    """
    merged: list[str] = []
    pending: str | None = None   # fragment carried forward to prepend to next seg

    for idx, raw in enumerate(parts):
        seg = raw.strip()
        if not seg:
            continue

        # Prepend any fragment held from the previous iteration
        if pending is not None:
            seg = pending + '-' + seg
            pending = None

        # --- Pattern A: the whole segment is a fragment ---
        next_non_empty: str | None = None
        for candidate in parts[idx + 1:]:
            if candidate.strip():
                next_non_empty = candidate.strip()
                break

        if _should_hold_fragment(seg, next_non_empty):
            pending = seg
            continue

        # --- Pattern B: the segment ends with a fragment word ---
        main, tail = _peel_trailing_fragment(seg)
        if tail is not None:
            if main.strip():
                merged.append(main)
            pending = tail
        else:
            merged.append(seg)

    # Trailing pending fragment: glue onto the last accepted topic
    if pending is not None:
        if merged:
            merged[-1] = merged[-1] + '-' + pending
        else:
            merged.append(pending)

    return merged


def _clean_topic(text: str) -> str:
    """Strip stray punctuation and whitespace from both ends of a topic."""
    text = text.strip()
    text = re.sub(r'^[\s,.\-\u2013\u2014]+|[\s,.\-\u2013\u2014]+$', '', text)
    text = _restore_hyphenated_terms(text)
    return text.strip()


def _split_fine_grained(parts: list[str]) -> list[str]:
    """
    Split merged segments into finer topics using sentence/comma boundaries.
    Keeps ordering and filters empty fragments.
    """
    fine: list[str] = []
    for part in parts:
        # First split sentence-like boundaries, then comma-separated lists.
        sentence_parts = re.split(r'(?<=[A-Za-z0-9\)])\.\s+', part)
        for sent in sentence_parts:
            comma_parts = re.split(r'\s*,\s*', sent)
            for item in comma_parts:
                cleaned = item.strip()
                if cleaned:
                    fine.append(cleaned)
    return fine


# ---------------------------------------------------------------------------
# Public parsing API
# ---------------------------------------------------------------------------

def parse_unit_text(unit_text: str) -> list[str]:
    """
    Parse a single unit's syllabus text into an ordered list of topic names.

    Use this function from the Streamlit UI, where the user already has text
    split into per-unit text areas.

    Pipeline
    --------
    1. Normalise whitespace   (collapse newlines + multi-spaces)
    2. Repair broken hyphens  ("multi- dimensional" -> "multi-dimensional")
    3. Protect lexical hyphens (object-oriented, built-in, ...)
    4. Inject sentinels        (en-dashes, ' - ', hyphen-before-capital)
    5. Split on sentinels
    6. Re-merge fragments      (Gram-Schmidt, Floyd-Warshall, big-Oh, AM-DSB-SC ...)
    7. Fine-grained split      (sentence/comma boundaries)
    8. Clean and filter
    """
    text = _normalize_whitespace(unit_text)
    text = _fix_broken_hyphens(text)
    text = _protect_hyphenated_terms(text)
    text = _inject_sentinels(text)

    raw_parts = text.split(_SENTINEL)
    parts = _merge_fragments(raw_parts)
    parts = _split_fine_grained(parts)

    topics: list[str] = []
    for part in parts:
        cleaned = _clean_topic(part)
        if cleaned and re.search(r'[a-zA-Z]', cleaned):
            topics.append(cleaned)
    return topics


def parse_syllabus_text(raw_text: str) -> dict[int, list[str]]:
    """
    Parse a complete multi-unit syllabus blob in one call.

    Detects 'Unit N' headers automatically and splits accordingly.
    Returns {unit_number: [topic, topic, ...]}.

    Falls back to {1: [...]} when no unit headers are present.

    API NOTE: Return type changed from the previous version (was list[str]).
    Call parse_unit_text() directly when working with a pre-split unit string
    (e.g. from individual Streamlit text areas).
    """
    units_raw = _split_into_units(raw_text)
    return {num: parse_unit_text(text) for num, text in sorted(units_raw.items())}


def _run_parser_self_tests() -> None:
    """Lightweight parser checks for frequent syllabus formatting edge cases."""
    # Broken copy/paste spacing and hyphens
    assert parse_unit_text("single and multi- dimensional arrays") == [
        "single and multi-dimensional arrays"
    ]
    assert parse_unit_text("Topic\tA\n\n  -   Topic B") == ["Topic A", "Topic B"]

    # Compound names should be preserved
    compound_topics = parse_unit_text(
        "QR decomposition-Gram-Schmidt Orthogonalization- "
        "Basics of Algorithm Analysis, big-Oh notation- "
        "BellmanFord algorithm, Floyd-Warshall algorithm- "
        "Euler-Lagrange equation"
    )
    assert any("Gram-Schmidt" in t for t in compound_topics)
    assert any("big-Oh" in t for t in compound_topics)
    assert any("Floyd-Warshall" in t for t in compound_topics)
    assert any("Euler-Lagrange" in t for t in compound_topics)

    # Short standalone topics should not be forcibly merged
    assert parse_unit_text("Trees - Graphs - Arrays") == ["Trees", "Graphs", "Arrays"]

    # Unit header variants: arabic, roman numerals, punctuation, module keyword
    blob = (
        "Unit 1 Intro - Basics "
        "Unit-II Advanced - Practice "
        "Module: 3 Design - Lab "
        "Module IV Project - Viva"
    )
    parsed = parse_syllabus_text(blob)
    assert sorted(parsed.keys()) == [1, 2, 3, 4]

    # Java-style comma-heavy syllabus should split into usable fine-grained topics
    java_blob = (
        "Unit 1 Introduction to Java Language and Runtime Environment, JVM, Bytecode, "
        "Basic program syntax, Datatypes, Variables, Operators, Control statements,Loops,Arrays,Functions. "
        "Unit 2 Object-oriented concepts- Abstraction, Encapsulation, Inheritance and Polymorphism. "
        "Class and objects, Constructor functions, Class members and methods, Class Instance variables, "
        "Garbage collector, Method overloading. Basics of Inheritance, Types of Inheritance, Super keyword, "
        "Final keyword, overriding of methods, Applying and implementing interfaces, Packages-create, "
        "access and importing packages. Introduction to UML diagrams. "
        "Unit 3 Introduction to exception handling, Hierarchy of exception, Usage of try, catch, throw, "
        "throws and finally. Built- in and user defined exceptions, Threads, Creating Threads, "
        "Thread lifecycle, Concept of multithreading. "
        "Unit 4 Applets-Applet class, Delegation event model-events, event sources, event listeners, "
        "event classes, mouse and keyboard events, JLabel, JText, JButton, JList, Combo box."
    )
    java_units = parse_syllabus_text(java_blob)
    assert len(java_units[1]) >= 8
    assert "Object-oriented concepts" in java_units[2]
    assert any("Built-in" in t for t in java_units[3])
    assert "Applets" in java_units[4]


# ---------------------------------------------------------------------------
# Database I/O  (interface unchanged from previous version)
# ---------------------------------------------------------------------------

def store_syllabus(subject_name: str, units: dict[int, list[str]],
                   db_path: str = "student_helper.db") -> int:
    """
    Store parsed syllabus topics in the Syllabus_Topics table.
    Replaces any existing data for this subject (clean re-upload).

    Parameters
    ----------
    subject_name : name of the subject, e.g. "Mathematics for Intelligent Systems"
    units        : {unit_number: [ordered topic names]}
    db_path      : path to the SQLite database

    Returns
    -------
    Total number of rows inserted.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Syllabus_Topics WHERE Subject_Name = ?",
        (subject_name,)
    )

    total = 0
    for unit_num, topic_list in sorted(units.items()):
        for order, topic_name in enumerate(topic_list, start=1):
            cursor.execute(
                """INSERT OR IGNORE INTO Syllabus_Topics
                   (Subject_Name, Unit_Number, Topic_Name, Topic_Order)
                   VALUES (?, ?, ?, ?)""",
                (subject_name, unit_num, topic_name, order)
            )
            total += 1

    conn.commit()
    conn.close()
    return total


def load_syllabus_edges(db_path: str = "student_helper.db") -> list[tuple[str, str]]:
    """
    Read Syllabus_Topics and derive prerequisite edges from consecutive
    topic ordering within each unit.

    Returns
    -------
    List of (prerequisite_topic, target_topic) tuples.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Subject_Name, Unit_Number, Topic_Name
        FROM Syllabus_Topics
        ORDER BY Subject_Name, Unit_Number, Topic_Order
    """)
    rows = cursor.fetchall()
    conn.close()

    edges: list[tuple[str, str]] = []
    prev_topic = prev_subject = prev_unit = None

    for subject, unit, topic in rows:
        if subject == prev_subject and unit == prev_unit and prev_topic:
            edges.append((prev_topic, topic))
        prev_topic, prev_subject, prev_unit = topic, subject, unit

    return edges


# ---------------------------------------------------------------------------
# CLI smoke-test  —  python syllabus_parser.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _run_parser_self_tests()
    print("Parser self-tests passed.")

    samples: dict[str, str] = {
        "Mathematics for IS": (
            "Unit 1 Gaussian elimination \u2013 LU decomposition \u2013 Vector spaces associated with Matrices- "
            "Special orthogonal matrices \u2013 QR decomposition-Gram-Schmidt Orthogonalization- "
            "Fourier Series and Fourier Transform and its properties \u2013 Convolution - "
            "Projection matrix and Regression - Convolution sum - Convolution Integral - "
            "Eigenvalues and Eigenvectors of Symmetric matrices - Eigenvalues and Eigen vectors of ATA, AAT - "
            "Relationship between vector spaces associated with A, ATA, AAT- "
            "Singular Value Decomposition \u2013 Concept of Pseudoinverse- "
            "Computational experiments using MATLAB/Excel/Simulink "
            "Unit 2 Taylor series expansion of multivariate functions-conditions for maxima, minima and saddle points-"
            "Concept of gradient and Hessian matrices- Impulse Response computations- "
            "converting higher order into first order equations \u2013 concept of eAT - "
            "Newton method for unconstrained optimization- "
            "Computational experiments using MATLAB/Excel/Simulink"
        ),
        "Data Structures & Algorithms": (
            "Unit 1 Data Structure \u2013 primitive and non-primitive, Array data structure, "
            "properties and functions, single and multi- dimensional arrays, simple problems, "
            "Basics of Algorithm Analysis, big-Oh notation, notion of time and space complexity, dynamic arrays "
            "Unit 4 Binary Tree\u2013 arrays and linked list representation, tree traversals-"
            "preorder, postorder, inorder, level order. Graphs- directed and undirected graphs, "
            "adjacency list and matrices, Shortest path- Dijkstra's algorithm, "
            "BellmanFord algorithm, Floyd-Warshall algorithm"
        ),
        "Communication Systems": (
            "Unit 2 Need for modulation, analog modulation schemes, amplitude modulation (AM) and its types "
            "- AMDSB-SC, AM- DSB-TC, SSB. AM Demodulation schemes, angle modulation- "
            "frequency modulation (FM) -Narrowband and wideband, phase modulation, FM demodulation"
        ),
        "Robotics": (
            "Unit 1 Definition and History of Robots, Applications of robots, Current trend in robotics, "
            "Basic mathematics for robotics \u2013 Vectors, Matrices and Linear Algebra concepts, "
            "Rigid body transformations \u2013 Translation and Rotation, Homogeneous Transformation matrix. "
            "Unit 3 Introduction to rigid body kinetics, Euler-Lagrange equation of simple robotic systems, "
            "Forward and Inverse dynamics of simple robotic systems, Reactive control using PID controller, "
            "Velocity based control of simple robotic systems, Torque based control of robotic systems."
        ),
        "Java Programming": (
            "Unit 2 Object-oriented concepts- Abstraction, Encapsulation, Inheritance and Polymorphism. "
            "Class and objects, Constructor functions, Class members and methods, Class Instance variables, "
            "Garbage collector, Method overloading. Basics of Inheritance, Types of Inheritance, "
            "Super keyword, Final keyword, overriding of methods, Applying and implementing interfaces, "
            "Packages-create, access and importing packages. Introduction to UML diagrams."
        ),
    }

    for subject, raw in samples.items():
        print(f"\n{'=' * 64}")
        print(f"  {subject}")
        print(f"{'=' * 64}")
        parsed = parse_syllabus_text(raw)
        for unit_num, topics in parsed.items():
            print(f"\n  Unit {unit_num}  ({len(topics)} topics)")
            for i, t in enumerate(topics, 1):
                print(f"    {i:>2}. {t}")