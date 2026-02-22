import re
import json
from collections import namedtuple

PASSBACK_LIS_RESULT_SOURCEDID_PATTERN = r"course-v1:(?P<course>[^:]+):lms\.skillfactory\.ru-(?P<target_id>[^:]+):(?P<user_id>.+)"
PASSBACK_PATTERN_GROUPS = ["course", "target_id", "user_id"]
EXPECTED_RAW_DATA_FIELDS = {"lti_user_id", "attempt_type", "created_at", "is_correct", "passback_params"}


pattern = re.compile(PASSBACK_LIS_RESULT_SOURCEDID_PATTERN)

Attempt = namedtuple("Attempt",
    [
        "user_id",
        "created_at",
        "course_name",
        "course_alias",
        "target_id",
        "target_alias",
        "attempt_type",
        "is_correct"
    ])


def get_attempt(data_item):
    item_fields = set(data_item.keys())

    if item_fields != EXPECTED_RAW_DATA_FIELDS:
        print("Item fields mismatch: ", item_fields)
        return None

    user_id = data_item["lti_user_id"]
    attempt_type = data_item["attempt_type"]
    created_at = data_item["created_at"]
    is_correct = data_item["is_correct"]

    passback_params = json.loads(data_item["passback_params"].replace("'", '"'))
    match = pattern.match(passback_params['lis_result_sourcedid'])

    if not match:
        print("Could not parse passback params: ", passback_params)
        return None
    if not user_id == match.group('user_id'):
        print("User ID mismatch (general-passback): ", user_id, match.group('user_id'))
        return None

    course_name = match.group('course').replace('+', ' ')
    course_alias = course_name.split(' ')[1]
    target_id = match.group('target_id')
    target_alias = course_alias + ' ' + target_id[:3] + '...' + target_id[-3:]

    return Attempt(
            user_id=user_id,
            created_at=created_at,
            course_name=course_name,
            course_alias=course_alias,
            target_id=target_id,
            target_alias=target_alias,
            attempt_type=attempt_type,
            is_correct=is_correct
    )
