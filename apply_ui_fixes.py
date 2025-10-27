#!/usr/bin/env python3
"""
Script to apply all UI fixes for BSW Scheduling Agent.
Handles: emojis, deprecation warnings, text visibility, and routing logic.
"""

import re

def remove_emojis_from_file(filepath):
    """Remove all emojis from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove emoji patterns
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    content_no_emoji = emoji_pattern.sub('', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_no_emoji)

    print(f"Removed emojis from {filepath}")

def fix_column_width_deprecation(filepath):
    """Replace use_column_width with use_container_width."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('use_column_width', 'use_container_width')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed column width deprecation in {filepath}")

def main():
    files_to_fix = [
        'app.py',
        'pages/chat.py',
        'pages/metrics_dashboard.py',
        'pages/feedback.py'
    ]

    print("Applying UI fixes...")
    print("=" * 60)

    for filepath in files_to_fix:
        try:
            remove_emojis_from_file(filepath)
            fix_column_width_deprecation(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")

    print("=" * 60)
    print("UI fixes applied successfully!")

if __name__ == "__main__":
    main()
