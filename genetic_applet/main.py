import os
import sys

sys.path.append(os.path.join("..", ".."))

from genetic_applet import applet


def main():
    applet.run()


if __name__ == '__main__':
    main()
