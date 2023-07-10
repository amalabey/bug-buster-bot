import os


def add_line_numbers(original_text: str) -> str:
    lines = original_text.splitlines()
    updated_lines = list()
    for line_number, line in enumerate(lines, start=1):
        line_with_number = f"{line_number} {line}"
        updated_lines.append(line_with_number)
    return "\n".join(updated_lines)


def detect_lang(file_name: str) -> str:
    lang_map = {
        ".cs": "C#",
        ".kt": "Kotlin",
        ".py": "Python",
        ".ps1": "PowerShell"
    }
    _, extension = os.path.splitext(file_name)
    return lang_map[extension.lower()]
