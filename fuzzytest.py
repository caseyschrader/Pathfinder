from thefuzz import fuzz

test_pairs = [
    ("State Street", "State St"),
    ("State Street", "Estate St"),  # Should not match
    ("800 South", "800 S"),
    ("800 South", "7800 S")        # Should not match
]

for search, target in test_pairs:
    score = fuzz.partial_ratio(search, target)
    print(f"'{search}' vs '{target}': {score}")