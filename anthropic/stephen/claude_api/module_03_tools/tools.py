import os
import shutil
from datetime import datetime, timedelta
from anthropic.types import ToolParam
from typing import Optional, List


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format is required")

    return datetime.now().strftime(date_format)


def add_duration_to_datetime(
    datetime_str, duration=0, unit="days", input_format="%Y-%m-%d"
):
    date = datetime.strptime(datetime_str, input_format)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)
    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)
    elif unit == "hours":
        new_date = date + timedelta(hours=duration)
    elif unit == "days":
        new_date = date + timedelta(days=duration)
    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)
    elif unit == "months":
        month = date.month + duration
        year = date.year + month // 12
        month = month % 12
        if month == 0:
            month = 12
            year -= 1
        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        new_date = date.replace(year=year, month=month, day=day)
    elif unit == "years":
        new_date = date.replace(year=date.year + duration)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")


def set_reminder(content, timestamp):
    print(f"----\nSetting the following reminder for {timestamp}:\n{content}\n----")


def save_article(**kwargs):
    return "Article saved!"


class TextEditorTool:
    def __init__(self, base_dir: str = "", backup_dir: str = ""):
        # Resolve relative paths from this module_03_tools directory by default.
        self.base_dir = os.path.abspath(base_dir or os.path.dirname(__file__))
        self.backup_dir = backup_dir or os.path.join(self.base_dir, ".backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def _validate_path(self, file_path: str) -> str:
        abs_path = os.path.normpath(os.path.join(self.base_dir, file_path))
        if not abs_path.startswith(self.base_dir):
            raise ValueError(
                f"Access denied: Path '{file_path}' is outside the allowed directory"
            )
        return abs_path

    def _backup_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return ""
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(
            self.backup_dir, f"{file_name}.{os.path.getmtime(file_path):.0f}"
        )
        shutil.copy2(file_path, backup_path)
        return backup_path

    def _restore_backup(self, file_path: str) -> str:
        file_name = os.path.basename(file_path)
        backups = [
            f for f in os.listdir(self.backup_dir) if f.startswith(file_name + ".")
        ]
        if not backups:
            raise FileNotFoundError(f"No backups found for {file_path}")

        latest_backup = sorted(backups, reverse=True)[0]
        backup_path = os.path.join(self.backup_dir, latest_backup)

        shutil.copy2(backup_path, file_path)
        return f"Successfully restored {file_path} from backup"

    def _count_matches(self, content: str, old_str: str) -> int:
        return content.count(old_str)

    def view(self, file_path: str, view_range: Optional[List[int]] = None) -> str:
        try:
            abs_path = self._validate_path(file_path)

            if os.path.isdir(abs_path):
                try:
                    return "\n".join(os.listdir(abs_path))
                except PermissionError:
                    raise PermissionError(
                        "Permission denied. Cannot list directory contents."
                    )

            if not os.path.exists(abs_path):
                raise FileNotFoundError("File not found")

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            if view_range:
                start, end = view_range
                lines = content.split("\n")

                if end == -1:
                    end = len(lines)

                selected_lines = lines[start - 1 : end]

                result = []
                for i, line in enumerate(selected_lines, start):
                    result.append(f"{i}: {line}")

                return "\n".join(result)
            else:
                lines = content.split("\n")
                result = []
                for i, line in enumerate(lines, 1):
                    result.append(f"{i}: {line}")

                return "\n".join(result)

        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                "utf-8",
                b"",
                0,
                1,
                "File contains non-text content and cannot be displayed.",
            )
        except ValueError as e:
            raise ValueError(str(e))
        except PermissionError:
            raise PermissionError("Permission denied. Cannot access file.")
        except Exception as e:
            raise type(e)(str(e))

    def str_replace(self, file_path: str, old_str: str, new_str: str) -> str:
        try:
            abs_path = self._validate_path(file_path)

            if not os.path.exists(abs_path):
                raise FileNotFoundError("File not found")

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            match_count = self._count_matches(content, old_str)

            if match_count == 0:
                raise ValueError(
                    "No match found for replacement. Please check your text and try again."
                )
            elif match_count > 1:
                raise ValueError(
                    f"Found {match_count} matches for replacement text. Please provide more context to make a unique match."
                )

            # Create backup before modifying
            self._backup_file(abs_path)

            # Perform the replacement
            new_content = content.replace(old_str, new_str)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return "Successfully replaced text at exactly one location."

        except ValueError as e:
            raise ValueError(str(e))
        except PermissionError:
            raise PermissionError("Permission denied. Cannot modify file.")
        except Exception as e:
            raise type(e)(str(e))

    def create(self, file_path: str, file_text: str) -> str:
        try:
            abs_path = self._validate_path(file_path)

            # Check if file already exists
            if os.path.exists(abs_path):
                raise FileExistsError(
                    "File already exists. Use str_replace to modify it."
                )

            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            # Create the file
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(file_text)

            return f"Successfully created {file_path}"

        except ValueError as e:
            raise ValueError(str(e))
        except PermissionError:
            raise PermissionError("Permission denied. Cannot create file.")
        except Exception as e:
            raise type(e)(str(e))

    def insert(self, file_path: str, insert_line: int, new_str: str) -> str:
        try:
            abs_path = self._validate_path(file_path)

            if not os.path.exists(abs_path):
                raise FileNotFoundError("File not found")

            # Create backup before modifying
            self._backup_file(abs_path)

            with open(abs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Handle line endings
            if lines and not lines[-1].endswith("\n"):
                new_str = "\n" + new_str

            # Insert at the beginning if insert_line is 0
            if insert_line == 0:
                lines.insert(0, new_str + "\n")
            # Insert after the specified line
            elif insert_line > 0 and insert_line <= len(lines):
                lines.insert(insert_line, new_str + "\n")
            else:
                raise IndexError(
                    f"Line number {insert_line} is out of range. File has {len(lines)} lines."
                )

            with open(abs_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            return f"Successfully inserted text after line {insert_line}"

        except ValueError as e:
            raise ValueError(str(e))
        except PermissionError:
            raise PermissionError("Permission denied. Cannot modify file.")
        except Exception as e:
            raise type(e)(str(e))

    def undo_edit(self, file_path: str) -> str:
        try:
            abs_path = self._validate_path(file_path)

            if not os.path.exists(abs_path):
                raise FileNotFoundError("File not found")

            return self._restore_backup(abs_path)

        except ValueError as e:
            raise ValueError(str(e))
        except FileNotFoundError:
            raise FileNotFoundError("No previous edits to undo")
        except PermissionError:
            raise PermissionError("Permission denied. Cannot restore file.")
        except Exception as e:
            raise type(e)(str(e))


get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": "Retrieves the current date and time, formatted according to the specified format string. Returns a string representation of the current datetime. Use this tool when the user asks for the current date, time, or both. The format parameter accepts Python strftime directives (e.g., '%Y' for four-digit year, '%m' for month, '%d' for day, '%H' for hour, '%M' for minute, '%S' for second). If no format is provided, defaults to 'YYYY-MM-DD HH:MM:SS'. This tool does not accept an empty string for the format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "A Python strftime format string that controls the output format of the datetime. For example, '%Y-%m-%d' returns '2026-03-28', '%H:%M' returns '14:30', and '%B %d, %Y' returns 'March 28, 2026'. Defaults to '%Y-%m-%d %H:%M:%S' if not provided. Must not be an empty string.",
                }
            },
            "required": [],
        },
    }
)

