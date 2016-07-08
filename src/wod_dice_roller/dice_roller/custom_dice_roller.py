from .random_number_generator import StandardRandomNumberGenerator
from .wod_dice_roller import WodDiceConstants, WodDiceRoller, WodDiceRollResult

class DicePoolNormalizationMethods:
   Successes = "successes"
   DicePool = "dp"

class CustomWodDiceRoller( WodDiceRoller ):
   def __init__( self, prng = None, **kwargs ):
      self._prng = StandardRandomNumberGenerator()

   def _roll_series( self, quantity, die_type = WodDiceConstants.DefaultDiceType, **kwargs ):
      dice_minimum_value = kwargs.get( "dice_minimum_value", WodDiceConstants.DefaultDiceMinimumValue )
      dice_maximum_value = kwargs.get( "dice_maximum_value", WodDiceConstants.DefaultDiceMaximumValue )
      dice_value_stride = kwargs.get( "dice_stride", WodDiceConstants.DefaultDiceStride )

      dice_values = list( range( dice_minimum_value, dice_maximum_value + dice_value_stride, dice_value_stride ) )

      return [ self._prng.getRandomItem( dice_values ) for _ in range( quantity ) ]

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

      dice_type = kwargs.get( "dice_type", WodDiceConstants.DefaultDiceType )
      dice_minimum_value = kwargs.get( "dice_minimum_value", WodDiceConstants.DefaultDiceMinimumValue )
      dice_maximum_value = kwargs.get( "dice_maximum_value", WodDiceConstants.DefaultDiceMaximumValue )
      explosion_limit = kwargs.get( "dice_explosion_limit", WodDiceConstants.DefaultExplosionLimit )
      allow_botch_on_explosion = kwargs.get( "allow_botch_on_explosion", WodDiceConstants.DefaultAllowBotchOnExplosion )
      target_number_minimum = kwargs.get( "target_number_minimum", WodDiceConstants.DefaultMinimumTargetNumber )
      target_number_maximum = kwargs.get( "target_number_maximum", WodDiceConstants.DefaultMaximumTargetNumber )
      dp_normalization_method = kwargs.get( "dp_norm_method", DicePoolNormalizationMethods.Successes )

      has_explosion_limit = explosion_limit != WodDiceConstants.NoExplosionLimit

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

      original_dp_norm_bias = dp_norm_bias

      adjusted_dice_pool = dice_pool
      if dp_normalization_method == DicePoolNormalizationMethods.DicePool:
         adjusted_dice_pool += dp_norm_bias
      elif dp_normalization_method != DicePoolNormalizationMethods.Successes:
         raise ValueError( "Dice pool normalization method ({}) is not valid.".format( dp_normalization_method ) )

      if adjusted_dice_pool > 0:
         rolls = self._roll_series( adjusted_dice_pool, dice_type )
      else:
         rolls = []

      num_rolls = 0
      while len( rolls ) > 0:
         explosions_valid = not has_explosion_limit or num_rolls < explosion_limit
         roll_botches = roll_failures = roll_successes = roll_aces = 0

         while len( rolls ) > 0:
            # Separate the rolls into classes.
            roll = rolls.pop( 0 )
            all_rolls.append( roll )

            if roll == dice_minimum_value:
               if explosions_valid and ( num_rolls == 0 or allow_botch_on_explosion ):
                  roll_botches += 1
               else:
                  roll_failures += 1
            elif roll == dice_maximum_value:
               if explosions_valid:
                  roll_aces += 1
               else:
                  roll_successes += 1
            elif roll >= target_number:
               roll_successes += 1
            else:
               roll_failures += 1

         total_successes += roll_successes
         total_failures += roll_failures
         total_aces += roll_aces
         total_botches += roll_botches

         # For the rest of the roll processing the failures are ignored.

         processed_roll_successes = roll_successes
         processed_roll_botches = roll_botches
         processed_roll_aces = roll_aces

         if processed_roll_botches > 0 or processed_roll_aces > 0:
            if processed_roll_botches > processed_roll_aces:
               # The aces will cancel some of the botches. An ace is still treated as a success.

               processed_roll_botches -= processed_roll_aces
               processed_roll_successes += processed_roll_aces
               processed_roll_aces = 0
            else:
               # The botches will cancel some or all of the aces. The cancelled ace is still treated as a success.

               processed_roll_aces -= processed_roll_botches
               processed_roll_successes += processed_roll_botches
               processed_roll_botches = 0

            if processed_roll_aces > 0:
               # If an excess number of aces, treat all remaining aces as successes and roll the explosions.

               processed_roll_successes += processed_roll_aces
               rolls.extend( self._roll_series( processed_roll_aces, dice_type ) )
               processed_roll_aces = 0
            elif processed_roll_botches > 0:
               # If an excess number of botches, reduce the number of roll successes by the number of unresolved botches.

               processed_roll_successes -= processed_roll_botches
               processed_roll_botches = 0

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

            dp_norm_bias = 0

      result = WodDiceRollResult( dice_type, dice_pool, original_target_number, original_dp_norm_bias, all_rolls, net_successes, unresolved_botches, total_botches, total_failures, total_successes, total_aces )

      return result
