from typing import Union


class ProgressBar:
    """
    A class to create a simple progress bar.

    Args:
        total (int, float): Total number of iterations.

    Raises:
        ValueError: The value given is not numeric.
    """

    def __init__(self, total: Union[int, float]) -> None:
        self.total = self.__validate_total(total)
        self.__progress = 0
        self.__bar_length = 40
        self.__pct_completed = 0

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
            self.__pct_completed = n / self.total * 100
            self.__draw()
        else:
            raise ValueError("'n' must be int or float.")

    def __draw(self) -> None:
        """Prints the progress bar"""
        self.__block = int(self.__bar_length * self.__pct_completed / 100)

        if self.__block == 0:
            self.__progress = " " * self.__bar_length
        elif self.__block == self.__bar_length:
            self.__progress = "-" * self.__block
        else:
            self.__progress = (
                "-" * self.__block + ">" + " " * (self.__bar_length - self.__block - 1)
            )

        print(
            f"\rDownloading... |{self.__progress}| {self.__pct_completed:.2f}% completed",
            end="",
            flush=True,
        )
