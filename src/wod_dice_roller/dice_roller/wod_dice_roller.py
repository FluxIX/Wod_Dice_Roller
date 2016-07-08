import math

class WodDiceConstants:
   NoExplosionLimit = -1

   DefaultDiceType = 10
   DefaultDiceMinimumValue = 1
   DefaultDiceStride = 1
   DefaultDiceMaximumValue = ( DefaultDiceMinimumValue + DefaultDiceType ) * DefaultDiceStride - DefaultDiceMinimumValue

   DefaultExplosionLimit = 1
   DefaultAllowBotchOnExplosion = False

   DefaultTargetNumber = int( math.floor( ( ( DefaultDiceMinimumValue + DefaultDiceMaximumValue ) / 2 ) + DefaultDiceStride ) ) # Selects the value past 1/2 of the values
   DefaultMinimumTargetNumber = DefaultDiceMinimumValue + DefaultDiceStride
   DefaultMaximumTargetNumber = DefaultDiceMaximumValue

class WodDiceRoller( object ):
   def roll( self, dice_pool, target_number = WodDiceConstants.DefaultTargetNumber, **kwargs ):
      raise NotImplementedError( "Child must implement." )

class WodDiceRollResult( object ):
   def __init__( self, dice_type, dice_pool, target_number, dice_pool_bias, rolls, net_successes, unresolved_botches, botches, failures, successes, aces, **kwargs ):
      self._set_dice_type( dice_type )
      self._set_dice_pool( dice_pool )
      self._set_target_number( target_number )
      self._set_dice_pool_bias( dice_pool_bias )
      self._set_rolls( rolls )
      self._set_net_successes( net_successes )
      self._set_unresolved_botches( unresolved_botches )
      self._set_botches( botches )
      self._set_failures( failures )
      self._set_successes( successes )
      self._set_aces( aces )

   def _set_dice_type( self, value ):
      self._dice_type = value

   def get_dice_type( self ):
      return self._dice_type

   dice_type = property( fget = get_dice_type )

   def _set_dice_pool( self, value ):
      self._dice_pool = value

   def get_dice_pool( self ):
      return self._dice_pool

   dice_pool = property( fget = get_dice_pool )

   def _set_target_number( self, value ):
      self._target_number = value

   def get_target_number( self ):
      return self._target_number

   target_number = property( fget = get_target_number )

   def _set_dice_pool_bias( self, value ):
      self._dice_pool_bias = value

   def get_dice_pool_bias( self ):
      return self._dice_pool_bias

   dice_pool_bias = property( fget = get_dice_pool_bias )

   def _set_rolls( self, value ):
      self._rolls = value

   def get_rolls( self ):
      return self._rolls

   rolls = property( fget = get_rolls )

   def get_sorted_rolls( self, reverse = True ):
      return sorted( self.get_rolls(), reverse = reverse )

   sorted_rolls = property( fget = get_sorted_rolls )

   def _set_botches( self, value ):
      self._botches = value

   def get_botches( self ):
      return self._botches

   def _has_botches( self ):
      return self.get_botches() > 0

   botches = property( fget = get_botches )

   has_botches = property( fget = _has_botches )

   def _set_aces( self, value ):
      self._aces = value

   def get_aces( self ):
      return self._aces

   def _has_aces( self ):
      return self.get_aces() > 0

   aces = property( fget = get_aces )

   has_aces = property( fget = _has_aces )

   def _set_successes( self, value ):
      self._successes = value

   def get_successes( self ):
      return self._successes

   def _has_successes( self ):
      return self.get_successes() > 0

   successes = property( fget = get_successes )

   has_successes = property( fget = _has_successes )

   def _set_failures( self, value ):
      self._failures = value

   def get_failures( self ):
      return self._failures

   def _has_failures( self ):
      return self.get_failures() > 0

   failures = property( fget = get_failures )

   has_failures = property( fget = _has_failures )

   def _set_net_successes( self, value ):
      self._net_successes = value

   def get_net_successes( self ):
      return self._net_successes

   def _has_net_successes( self ):
      return self.get_net_successes() > 0

   net_successes = property( fget = get_net_successes )

   has_net_successes = property( fget = _has_net_successes )

   def get_is_success( self ):
      return self.has_net_successes

   is_success = property( fget = get_is_success )

   def _set_unresolved_botches( self, value ):
      self._unresolved_botches = value

   def get_unresolved_botches( self ):
      return self._unresolved_botches

   def _has_unresolved_botches( self ):
      return self.get_unresolved_botches() > 0

   unresolved_botches = property( fget = get_unresolved_botches )

   has_unresolved_botches = property( fget = _has_unresolved_botches )

   def get_is_botch( self ):
      return self.has_unresolved_botches

   is_botch = property( fget = get_is_botch )

   def get_result( self ):
      if self.is_botch:
         result = -self.unresolved_botches
      else:
         result = self.net_successes

      return result

   result = property( fget = get_result )
