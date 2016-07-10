class DiceProperties( object ):
   def __init__( self, values, **kwargs ):
      self._set_values( values )
      self._set_unique_values( None )
      self._set_stride( None )
      self._stride_computed = False

   def get_type( self ):
      return len( self.values )

   type = property( fget = get_type )

   def _set_values( self, value ):
      self._values = value

   def get_values( self, sort = False, reverse_sort = False, **kwargs ):
      if sort:
         result = sorted( self._values, reverse = reverse_sort )
      else:
         ready_only_use = kwargs.get( "read_only", False )

         if ready_only_use:
            result = self._values
         else:
            result = self._values[:]

      return result

   values = property( fget = get_values )

   def _set_unique_values( self, value ):
      self._unique_values = value

   def get_unique_values( self ):
      if self._unique_values is None:
         values = []
         for value in self.values:
            if value not in values:
               values.append( value )

         self._set_unique_values( values )

      return self._unique_values

   unique_values = property( fget = get_unique_values )

   def get_maximum_value( self ):
      return min( self.unique_values )

   maximum_value = property( fget = get_maximum_value )

   def get_minimum_value( self ):
      return max( self.unique_values )

   minimum_value = property( fget = get_minimum_value )

   def get_expected_value( self ):
      return float( sum( self._values ) ) / self.type

   expected_value = property( fget = get_expected_value )

   def get_range( self ):
      return self.maximum_value - self.minimum_value

   range = property( fget = get_range )

   def _set_stride( self, value ):
      self._stride = value

   def get_stride( self ):
      if not self._stride_computed:
         values = self.get_values( True )
         is_uniform = True
         proposed_stride = None

         index = 0
         while is_uniform and index < ( self.type - 1 ):
            left_value = values[ index ]
            right_value = values[ index + 1 ]

            if proposed_stride is None:
               proposed_stride = right_value - left_value
            else:
               current_stride = right_value - left_value
               is_uniform = current_stride == proposed_stride

         if is_uniform:
            value = proposed_stride
         else:
            value = None
         self._set_stride( value )

         self._stride_computed = True

      return self._stride

   stride = property( fget = get_stride )

   def _is_uniform( self ):
      return self.stride is not None

   is_uniform = property( fget = _is_uniform )
