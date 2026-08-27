from flask import Flask, render_template, request, jsonify
import language_tool_python
import re

app = Flask(__name__)

# Initialize LanguageTool grammar engine
tool = language_tool_python.LanguageTool('en-US')

# ─── RULES TO ALWAYS IGNORE ───────────────────────────────────
# These LanguageTool rule IDs cause too many false positives.
# We disable them so correct sentences are not flagged wrongly.
DISABLED_RULES = {
    'MORFOLOGIK_RULE_EN_US',   # Flags proper nouns (Hyderabad, Telangana, etc.) as spelling errors
    'EN_QUOTES',               # Flags quote style differences — not real errors
    'WHITESPACE_RULE',         # Flags extra spaces — too strict for casual use
    'COMMA_PARENTHESIS_WHITESPACE',  # Minor punctuation style — not a real mistake
    'DOUBLE_PUNCTUATION',      # Sometimes flags intentional punctuation
    'EN_UNPAIRED_BRACKETS',    # Flags unmatched brackets — false positives in casual text
}

# ─── WORDS THAT SHOULD NEVER BE FLAGGED ───────────────────────
# Add any proper nouns, brand names, or technical words here.
# Even with MORFOLOGIK disabled, some words may still be caught
# by other rules — this whitelist is the final safety net.
WHITELISTED_WORDS = {
    # Indian cities & states
    'Hyderabad', 'Telangana', 'Mumbai', 'Chennai', 'Bengaluru',
    'Kolkata', 'Delhi', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow',
    'Andhra', 'Pradesh', 'Karnataka', 'Maharashtra', 'Gujarat',
    # Common proper nouns that get false-flagged
    'Google', 'YouTube', 'WhatsApp', 'Instagram', 'LinkedIn',
    'Python', 'Flask', 'JavaScript', 'HTML', 'CSS', 'API',
    # Add your own words below this line:
}


def is_false_positive(match, text):
    """
    Returns True if this match is a false positive that we should ignore.

    A false positive = LanguageTool says it's an error, but it is actually correct.

    We check three things:
    1. Is this rule in our disabled rules list?
    2. Is the flagged word in our whitelist?
    3. Is the flagged word a Capitalized word (likely a proper noun)?
    """

    # Check 1: Is this a rule we always want to ignore?
    if match.ruleId in DISABLED_RULES:
        return True

    # Check 2 & 3: Look at the actual word that was flagged
    flagged_word = text[match.offset: match.offset + match.errorLength].strip()

    # Check 2: Is the word in our custom whitelist?
    if flagged_word in WHITELISTED_WORDS:
        return True

    # Check 3: Is it a Capitalized word that is NOT at the start of a sentence?
    # Words like "Hyderabad", "Python", "Amazon" are proper nouns — they start with capital
    # We check: is the character before this word a space or punctuation (not start of sentence)?
    if flagged_word and flagged_word[0].isupper():
        # Find position before the flagged word
        pos_before = match.offset - 1
        if pos_before > 0:
            char_before = text[pos_before]
            # If the word is in the middle of a sentence (preceded by space),
            # and it starts with a capital, it's very likely a proper noun
            if char_before == ' ':
                # Only skip if LanguageTool's category is a spelling/typo category
                # (we don't want to skip real grammar issues for capitalized words)
                if 'TYPOS' in match.category.upper() or 'SPELL' in match.category.upper():
                    return True

    return False


@app.route('/')
def index():
    """Serve the homepage."""
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_grammar():
    """
    Receives text, checks grammar, filters false positives, returns results.
    """
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'Please enter some text to check.'}), 400

    # Step 1: Get ALL matches from LanguageTool
    all_matches = tool.check(text)

    # Step 2: Filter out false positives — keep only real errors
    real_matches = [m for m in all_matches if not is_false_positive(m, text)]

    # Step 3: Build issues list from real matches only
    issues = []
    for match in real_matches:
        issue = {
            'message':      match.message,
            'offset':       match.offset,
            'length':       match.errorLength,
            'replacements': match.replacements[:5],
            'rule_id':      match.ruleId,
            'category':     match.category,
            'context':      match.context,
        }
        issues.append(issue)

    # Step 4: Auto-correct using only real matches (not false positives)
    corrected_text = language_tool_python.utils.correct(text, real_matches)

    # Step 5: Count error types
    grammar_count  = sum(1 for m in real_matches if 'GRAMMAR' in m.category.upper())
    spelling_count = sum(1 for m in real_matches if 'TYPOS'   in m.category.upper() or 'SPELL' in m.category.upper())
    style_count    = len(real_matches) - grammar_count - spelling_count

    # Step 6: Calculate writing score (100 = perfect, 0 = many errors)
    words  = len(text.split())
    errors = len(real_matches)

    if words == 0:
        score = 100
    else:
        deduction = min(100, (errors / max(words, 1)) * 200)
        score = max(0, round(100 - deduction))

    return jsonify({
        'original':  text,
        'corrected': corrected_text,
        'issues':    issues,
        'stats': {
            'total_errors':   errors,
            'grammar_errors': grammar_count,
            'spelling_errors':spelling_count,
            'style_errors':   style_count,
            'word_count':     words,
            'score':          score
        }
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Grammar Tool is running!'})


if __name__ == '__main__':
    print("=" * 50)
    print("  Grammar Correction Tool is starting...")
    print("  Open your browser and go to:")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)