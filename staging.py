#!/usr/bin/env python
import freeipa

group = 'staging'

if __name__ == '__main__':
    freeipa.filter_main(group)
