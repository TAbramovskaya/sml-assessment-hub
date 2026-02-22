import re
import json
from collections import namedtuple

PASSBACK_LIS_RESULT_SOURCEDID_PATTERN = r"course-v1:(?P<course>[^:]+):lms\.skillfactory\.ru-(?P<target_id>[^:]+):(?P<user_id>.+)"
EXPECTED_RAW_DATA_FIELDS = {"lti_user_id", "attempt_type", "created_at", "is_correct", "passback_params"}
EXPECTED_RAW_PASSBACK_PARAMS_FIELDS = {"oauth_consumer_key", "lis_result_sourcedid", "lis_outcome_service_url"}


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
        "is_correct",
        "raw_oauth_consumer_key",
        "raw_lis_result_sourcedid",
        "raw_lis_outcome_service_url"
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

    try:
        passback_params = json.loads(data_item["passback_params"].replace("'", '"'))
    except json.decoder.JSONDecodeError as e:
        print('Invalid JSON in passback params: ', data_item["passback_params"])
        return None

    passback_params_fields = set(passback_params.keys())
    if passback_params_fields != EXPECTED_RAW_PASSBACK_PARAMS_FIELDS:
        print("Passback params mismatch: ", passback_params_fields)
        return None

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
        is_correct=is_correct,
        raw_oauth_consumer_key=passback_params['oauth_consumer_key'],
        raw_lis_result_sourcedid=passback_params['lis_result_sourcedid'],
        raw_lis_outcome_service_url=passback_params['lis_outcome_service_url']
    )
