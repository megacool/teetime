#!/usr/bin/env python

import teetime
import os


def main():
    with open('samples/sample-texts.txt') as fh:
        for line in fh:
            print line.strip()
            path = teetime.create_typography(line.strip(), colors=False)
            os.rename(path, os.path.join('samples', os.path.basename(path)))


if __name__ == '__main__':
    main()
