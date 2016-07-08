__version__ = "0.1"

if __debug__:
   import sys
   import traceback

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from wod_dice_roller.ui.roll_screen import RollScreen

class WodDiceRollerApp( App ):
   def build( self ):
      screens = [ RollScreen() ]

      manager = ScreenManager()

      for screen in screens:
         manager.add_widget( screen )

      return manager

def run_app( args = None ):
   result = 0

   try:
      app = WodDiceRollerApp( title = "WoD Dice Roller" )
      app.run()
   except Exception, e:
      result = 1

      print( "Top-level error caught: {}".format( e ) )

      if __debug__:
         exc_type, exc_value, exc_traceback = sys.exc_info()
         print( "".join( traceback.format_exception( exc_type, exc_value, exc_traceback ) ) )

         raise e
   finally:
      return result
