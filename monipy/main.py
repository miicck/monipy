import argparse
import curses
import math
import time


def divide_span(size: int, divisions: int):
    result = [size // divisions] * divisions
    result[-1] += size - sum(result)
    assert sum(result) == size
    assert len(result) == divisions
    return result


class Monipy:
    WINDOW_TITLE = 1
    WINDOW_CONTENT = 2

    def __init__(self, args: argparse.Namespace):

        # Get number of windows
        self.N = math.ceil(len(args.files) ** 0.5)

        # Persistent variables
        self.last_height, self.last_width = -1, -1
        self.windows = []
        self.margins = []

        # Save arguments
        self.args = args

    def _update(self, stdscr: curses.window):

        height, width = stdscr.getmaxyx()

        # Check for screen re-size
        if height != self.last_height or width != self.last_width:
            self.last_height, self.last_width = height, width

            # Widths and heights of windows
            widths = divide_span(width, self.N)
            heights = divide_span(height, self.N)

            # Split screen into those windows
            self.windows = []
            self.margins = []
            for i, w in enumerate(widths):
                for j, h in enumerate(heights):
                    x = sum(widths[:i])
                    y = sum(heights[:j])
                    self.windows.append(curses.newwin(h, w, y, x))
                    self.margins.append((
                        self.args.padding_x if i < self.N - 1 else 0,
                        self.args.padding_y if j < self.N - 1 else 0
                    ))

        for f, window, (margin_x, margin_y) in zip(self.args.files, self.windows, self.margins):
            window: curses.window

            # Get size of window, content
            w_height, w_width = window.getmaxyx()
            c_height, c_width = w_height - margin_y, w_width - margin_x

            # Grab content from file
            lines = [f]  # File name is first line
            with open(f, "r") as fo:
                lines.extend(fo.readlines()[-(c_height - 1):])
            lines.extend([""] * (w_height - len(lines)))
            assert len(lines) == w_height

            # Truncate/pad lines to width
            lines = [l.replace("\n", "")[:c_width] for l in lines]
            lines = [l + " " * (c_width - len(l)) for l in lines]

            # Write lines to window
            for i, line in enumerate(lines):
                assert len(line) <= w_width
                window.insstr(i, 0, line, curses.color_pair(self.WINDOW_TITLE if i == 0 else self.WINDOW_CONTENT))

                # Draw the margin
                if margin_x > 0:
                    window.insstr(i, len(line), " " * margin_x, curses.color_pair(self.WINDOW_CONTENT))

            # Refresh content
            window.refresh()

        # Hide cursor
        curses.curs_set(0)

        # Refresh whole window
        stdscr.refresh()

    def update_loop(self, stdscr: curses.window):

        # Define colors
        curses.init_pair(self.WINDOW_TITLE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(self.WINDOW_CONTENT, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Ensure updated immediately
        self._update(stdscr)

        # Update loop
        while True:
            self._update(stdscr)
            time.sleep(self.args.refresh)


def main():
    parser = argparse.ArgumentParser()

    # Set up command line arguments
    parser.add_argument("files", nargs="+")
    parser.add_argument("-px", "--padding_x", default=1, type=int)
    parser.add_argument("-py", "--padding_y", default=0, type=int)
    parser.add_argument("-r", "--refresh", default=0.1, type=float)

    # Parse command line arguments
    args = parser.parse_args()

    # Ensure valid
    args.padding_x = max(0, args.padding_x)
    args.padding_y = max(0, args.padding_y)

    curses.wrapper(Monipy(args).update_loop)


if __name__ == "__main__":
    main()
