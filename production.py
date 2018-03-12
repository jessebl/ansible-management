#!/usr/bin/env python
import freeipa

group = 'production'

if __name__ == '__main__':
    freeipa.filter_main(group)
