"""P03 entry point. Run: python hotel_booking.py [--race]"""

import sys

from hotel_booking.demo import run_demo, run_race


if __name__ == "__main__":
    run_race() if "--race" in sys.argv else run_demo()
