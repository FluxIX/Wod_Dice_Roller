class RollProperties( object ):
   def __init__( self, dice_properties, dice_quantity, target_number, explosion_limit, allow_botch_on_explosion, roll_normalization_bias = 0, **kwargs ):
      botch_width = kwargs.get( "botch_width", 1 )
      ace_width = kwargs.get( "ace_width", 1 )

      self._set_dice_properties( dice_properties )
      self._set_dice_quantity( dice_quantity )
      self._set_target_number( target_number )
      self._set_explosion_limit( explosion_limit )
      self._set_allow_botch_on_explosion( allow_botch_on_explosion )
      self._set_roll_normalization_bias( roll_normalization_bias )
      self._set_botch_width( botch_width )
      self._set_ace_width( ace_width )

      self._set_botch_values( None )
      self._set_ace_values( None )

   def _set_dice_properties( self, value ):
      if value is not None:
         self._dice_properties = value
      else:
         raise ValueError( "Dice properties cannot be None." )

   def get_dice_properties( self ):
      return self._dice_properties

   dice_properties = property( fget = get_dice_properties )

   def _set_dice_quantity( self, value ):
      self._dice_quantity = value

   def get_dice_quantity( self ):
      return self._dice_quantity

   dice_quantity = property( fget = get_dice_quantity )

   def _set_target_number( self, value ):
      self._target_number = value

   def get_target_number( self ):
      return self._target_number

   target_number = property( fget = get_target_number )

   def _set_roll_normalization_bias( self, value ):
      self._roll_normalization_bias = value

   def get_roll_normalization_bias( self ):
      return self._roll_normalization_bias

   roll_normalization_bias = property( fget = get_roll_normalization_bias )

   def _set_explosion_limit( self, value ):
      self._explosion_limit = value

   def get_explosion_limit( self ):
      return self._explosion_limit

   explosion_limit = property( fget = get_explosion_limit )

   def _has_explosion_limit( self ):
      return self.explosion_limit > 0

   has_explosion_limit = property( fget = _has_explosion_limit )

   def are_explosions_valid( self, rolls_made ):
      return not self.has_explosion_limit or rolls_made < self.explosion_limit

   def _set_allow_botch_on_explosion( self, value ):
      self._allow_botch_on_explosion = value

   def get_allow_botch_on_explosion( self ):
      return self._allow_botch_on_explosion

   allow_botch_on_explosion = property( fget = get_allow_botch_on_explosion )

   def _set_botch_width( self, value ):
      self._botch_width = value

   def get_botch_width( self ):
      return self._botch_width

   botch_width = property( fget = get_botch_width )

   def _is_botching_allowed( self ):
      return self.botch_width > 0

   is_botching_allowed = property( fget = _is_botching_allowed )

   def _set_ace_width( self, value ):
      self._ace_width = value

   def get_ace_width( self ):
      return self._ace_width

   ace_width = property( fget = get_ace_width )

   def _is_acing_allowed( self ):
      return self.ace_width > 0

   is_acing_allowed = property( fget = _is_acing_allowed )

   def _set_botch_values( self, value ):
      self._botch_values = value

   def get_botch_values( self ):
      """
      Note: Assumes botches are the lower end of the sorted value set.
      """

      if self._botch_values is None:
         if self.is_botching_allowed:
            result = self.dice_properties.get_values( sort = True )[ : self.botch_width ]
         else:
            result = []

         self._botch_values = result

      return self._botch_values

   botch_values = property( fget = get_botch_values )

   def _set_ace_values( self, value ):
      self._ace_values = value

   def get_ace_values( self ):
      """
      Note: Assumes aces are the upper end of the sorted value set.
      """

      if self._ace_values is None:
         if self.is_acing_allowed:
            result = self.dice_properties.get_values( sort = True )[ -self.ace_width : ]
         else:
            result = []

         self._ace_values = result

      return self._ace_values

   ace_values = property( fget = get_ace_values )

   def is_botch( self, roll_value, **kwargs ):
      return roll_value in self.botch_values

   def is_ace( self, roll_value, **kwargs ):
      return roll_value in self.ace_values

   def is_success( self, roll_value, **kwargs ):
      include_aces = kwargs.get( "include_aces", False )

      return roll_value >= self.target_number and ( include_aces or not self.is_ace( roll_value, **kwargs ) )

   def is_failure( self, roll_value, **kwargs ):
      include_botches = kwargs.get( "include_botches", False )

      return not self.is_success( roll_value, include_aces = True ) and ( include_botches or not self.is_botch( roll_value, **kwargs ) )