add_duration_to_datetime_schema = {
    "name": "add_duration_to_datetime",
    "description": "Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format. This tool converts an input datetime string to a Python datetime object, adds the specified duration in the requested unit, and returns a formatted string of the resulting datetime. It handles various time units including seconds, minutes, hours, days, weeks, months, and years, with special handling for month and year calculations to account for varying month lengths and leap years. The output is always returned in a detailed format that includes the day of the week, month name, day, year, and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "The input datetime string to which the duration will be added. This should be formatted according to the input_format parameter.",
            },
            "duration": {
                "type": "number",
                "description": "The amount of time to add to the datetime. Can be positive (for future dates) or negative (for past dates). Defaults to 0.",
            },
            "unit": {
                "type": "string",
                "description": "The unit of time for the duration. Must be one of: 'seconds', 'minutes', 'hours', 'days', 'weeks', 'months', or 'years'. Defaults to 'days'.",
            },
            "input_format": {
                "type": "string",
                "description": "The format string for parsing the input datetime_str, using Python's strptime format codes. For example, '%Y-%m-%d' for ISO format dates like '2025-04-03'. Defaults to '%Y-%m-%d'.",
            },
        },
        "required": ["datetime_str"],
    },
}

set_reminder_schema = {
    "name": "set_reminder",
    "description": "Creates a timed reminder that will notify the user at the specified time with the provided content. This tool schedules a notification to be delivered to the user at the exact timestamp provided. It should be used when a user wants to be reminded about something specific at a future point in time. The reminder system will store the content and timestamp, then trigger a notification through the user's preferred notification channels (mobile alerts, email, etc.) when the specified time arrives. Reminders are persisted even if the application is closed or the device is restarted. Users can rely on this function for important time-sensitive notifications such as meetings, tasks, medication schedules, or any other time-bound activities.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The message text that will be displayed in the reminder notification. This should contain the specific information the user wants to be reminded about, such as 'Take medication', 'Join video call with team', or 'Pay utility bills'.",
            },
            "timestamp": {
                "type": "string",
                "description": "The exact date and time when the reminder should be triggered, formatted as an ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS) or a Unix timestamp. The system handles all timezone processing internally, ensuring reminders are triggered at the correct time regardless of where the user is located. Users can simply specify the desired time without worrying about timezone configurations.",
            },
        },
        "required": ["content", "timestamp"],
    },
}

save_article_schema = ToolParam(
    {
        "name": "save_article",
        "description": "Saves a scholarly journal article",
        "input_schema": {
            "type": "object",
            "properties": {
                "abstract": {
                    "type": "string",
                    "description": "Abstract of the article. One short sentence max",
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "word_count": {
                            "type": "integer",
                            "description": "Word count",
                        },
                        "review": {
                            "type": "string",
                            "description": "Eight sentence review of the paper",
                        },
                    },
                    "required": ["word_count", "review"],
                },
            },
            "required": ["abstract", "meta"],
        },
    }
)

batch_tool_schema = {
    "name": "batch_tool",
    "description": "Invoke multiple other tool calls simultaneously",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": "The tool calls to invoke",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the tool to invoke",
                        },
                        "arguments": {
                            "type": "string",
                            "description": "The arguments to the tool, encoded as a JSON string",
                        },
                    },
                    "required": ["name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
}

article_summary_schema = {
    "name": "article_summary",
    "description": "Creates a summary of an article with its key insights. Use this tool when you need to generate a structured summary of an article, research paper, or any textual content. The tool requires the article's title, author name, and a list of the most important insights or takeaways from the content. Each insight should be a concise statement capturing a significant point from the article.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the article being summarized.",
            },
            "author": {
                "type": "string",
                "description": "The name of the author who wrote the article.",
            },
            "key_insights": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of the most important takeaways or insights from the article. Each insight should be a complete, concise statement.",
            },
        },
        "required": ["title", "author", "key_insights"],
    },
}

get_text_edit_schema = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
}
