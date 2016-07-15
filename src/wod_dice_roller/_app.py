__version__ = "0.1"

if __debug__:
   import sys
   import traceback

from kivy.app import App
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
import kivy
import os.path

# Add the 'ui' directory to the resource path before import the UI components.
# From: https://github.com/kivy/kivy/issues/4458
KV_PATH = os.path.abspath( os.path.join( os.path.dirname( __file__ ), 'ui' ) )
resource_add_path( KV_PATH )

if kivy.platform == "android": # :KLUDGE p4a appears to mishandle relative imports
   from ui.roll_screen import RollScreen
else:
   from .ui.roll_screen import RollScreen

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
