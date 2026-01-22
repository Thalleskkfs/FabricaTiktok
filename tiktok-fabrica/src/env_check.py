from __future__ import annotations

import sys


def _report_import(module_name: str) -> None:
    try:
        module = __import__(module_name, fromlist=["*"])
    except Exception as exc:
        print(f"{module_name}: FAILED ({exc})")
        return

    print(f"{module_name}: OK")
    if module_name == "moviepy":
        print(f"moviepy.__file__: {getattr(module, '__file__', 'unknown')}")


def main() -> None:
    print(f"Python executable: {sys.executable}")
    print("sys.path:")
    for path in sys.path:
        print(f"  {path}")

    print("\nImport checks:")
    _report_import("moviepy")
    _report_import("moviepy.editor")
    _report_import("pyttsx3")
    _report_import("yaml")


if __name__ == "__main__":
    main()
