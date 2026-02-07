#!/usr/bin/env python3
import os
import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

# Add the current directory to sys.path so we can import the 'review' package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from review.application import ReviewApplication

def main():
    app = ReviewApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
