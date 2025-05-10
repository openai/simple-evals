import re
text1 = "To determine the correct answer, let's analyze each option in the context of characteristics of all living organisms.\n\nA) Move from place to place - Not all living organisms can move from place to place. For example, plants and some microorganisms are generally immobile.\n\nB) Detect and respond to changes in the environment - All living organisms have the ability to detect and respond to changes in their environment. This is a fundamental characteristic of life, as it allows organisms to adapt and survive.\n\nC) Produce sugars by photosynthesis - Not all living organisms can produce sugars by photosynthesis. This ability is primarily found in plants, algae, and some bacteria. Many other organisms, including animals and some microorganisms, cannot perform photosynthesis.\n\nD) Produce heat to maintain a constant internal temperature - This characteristic is known as endothermy and is not a feature of all living organisms. Many organisms, including most plants, fish, and reptiles, are ectothermic, meaning their body temperature is regulated by the environment.\n\nGiven the above analysis, the characteristic that is common to all living organisms is the ability to detect and respond to changes in the environment.\n\nAnswer: B"

MULTILINGUAL_ANSWER_PATTERN_TEMPLATE = (
    "(?i){}[ \t]*([A-D]|[أ-د]|[অ]|[ব]|[ড]|[ঢ]|[Ａ]|[Ｂ]|[Ｃ]|[Ｄ])"
)
MULTILINGUAL_ANSWER_REGEXES = r"Answer\s*:"
regex = MULTILINGUAL_ANSWER_PATTERN_TEMPLATE.format(MULTILINGUAL_ANSWER_REGEXES)

match = re.search(regex, text1)
if match:
    print(match.group(1))
else:
    print("No match found")