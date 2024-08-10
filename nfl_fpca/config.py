import logging
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    BarColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)


def setup_logging(name, log_file):
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    file_handler = logging.FileHandler(log_file, mode='w')
    console_handler = RichHandler()

    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Formatter
    file_formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}",
                                       style="{",
                                       datefmt="%H:%M",
                                       )

    console_formatter = logging.Formatter("{levelname} - {message}",
                                          style="{",
                                          datefmt="%H:%M",
                                          )

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    return logger


def setup_progress_bar():
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn("[{task.completed}/{task.total}]"),
        TimeRemainingColumn(),
    )

    return progress
