import numpy as np
CATEGORIES_NAMES = [
    'Ones',
    'Twos',
    'Threes',
    'Fours',
    'Fives',
    'Sixes',
    'Three-of-a-Kind',
    'Four-of-a-Kind',
    'Full House',
    'Small Straight',
    'Large Straight',
    'Yahtzee',
    'Chance',
    'Bonus',
]

CATEGORY_NAME2ID = {
    'Ones': 0,
    'Twos': 1,
    'Threes': 2,
    'Fours': 3,
    'Fives': 4,
    'Sixes': 5,
    'Three-of-a-Kind': 6,
    'Four-of-a-Kind': 7,
    'Full House': 8,
    'Small Straight': 9,
    'Large Straight': 10,
    'Yahtzee': 11,
    'Chance': 12,
    'Bonus': 13,
}

CATEGORIES_SCORING = [
    lambda dice: np.count_nonzero(dice == 1),
    lambda dice: np.count_nonzero(dice == 2) * 2,
    lambda dice: np.count_nonzero(dice == 3) * 3,
    lambda dice: np.count_nonzero(dice == 4) * 4,
    lambda dice: np.count_nonzero(dice == 5) * 5,
    lambda dice: np.count_nonzero(dice == 6) * 6,
    lambda dice: sum(dice),
    lambda dice: sum(dice),
    lambda dice: 25,
    lambda dice: 30,
    lambda dice: 40,
    lambda dice: 50,
    lambda dice: sum(dice),
    lambda dice: 35
]


CATEGORIES_CHECK = [
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: max([np.count_nonzero(dice == die) for die in set(dice)]) >= 3,
    lambda dice: max([np.count_nonzero(dice == die) for die in set(dice)]) >= 4,
    lambda dice: (max([np.count_nonzero(dice == die) for die in set(dice)]) == 3 and 
                  min([np.count_nonzero(dice == die) for die in set(dice)]) == 2),
    lambda dice: (len(set(dice).intersection({1, 2, 3, 4})) == 4 or 
                  len(set(dice).intersection({2, 3, 4, 5})) == 4 or
                  len(set(dice).intersection({3, 4, 5, 6})) == 4),
    lambda dice: set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}),
    lambda dice: len(set(dice)) == 1,
    lambda dice: True,
    lambda dice: True
]


CATEGORIES = dict(
    [(name, (score, check)) for name, score, check in zip(
        CATEGORIES_NAMES,
        CATEGORIES_SCORING,
        CATEGORIES_CHECK
    )]
)

get_category_free_feature_name = lambda cat: f'is_{cat}_free'
get_die_value_feature_name = lambda die, face: f'is_die_{die}_{face}'
get_die_count_feature_name = lambda count, face: f'{count}_dice_with_{face}'
get_distinct_face_feature_name = lambda count: f'{count}_distinct_dice'
get_sum_feature_name = lambda lower: f'sum_between_{lower}_and_{lower + 6}'
get_rerolls_feature_name = lambda count: f'{count}_rerolls_left'
get_turns_feature_name = lambda turns: f'{turns}_turns_left'
get_select_category_feature_name = lambda cat: f'select_{cat}'
get_reroll_dice_feature_name = lambda die: f'rerolling_{die}'
category_free_features = [get_category_free_feature_name(cat) for cat in CATEGORIES_NAMES[:-1]]
die_value_features = [get_die_value_feature_name(die, face) for die in range(1, 6) for face in range(1, 7)]
die_count_features = [get_die_count_feature_name(count, face) for face in range(1, 7) for count in range(6)]
distinct_face_features = [get_distinct_face_feature_name(count) for count in range(1, 6)]
sum_features = [get_sum_feature_name(lower) for lower in range(1, 30, 6)]
rerolls_features = [get_rerolls_feature_name(count) for count in range(3)]
turns_features = [get_turns_feature_name(turns) for turns in range(1, 8)]
select_category_features = [get_select_category_feature_name(cat) for cat in CATEGORIES_NAMES[:-1]]
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
