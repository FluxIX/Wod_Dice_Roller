from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from ..dice_roller.custom_dice_roller import CustomWodDiceRoller
from ..dice_roller.wod_dice_roller import WodDiceConstants
from ..utils.kivy.version import get_version

Builder.load_file( "roll_screen.kv" )

class _ResultColors:
   ItemSeparator = "ffffff"

   RollBotch = "ff0000"
   RollFailure = "fff000"
   RollSuccess = "ffffff"
   RollAce_Suppressed = "00ff00"
   RollAce_Unsuppressed = "0000ff"

   ResultBotch = "ff0000"
   ResultFailure = "fff000"
   ResultSuccess_MaxHuman = "4169E1"
   ResultSuccess_MaxSuperhuman = "9932CC"

class RollScreen( Screen ):
   _default_title = "Roll"

   def __init__( self, **kwargs ):
      kwargs.setdefault( "name", RollScreen._default_title )

      super( RollScreen, self ).__init__( **kwargs )

      self._initialize( **kwargs )

   def _initialize( self, **kwargs ):
      self._roller = CustomWodDiceRoller()

      self._dp = self.ids.dice_pool_selector
      self._tn = self.ids.target_number_selector
      self._output = self.ids.roll_result_display

      self._reset()

   def _roll_dice( self ):
      dice_pool = self._dp.selected_value
      target_number = self._tn.selected_value

      roll_result = self._roller.roll( dice_pool, target_number )

      self._output.text = self._get_roll_string( roll_result )

   def _reset( self ):
      self._dp.select_and_center( 5 )
      self._tn.select_and_center( WodDiceConstants.DefaultTargetNumber )

   def _apply_gradient( self, value, domain_size, source_color, destination_color ):
      if len( source_color ) != len( destination_color ):
         raise ValueError( "Source and destination colors must have the same length." )
      elif len( source_color ) != 3:
         raise ValueError( "Source color has an incorrect number of components ({:d}).".format( len( source_color ) ) )
      else:
         scale_factor = float( value ) / domain_size

         color_difference = [ ( destination_color[ i ] - source_color[ i ] ) for i in range( len( source_color ) ) ]

         return [ ( source_color[ i ] + scale_factor * component ) for i, component in enumerate( color_difference ) ]

   def _to_hex_color( self, kivy_color ):
      result = ""

      for element in kivy_color:
         value = int( round( element ) )

         if value > 255:
            value = 255

         result += "%02X" % value

      return result

   def _color_str_to_list( self, color_str ):
      if len( color_str ) != 6:
         raise ValueError( "Color string is an invalid length ({:d})".format( len( color_str ) ) )
      else:
         stride = 2
         result = [ int( color_str[ index : index + stride ], 16 ) for index in range( 0, len( color_str ), stride ) ]

         return result

   def _get_result_color( self, roll_result ):
      if roll_result < 0:
         result = _ResultColors.ResultBotch
      elif roll_result == 0:
         result = _ResultColors.ResultFailure
      else:
         human_tier_limit = 5
         superhuman_tier_limit = 10
         base_color = _ResultColors.ResultFailure
         max_human_tier_color = _ResultColors.ResultSuccess_MaxHuman
         max_superhuman_color = _ResultColors.ResultSuccess_MaxSuperhuman

         if roll_result <= human_tier_limit: # human tier
            result = self._to_hex_color( self._apply_gradient( roll_result, human_tier_limit, self._color_str_to_list( base_color ), self._color_str_to_list( max_human_tier_color ) ) )
         elif roll_result <= superhuman_tier_limit: # superhuman tier
            result = self._to_hex_color( self._apply_gradient( roll_result - human_tier_limit, superhuman_tier_limit - human_tier_limit, self._color_str_to_list( max_human_tier_color ), self._color_str_to_list( max_superhuman_color ) ) )
         else:
            result = max_superhuman_color

      return result

   def _get_dice_value_color( self, dice_value, roll_result, is_suppressed ):
      if roll_result.roll_properties.is_botch( dice_value ):
         result = _ResultColors.RollBotch
      elif roll_result.roll_properties.is_ace( dice_value ):
         if is_suppressed:
            result = _ResultColors.RollAce_Suppressed
         else:
            result = _ResultColors.RollAce_Unsuppressed
      elif roll_result.roll_properties.is_success( dice_value ):
         result = _ResultColors.RollSuccess
      else: # is a failure
         result = _ResultColors.RollFailure

      return result

   def _get_modified_indexes( self, roll_result, roll_list ):
      cancelled_botch_indexes = []
      cancelled_success_indexes = []
      suppressed_reroll_indexes = []

      botch_indexes = []
      success_indexes = []
      aces_indexes = []

      for index, roll in enumerate( roll_list ):
         if roll_result.roll_properties.is_botch( roll ):
            botch_indexes.append( index )
         elif roll_result.roll_properties.is_ace( roll ):
            aces_indexes.append( index )
         elif roll_result.roll_properties.is_success( roll ):
            success_indexes.append( index )

      ace_count = len( aces_indexes )
      success_indexes_sorted = False

      while len( botch_indexes ) > 0 and ( len( success_indexes ) > 0 or len( aces_indexes ) > 0 ):
         botch_index = botch_indexes.pop( 0 )

         cancelled_botch_indexes.append( botch_index )

         if len( suppressed_reroll_indexes ) < ace_count: # reroll is suppressed
            ace_index = aces_indexes.pop() # pop the last ace index

            suppressed_reroll_indexes.append( ace_index )
            success_indexes.append( ace_index )
         else: # A success is being cancelled
            if not success_indexes_sorted:
               success_indexes.sort( key = lambda item: roll_list[ item ] )
               success_indexes_sorted = True

            success_index = success_indexes.pop( 0 ) # pop the index to the smallest value
            cancelled_success_indexes.append( success_index )

      all_index_cancellations = cancelled_botch_indexes + cancelled_success_indexes

      return ( suppressed_reroll_indexes, all_index_cancellations )

   def _get_roll_string( self, roll_result ):
      apply_strikethough = get_version().gte_version( [ 1, 9, 2 ] ) # 1.9.2 is needed for the strike-through effect

      pieces = [ "[color={}]{:d}[/color]\n".format( self._get_result_color( roll_result.result ), roll_result.result ) ]

      roll_list = roll_result.sorted_rolls
      suppressed_reroll_indexes, index_cancellations = self._get_modified_indexes( roll_result, roll_list )
      length = len( roll_list )
      for index, roll in enumerate( roll_list ):
         piece = "[color={}]{:d}[/color]".format( self._get_dice_value_color( roll, roll_result, index in suppressed_reroll_indexes ), roll )

         if apply_strikethough and index in index_cancellations:
            piece = "[s]{}[/s]".format( piece )

         pieces.append( piece )

         if index + 1 < length:
            pieces.append( "[color={}], [/color]".format( _ResultColors.ItemSeparator ) )

      return "".join( pieces )
