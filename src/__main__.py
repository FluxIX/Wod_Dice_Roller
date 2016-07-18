import sys
from wod_dice_roller.main import main as entry_point

if __name__ == "__main__":
   sys.exit( entry_point( sys.argv[ 1 : ] ) )
