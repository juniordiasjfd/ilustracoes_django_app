import os
from django.core.management.base import BaseCommand
from django.conf import settings
import pyperclip


EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "migrations",
    "media",
    "staticfiles",
}

EXCLUDE_FILES = {
    ".DS_Store",
}


class Command(BaseCommand):
    help = "Imprime a estrutura do projeto para contextualização com IA"

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR

        estrutura = self.build_tree(base_dir)

        self.stdout.write(self.style.SUCCESS(estrutura))

    def build_tree(self, path, prefix=""):
        tree = ""

        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return ""

        for index, item in enumerate(items):
            if item in EXCLUDE_DIRS or item in EXCLUDE_FILES:
                continue

            full_path = os.path.join(path, item)

            connector = "└── " if index == len(items) - 1 else "├── "
            tree += f"{prefix}{connector}{item}\n"

            if os.path.isdir(full_path):
                extension = "    " if index == len(items) - 1 else "│   "
                tree += self.build_tree(full_path, prefix + extension)

        pyperclip.copy(tree)
        return tree