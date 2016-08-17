from .random_number_generator import StandardRandomNumberGenerator
from .roll_properties import RollProperties
from .uniform_dice_properties import UniformDiceProperties
from .wod_dice_roll_result import WodDiceRollResult, DiceRollValueCategory, DiceRollValueCategoryFlags
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
      botches = []
      failures = []
      successes = []
      aces = []

      categories = []

      for index, roll in enumerate( rolls ):
         # Separate the rolls into classes.

         if roll_properties.is_botch( roll ):
            if botches_allowed:
               partition = botches
               category_value = DiceRollValueCategoryFlags.Botch
            else:
               partition = failures
               category_value = DiceRollValueCategoryFlags.Failure
         elif roll_properties.is_ace( roll ):
            if aces_allowed:
               partition = aces
               category_value = DiceRollValueCategoryFlags.Ace
            else:
               partition = successes
               category_value = DiceRollValueCategoryFlags.Success
         elif roll_properties.is_success( roll ):
            partition = successes
            category_value = DiceRollValueCategoryFlags.Success
         else:
            partition = failures
            category_value = DiceRollValueCategoryFlags.Failure

         partition.append( index )
         categories.append( DiceRollValueCategory( category_value ) )

      return ( categories, botches, failures, successes, aces )

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
      all_roll_categories = []
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

         all_rolls.append( rolls )

         roll_categories, roll_botches, roll_failures, roll_successes, roll_aces = self._partition_rolls( roll_properties, rolls, explosions_valid and ( num_rolls == 0 or roll_properties.allow_botch_on_explosion ), explosions_valid )

         total_successes += len( roll_successes )
         total_failures += len( roll_failures )
         total_aces += len( roll_aces )
         total_botches += len( roll_botches )

         # For the rest of the roll processing the failures are ignored.

         processed_roll_successes, dice_to_reroll, cancelled_indicies, suppressed_indicies = self._process_successes( rolls, roll_categories, roll_successes, roll_botches, roll_aces )

         for index in cancelled_indicies:
            category = roll_categories[ index ]
            category._set_value( category.value | DiceRollValueCategoryFlags.Cancelled )

         for index in suppressed_indicies:
            category = roll_categories[ index ]
            category._set_value( category.value | DiceRollValueCategoryFlags.Suppressed )

         if dice_to_reroll > 0:
            rolls = self._roll_series( dice_to_reroll, roll_properties.dice_properties )
         else:
            rolls = []

         net_successes += processed_roll_successes
         all_roll_categories.append( roll_categories )

         num_rolls += 1

      if net_successes < 0:
         unresolved_botches = -net_successes
         net_successes = 0
      else:
         unresolved_botches = 0

      if dp_normalization_method == DicePoolNormalizationMethods.Successes:
         # The dice pool normalization cannot cause a roll to botch (but it can cause it to fail), although it may cause a roll which would have otherwise botched to simply fail or even succeed. A botch can be made more severe by the dice pool normalization.

         if unresolved_botches > 0:
            if dp_norm_bias < 0 or unresolved_botches > dp_norm_bias: # If the bias makes the botch more severe or if the unresolved botch count is reduced but still remains positive
               unresolved_botches -= dp_norm_bias
            elif dp_norm_bias > 0: # The roll may succeed as the bias is adding successes and is at least equal to the number of unresolved botches
               excess_dp_norm_bias = dp_norm_bias - unresolved_botches
               unresolved_botches = 0

               net_successes += excess_dp_norm_bias
         else:
            net_successes = max( net_successes + dp_norm_bias, 0 )

      result = WodDiceRollResult( roll_properties, all_rolls, all_roll_categories, net_successes, unresolved_botches, total_botches, total_failures, total_successes, total_aces )

      return result

   def _process_successes( self, rolls, categories, rolled_successes, rolled_botches, rolled_aces ):
      ace_count = len( rolled_aces )
      success_count = len( rolled_successes )
      botch_count = len( rolled_botches )

      suppressed_ace_indicies = []
      cancelled_botch_indicies = []
      cancelled_success_indicies = []
      cancelled_ace_indicies = []

      if botch_count > 0:
         initial_state = 0
         ace_suppress_state = initial_state + 1
         success_cancel_state = ace_suppress_state + 1
         ace_cancel_state = success_cancel_state + 1
         finished_state = ace_cancel_state + 1

         def get_roll_value( index ):
            return rolls[ index ]

         sorted_botches = sorted( rolled_botches, reverse = True, key = get_roll_value )
         sorted_successes = sorted( rolled_successes, key = get_roll_value )
         sorted_aces = sorted( rolled_aces, key = get_roll_value )

         def get_next_state( current_state = None ):
            if current_state is None:
               current_state = initial_state

            if current_state == initial_state and len( sorted_aces ) > 0:
               current_state = ace_suppress_state
               target_count = ace_count
            elif current_state in [ initial_state, ace_suppress_state ] and len( sorted_successes ) > 0:
               current_state = success_cancel_state
               target_count = success_count
            elif current_state in [ initial_state, ace_suppress_state, success_cancel_state ] and len( sorted_aces ) > 0:
               current_state = ace_cancel_state
               target_count = ace_count
            else:
               current_state = finished_state
               target_count = None

            current_state_pass_count = 0

            return ( current_state, target_count, current_state_pass_count )

         current_state, target_count, current_state_pass_count = get_next_state()

         for botch_index in sorted_botches:
            cancelled_botch_indicies.append( botch_index )
            current_state_pass_count += 1

            if current_state == ace_suppress_state:
               suppressed_ace_indicies.append( sorted_aces[ len( suppressed_ace_indicies ) ] )

               if current_state_pass_count == target_count:
                  current_state, target_count, current_state_pass_count = get_next_state( current_state )
            elif current_state == success_cancel_state:
               cancelled_success_indicies.append( sorted_successes[ len( cancelled_success_indicies ) ] )

               if current_state_pass_count == target_count:
                  current_state, target_count, current_state_pass_count = get_next_state( current_state )
            elif current_state == ace_cancel_state:
               cancelled_ace_indicies.append( sorted_aces[ len( cancelled_ace_indicies ) ] )

               if current_state_pass_count == target_count:
                  current_state, target_count, current_state_pass_count = get_next_state( current_state )
            else: # if current_state == finished_state:
               cancelled_botch_indicies.pop() # The botch wasn't actually cancelled so we correct the bookkeeping

               break

         successes = success_count - len( cancelled_success_indicies ) + ace_count - len( cancelled_ace_indicies ) - ( botch_count - len( cancelled_botch_indicies ) )
         dice_to_reroll = ace_count - len( suppressed_ace_indicies )
      else:
         dice_to_reroll = ace_count
         successes = success_count + ace_count

      return ( successes, dice_to_reroll, cancelled_ace_indicies + cancelled_success_indicies + cancelled_botch_indicies, suppressed_ace_indicies )
