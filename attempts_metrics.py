from collections import defaultdict, Counter


def get_unique_users(attempts):
    return set(att.user_id for att in attempts)


def get_unique_targets(attempts):
    return set(att.target_id for att in attempts)


def get_attempts_per_course(attempts):
    attempts_per_course = defaultdict(list)

    for att in attempts:
        attempts_per_course[att.course_name].append(att)

    return attempts_per_course


def count_attempts_per_user(attempts):
    return Counter(att.user_id for att in attempts)


def count_correctness(attempts):
    return Counter(att.is_correct for att in attempts)


def count_attempt_types(attempts):
    return Counter(att.attempt_type for att in attempts)


