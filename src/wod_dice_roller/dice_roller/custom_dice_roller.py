from .random_number_generator import StandardRandomNumberGenerator
from .roll_properties import RollProperties
from .uniform_dice_properties import UniformDiceProperties
from .wod_dice_roll_result import WodDiceRollResult
from .wod_dice_roller import WodDiceConstants, WodDiceRoller

class DicePoolNormalizationMethods:
   Successes = "successes"
   DicePool = "dp"

class CustomWodDiceRoller( WodDiceRoller ):
   def __init__( self, prng = None, **kwargs ):
      self._prng = StandardRandomNumberGenerator()

   def _roll_series( self, quantity, dice_properties, **kwargs ):
      return [ self._prng.getRandomItem( dice_properties.get_values( read_only = True ) ) for _ in range( quantity ) ]

   def _partition_rolls( self, roll_properties, rolls, botches_allowed, aces_allowed, **kwargs ):
      botches = failures = successes = aces = 0

      while len( rolls ) > 0:
         # Separate the rolls into classes.
         roll = rolls.pop( 0 )

         if roll_properties.is_botch( roll ):
            if botches_allowed:
               botches += 1
            else:
               failures += 1
         elif roll_properties.is_ace( roll ):
            if aces_allowed:
               aces += 1
            else:
               successes += 1
         elif roll_properties.is_success( roll ):
            successes += 1
         else:
            failures += 1

      return ( botches, failures, successes, aces )

   def roll( self, dice_pool, target_number = WodDiceConstants.DefaultTargetNumber, **kwargs ):
      """
      Process:
      1. Normalize target number:
         - if target number < minimum target number then compute penalty
         - if target number > maximum target number then compute benefit
      2. Roll dice pool
         - if dice pool <= 0 do not roll
         - if dice pool > 0
            - separate dice into classes: botches, aces, successes, failures
            - Process classes:
               1. botches are negated by moving aces into successes
               2. if botches == 0 and aces > 0 then process the explosions
                  if botches > 0 and aces == 0 then remove successes
                     if botches > 0 and successes == 0 then result = -botches
                  if botches == 0 and aces == 0 and successes > 0 then result = successes
                  if botches == and aces == 0 and successes <= 0 then result = 0
      """

      dice_minimum_value = kwargs.get( "dice_minimum_value", WodDiceConstants.DefaultDiceMinimumValue )
      dice_maximum_value = kwargs.get( "dice_maximum_value", WodDiceConstants.DefaultDiceMaximumValue )
      dice_value_stride = kwargs.get( "dice_stride", WodDiceConstants.DefaultDiceStride )
      explosion_limit = kwargs.get( "dice_explosion_limit", WodDiceConstants.DefaultExplosionLimit )
      allow_botch_on_explosion = kwargs.get( "allow_botch_on_explosion", WodDiceConstants.DefaultAllowBotchOnExplosion )
      target_number_minimum = kwargs.get( "target_number_minimum", WodDiceConstants.DefaultMinimumTargetNumber )
      target_number_maximum = kwargs.get( "target_number_maximum", WodDiceConstants.DefaultMaximumTargetNumber )
      dp_normalization_method = kwargs.get( "dp_norm_method", DicePoolNormalizationMethods.Successes )

      dice_properties = UniformDiceProperties( dice_minimum_value, dice_maximum_value, dice_value_stride )

      all_rolls = []
      net_successes = total_botches = total_failures = total_successes = total_aces = 0

      original_target_number = target_number

      if target_number < target_number_minimum:
         dp_norm_bias = target_number_minimum - target_number
         target_number = target_number_minimum
      elif target_number > target_number_maximum:
         dp_norm_bias = target_number_maximum - target_number
         target_number = target_number_maximum
      else:
         dp_norm_bias = 0

      roll_properties = RollProperties( dice_properties, dice_pool, original_target_number, explosion_limit, allow_botch_on_explosion, dp_norm_bias )

      adjusted_dice_pool = dice_pool
      if dp_normalization_method == DicePoolNormalizationMethods.DicePool:
         adjusted_dice_pool += dp_norm_bias
      elif dp_normalization_method != DicePoolNormalizationMethods.Successes:
         raise ValueError( "Dice pool normalization method ({}) is not valid.".format( dp_normalization_method ) )

      if adjusted_dice_pool > 0:
         rolls = self._roll_series( adjusted_dice_pool, roll_properties.dice_properties )
      else:
         rolls = []

      num_rolls = 0
      while len( rolls ) > 0:
         explosions_valid = roll_properties.are_explosions_valid( num_rolls )

         all_rolls.append( rolls[:] )

         roll_botches, roll_failures, roll_successes, roll_aces = self._partition_rolls( roll_properties, rolls, explosions_valid and ( num_rolls == 0 or roll_properties.allow_botch_on_explosion ), explosions_valid )

         total_successes += roll_successes
         total_failures += roll_failures
         total_aces += roll_aces
         total_botches += roll_botches

         # For the rest of the roll processing the failures are ignored.

         processed_roll_successes, dice_to_reroll = self._process_successes( roll_successes, roll_botches, roll_aces )
         if dice_to_reroll > 0:
            rolls = self._roll_series( dice_to_reroll, roll_properties.dice_properties )

         net_successes += processed_roll_successes

         num_rolls += 1

      if net_successes < 0:
         unresolved_botches = -net_successes
         net_successes = 0
      else:
         unresolved_botches = 0

      if dp_normalization_method == DicePoolNormalizationMethods.Successes:
         # The dice pool normalization cannot cause a roll to botch (but it can cause it to fail), although it may cause a roll which would have otherwise botched to simply fail or even succeed.

         if unresolved_botches > 0:
            if unresolved_botches > dp_norm_bias:
               unresolved_botches -= dp_norm_bias
               dp_norm_bias = 0
            else:
               dp_norm_bias -= unresolved_botches
               unresolved_botches = 0

            net_successes += dp_norm_bias
         else:
            if net_successes > dp_norm_bias:
               net_successes -= dp_norm_bias
            else:
               net_successes = 0

      result = WodDiceRollResult( roll_properties, all_rolls, net_successes, unresolved_botches, total_botches, total_failures, total_successes, total_aces )

      return result

   def _process_successes( self, rolled_successes, rolled_botches, rolled_aces ):
      if rolled_successes < 0:
         raise ValueError( "Rolled successes ({:d}) cannot be negative.".format( rolled_successes ) )
      elif rolled_botches < 0:
         raise ValueError( "Rolled botches ({:d}) cannot be negative.".format( rolled_botches ) )
      elif rolled_aces < 0:
         raise ValueError( "Rolled successes ({:d}) cannot be negative.".format( rolled_aces ) )
      else:
         successes = rolled_successes + rolled_aces # An ace is always still as success
         dice_to_reroll = 0

         if rolled_botches > rolled_aces:
            # The aces will cancel some of the botches. Any excess botches are subtracted from the success total.

            net_botches = rolled_botches - rolled_aces
            successes -= net_botches
         else:
            # The botches will cancel some or all of the aces.

            net_aces = rolled_aces - rolled_botches
            dice_to_reroll = net_aces

         return ( successes, dice_to_reroll )
