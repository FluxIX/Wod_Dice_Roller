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
