def match_group(text, group):
    return any(k in text for k in group)


def keyword_score(text, role_data):
    core = role_data.get("core", [])
    secondary = role_data.get("secondary", [])

    matched_core = [g for g in core if match_group(text, g)]
    matched_secondary = [g for g in secondary if match_group(text, g)]

    core_score = (len(matched_core) / len(core)) * 70 if core else 0
    secondary_score = (len(matched_secondary) / len(secondary)) * 30 if secondary else 0

    return core_score + secondary_score, matched_core + matched_secondary
