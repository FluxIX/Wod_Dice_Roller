class WodDiceRollResult( object ):
   def __init__( self, roll_properties, rolls, net_successes, unresolved_botches, botches, failures, successes, aces, **kwargs ):
      self._set_roll_properties( roll_properties )
      self._set_rolls( rolls )
      self._set_net_successes( net_successes )
      self._set_unresolved_botches( unresolved_botches )
      self._set_botches( botches )
      self._set_failures( failures )
      self._set_successes( successes )
      self._set_aces( aces )

   def _set_roll_properties( self, value ):
      self._roll_properties = value

   def get_roll_properties( self ):
      return self._roll_properties

   roll_properties = property( fget = get_roll_properties )

   def _set_rolls( self, value ):
      self._rolls = value

   def get_rolls( self, **kwargs ):
      sort = kwargs.get( "sort", False )
      reverse_sort = kwargs.get( "reverse", False )
      flatten_rolls = kwargs.get( "flatten", True )
      read_only = kwargs.get( "read_only", False )

      if flatten_rolls:
         result = []

         for item in self._rolls:
            result.extend( item )
      else:
         if read_only:
            result = self._rolls
         else:
            result = [ item[:] for item in self._rolls ]

      if sort:
         if flatten_rolls:
            result = sorted( result, reverse = reverse_sort )
         else:
            result = [ sorted( item, reverse = reverse_sort ) for item in result ]

      return result

   rolls = property( fget = get_rolls )

   def get_sorted_rolls( self, reverse = True, **kwargs ):
      return self.get_rolls( sort = True, reverse = reverse, **kwargs )

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
