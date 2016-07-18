class DiceRollValueCategoryFlags:
   # Flags
   Base = 0x0
   Type = 0x1
   Special = 0x2
   Cancelled = 0x4
   Suppressed = 0x8

   # Values
   Failure = 0x0
   Success = 0x1

   Botch = Failure | Special
   Ace = Success | Special
   SuppressedAce = Ace | Suppressed
   CancelledBotch = Botch | Cancelled
   CancelledSuccess = Success | Cancelled
   CancelledAce = SuppressedAce | Cancelled

class DiceRollValueCategory( object ):
   def __init__( self, value, **kwargs ):
      self._set_value( value )

   def _set_value( self, value ):
      self._value = value

   def get_value( self ):
      return self._value

   value = property( fget = get_value )

   def get_roll_type( self ):
      return self.value & DiceRollValueCategoryFlags.Type

   roll_type = property( fget = get_roll_type )

   def get_is_success( self ):
      return self.roll_type == DiceRollValueCategoryFlags.Success

   is_success = property( fget = get_is_success )

   def get_is_failure( self ):
      return not self.get_is_success()

   is_failure = property( fget = get_is_failure )

   def has_flag( self, flag, **kwargs ):
      flag_is_set = kwargs.get( "is_set", True )

      if flag_is_set:
         result = ( self.value & flag ) != DiceRollValueCategoryFlags.Base
      else:
         result = ( self.value & flag ) == DiceRollValueCategoryFlags.Base

      return result

   def get_is_special( self, **kwargs ):
      return self.has_flag( DiceRollValueCategoryFlags.Special, **kwargs )

   is_special = property( fget = get_is_special )

   def get_is_cancelled( self, **kwargs ):
      return self.has_flag( DiceRollValueCategoryFlags.Cancelled, **kwargs )

   is_cancelled = property( fget = get_is_cancelled )

   def get_is_suppressed( self, **kwargs ):
      return self.has_flag( DiceRollValueCategoryFlags.Suppressed, **kwargs )

   is_suppressed = property( fget = get_is_suppressed )

   def get_is_ace( self ):
      return self.is_success and self.is_special

   is_ace = property( fget = get_is_ace )

   def get_is_botch( self ):
      return self.is_failure and self.is_special

   is_botch = property( fget = get_is_botch )

   def _get_compare_value( self ):
      if self.is_failure and self.is_special: # is botch
         if not self.is_suppressed:
            result = 0
         else:
            result = 1
      elif self.is_failure and not self.is_special: # is failure
         result = 2
      elif self.is_success and not self.is_special: # is success
         if self.is_suppressed:
            result = 3
         else:
            result = 4
      else: # if self.is_success and self.is_special: # is ace
         if self.is_suppressed:
            if self.is_cancelled:
               result = 5
            else: # if not self.is_cancelled:
               result = 6
         else:
            if self.is_cancelled:
               result = 7
            else: # if not self.is_cancelled:
               result = 8

      return result

   def __cmp__( self, other ):
      this_compare_value = self._get_compare_value()
      other_compare_value = other._get_compare_value()

      if this_compare_value < other_compare_value:
         result = -1
      elif this_compare_value > other_compare_value:
         result = 1
      else:
         result = 0

      return result

   def __str__( self ):
      if self.is_cancelled:
         cancelled = 'C'
      else:
         cancelled = 'c'

      if self.is_suppressed:
         suppressed = 'S'
      else:
         suppressed = 's'

      if self.is_special:
         special = '*'
      else:
         special = '-'

      if self.is_success:
         value = 'Success'
      else: # if self.is_failure:
         value = 'Failure'

      return "{}{} {}{}".format( cancelled, suppressed, value, special )

class CategorizedDiceRoll( object ):
   @staticmethod
   def from_raw_category( roll, raw_category ):
      return CategorizedDiceRoll( roll, DiceRollValueCategory( raw_category ) )

   def __init__( self, roll, category ):
      self._set_roll( roll )
      self._set_category( category )

   def _set_roll( self, value ):
      self._roll = value

   def get_roll( self ):
      return self._roll

   roll = property( fget = get_roll )

   def _set_category( self, value ):
      self._category = value

   def get_category( self ):
      return self._category

   category = property( fget = get_category )

   def __cmp__( self, other ):
      result = 0

      if self.category < other.category:
         result = -1
      elif self.category > other.category:
         result = 1
      else:
         if self.roll > other.roll:
            result = 1
         elif self.roll < other.roll:
            result = -1

      return result

class WodDiceRollResult( object ):
   def __init__( self, roll_properties, rolls, roll_categories, net_successes, unresolved_botches, botches, failures, successes, aces, **kwargs ):
      self._set_roll_properties( roll_properties )
      self._set_rolls( rolls )
      self._set_roll_categories( roll_categories )
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
      categorize_rolls = kwargs.get( "categorize", False )

      if read_only or categorize_rolls or flatten_rolls or sort: # some option is going to generate a new list and/or the consumer promises not to modify the list contents
         source_rolls = self._rolls
      else:
         source_rolls = self._rolls[:]

      if categorize_rolls:
         rolls = self._categorize_rolls( source_rolls, self.roll_categories )
      else:
         rolls = source_rolls

      if flatten_rolls:
         result = []

         for item in rolls:
            result.extend( item )
      else:
         result = rolls

      if sort:
         if flatten_rolls:
            result = sorted( result, reverse = reverse_sort )
         else:
            result = [ sorted( item, reverse = reverse_sort ) for item in result ]

      return result

   rolls = property( fget = get_rolls )

   def _categorize_rolls( self, source_rolls, source_categories ):
      result = []
      for list_index, rolls in enumerate( source_rolls ):
         categories = source_categories[ list_index ]

         local_rolls = [ CategorizedDiceRoll( roll, categories[ local_index ] ) for local_index, roll in enumerate( rolls ) ]

         result.append( local_rolls )

      return result

   def _set_roll_categories( self, value ):
      self._roll_categories = value

   def get_roll_categories( self ):
      return self._roll_categories

   roll_categories = property( fget = get_roll_categories )

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
