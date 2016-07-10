from .dice_properties import DiceProperties

class UniformDiceProperties( DiceProperties ):
   def __init__( self, minimum_value, maximum_value, stride = 1, **kwargs ):
      super( UniformDiceProperties, self ).__init__( self._get_dice_values( minimum_value, maximum_value, stride ), **kwargs )

   def _get_dice_values( self, minimum_value, maximum_value, stride = 1 ):
      return list( range( minimum_value, maximum_value + stride, stride ) )
