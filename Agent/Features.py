MASTER_CATEGORIES = [
    'Three-of-a-Kind',
    'Four-of-a-Kind',
    'Full House',
    'Small Straight',
    'Large Straight',
    'Yahtzee',
    'Chance'
]
get_category_free_feature_name = lambda cat: f'is_{cat}_free'
get_die_value_feature_name = lambda die, face: f'is_die_{die}_{face}'
get_die_count_feature_name = lambda count, face: f'{count}_dice_with_{face}'
get_distinct_face_feature_name = lambda count: f'{count}_distinct_dice'
get_sum_feature_name = lambda lower: f'sum_between_{lower}_and_{lower + 6}'
get_rerolls_feature_name = lambda count: f'{count}_rerolls_left'
get_turns_feature_name = lambda turns: f'{turns}_turns_left'
get_select_category_feature_name = lambda cat: f'select_{cat}'
get_reroll_dice_feature_name = lambda die: f'rerolling_{die}'
category_free_features = [get_category_free_feature_name(cat) for cat in MASTER_CATEGORIES]
die_value_features = [get_die_value_feature_name(die, face) for die in range(1, 6) for face in range(1, 7)]
die_count_features = [get_die_count_feature_name(count, face) for face in range(1, 7) for count in range(6)]
distinct_face_features = [get_distinct_face_feature_name(count) for count in range(1, 6)]
sum_features = [get_sum_feature_name(lower) for lower in range(1, 30, 6)]
rerolls_features = [get_rerolls_feature_name(count) for count in range(3)]
turns_features = [get_turns_feature_name(turns) for turns in range(1, 8)]
select_category_features = [get_select_category_feature_name(cat) for cat in MASTER_CATEGORIES]
reroll_die_features = [get_reroll_dice_feature_name(die) for die in range(1, 6)]

feature_lists = [
    category_free_features,
    die_value_features,
    die_count_features,
    distinct_face_features,
    sum_features,
    rerolls_features,
    turns_features,
   #  select_category_features,
   #  reroll_die_features
]

TOTAL_COMBINED_FEATURES = []
for feature_list in feature_lists:
    TOTAL_COMBINED_FEATURES.extend(feature_list)

def getFeatures(state):
      feature_vals = dict([(feature, 0) for feature in TOTAL_COMBINED_FEATURES])
      dice, rerolls, categories = state
      
      # get categories features
      for category in categories:
         feature_vals[get_category_free_feature_name(MASTER_CATEGORIES[category])] = 1
      
      # get die value features
      for die, face in enumerate(dice):
         feature_vals[get_die_value_feature_name(die + 1, face)] = 1

      # get die count features
      die_count = dict([(face, dice.count(face)) for face in range(1, 7)])
      for face, counts in die_count.items():
         feature_vals[get_die_count_feature_name(counts, face)] = 1
      
      # get distinct die features
      feature_vals[get_distinct_face_feature_name(len(set(dice)))] = 1

      # get sum feature
      feature_vals[get_sum_feature_name(((sum(dice) - 1) // 6) * 6 + 1)] = 1

      # get rerolls feature
      feature_vals[get_rerolls_feature_name(rerolls)] = 1

      # get turns feature
      feature_vals[get_turns_feature_name(len(categories))] = 1

      # get select category features
      # feature_vals[get_select_category_feature_name(MASTER_CATEGORIES[action[1]])] = 1
      # get reroll die features
      # for i, select in enumerate(action[1]):
      #    if not select: 
      #       feature_vals[get_reroll_dice_feature_name(i + 1)] = 1
      return feature_vals
