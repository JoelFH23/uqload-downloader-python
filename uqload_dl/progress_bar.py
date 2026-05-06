from typing import Union
import sys


# ANSI color codes for better UI
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ProgressBar:
    """
    A class to create a modern, colorful progress bar.

    Args:
        total (int, float): Total number of iterations.

    Raises:
        ValueError: The value given is not numeric.
    """

    def __init__(self, total: Union[int, float]) -> None:
        self.total = self.__validate_total(total)
        self.__progress = 0
        self.__bar_length = 50
        self.__pct_completed = 0
        self.__downloaded = 0
        self.__speed = 0
        self.__eta = 0

    def __validate_total(self, total) -> Union[int, float]:
        """
        Validates that it is only a numeric value.

        Returns:
            total (int, float): Total number of iterations.

        Raises:
            ValueError: The value given is not numeric.
        """
        if type(total) is int or type(total) is float:
            return total
        raise ValueError("total must be int or float.")

    @property
    def get_pct_completed(self) -> Union[int, float]:
        """Returns the percentage completed."""
        return self.__pct_completed

    def update(self, n: Union[int, float] = 1) -> None:
        """
        Updates the progress bar.

        Args:
            n (int, float): Increases the progress bar by "n".

        Raises:
            ValueError: if "n" is not int or float.
        """
        if type(n) is int or type(n) is float:
            self.__downloaded = n
            self.__pct_completed = n / self.total * 100
            self.__draw()
        else:
            raise ValueError("'n' must be int or float.")

    def __draw(self) -> None:
        """Prints the modern progress bar with colors and formatting"""
        self.__block = int(self.__bar_length * self.__pct_completed / 100)

        # Create the progress bar
        if self.__block == 0:
            self.__progress = " " * self.__bar_length
        elif self.__block == self.__bar_length:
            self.__progress = "█" * self.__block
        else:
            self.__progress = "█" * self.__block + "░" * (self.__bar_length - self.__block)

        # Format file sizes
        downloaded_str = self.__format_size(self.__downloaded)
        total_str = self.__format_size(self.total)

        # Choose color based on progress
        if self.__pct_completed < 25:
            color = Colors.FAIL
            emoji = "🔄"
        elif self.__pct_completed < 75:
            color = Colors.WARNING
            emoji = "⚡"
        else:
            color = Colors.OKGREEN
            emoji = "🚀"

        # Calculate speed (MB/s)
        if hasattr(self, '_last_time') and hasattr(self, '_last_bytes'):
            import time
            current_time = time.time()
            time_diff = current_time - self._last_time
            if time_diff > 0:
                bytes_diff = self.__downloaded - self._last_bytes
                speed_mbps = (bytes_diff / (1024 * 1024)) / time_diff
                speed_str = f" {speed_mbps:.1f}MB/s"
            else:
                speed_str = ""
            self._last_time = current_time
            self._last_bytes = self.__downloaded
        else:
            import time
            self._last_time = time.time()
            self._last_bytes = self.__downloaded
            speed_str = ""

        # Create the progress display
        progress_text = (
            f"\r{emoji} {color}{self.__progress}{Colors.ENDC} "
            f"{Colors.BOLD}{self.__pct_completed:.1f}%{Colors.ENDC} "
            f"({downloaded_str}/{total_str}){speed_str}"
        )

        # Clear line and print
        sys.stdout.write("\033[K")  # Clear the line
        sys.stdout.write(progress_text)
        sys.stdout.flush()

    def __format_size(self, size_bytes: Union[int, float]) -> str:
        """Format bytes into human readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"

    def finish(self) -> None:
        """Mark the progress as complete."""
        self.__pct_completed = 100
        self.__downloaded = self.total
        self.__draw()
        print()  # New line after completion
