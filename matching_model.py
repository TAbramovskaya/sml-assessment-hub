import re
import json
from collections import namedtuple
from logger import get_validation_failures_logger
from dateutil import parser, tz

PASSBACK_LIS_RESULT_SOURCEDID_PATTERN = r"course-v1:(?P<course>[^:]+):lms\.skillfactory\.ru-(?P<target_id>[^:]+):(?P<user_id>.+)"
EXPECTED_RAW_DATA_FIELDS = {"lti_user_id", "attempt_type", "created_at", "is_correct", "passback_params"}
EXPECTED_RAW_PASSBACK_PARAMS_FIELDS = {"oauth_consumer_key", "lis_result_sourcedid", "lis_outcome_service_url"}

log = get_validation_failures_logger(__name__)

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
    # raw fields check
    if not isinstance(data_item, dict):
        log.error(f"Data item is not a dict:\n\tItem:\n\t{data_item}")
        return None

    item_fields = set(data_item.keys())
    if item_fields != EXPECTED_RAW_DATA_FIELDS:
        log.error(f"Item fields mismatch: {item_fields}\n\tItem:\n\t{data_item}")
        return None

    # user id validation
    user_id = data_item["lti_user_id"]
    if not isinstance(user_id, str) or len(user_id) == 0:
        log.error(f"User ID mismatch: {user_id}\n\tItem:\n\t{data_item}")
        return None

    # attempt type validation
    attempt_type = data_item["attempt_type"]
    if not attempt_type in {"submit", "run"}:
        log.error(f"Invalid attempt type: {attempt_type}\n\tItem:\n\t{data_item}")
        return None

    # is_correct param validation
    is_correct = data_item["is_correct"]
    if not is_correct in {None, 0, 1}:
        log.error(f"Field 'is_correct' not recognized: {is_correct}\n\tItem:\n\t{data_item}")
        return None

    # created_at validation
    try:
        dt_object = parser.parse(data_item["created_at"])
        created_at = dt_object.astimezone(tz.UTC)
    except (ValueError, TypeError):
        log.error(f"Could not parse datetime: {data_item['created_at']}\n\tItem:\n\t{data_item}")
        return None

    # passback params
    try:
        raw_passback = data_item["passback_params"]
        if not isinstance(raw_passback, str):
            raise TypeError("passback_params is not a string")

        passback_params = json.loads(raw_passback.replace("'", '"'))
        if not isinstance(passback_params, dict):
            raise TypeError("passback_params is not a dict")

    except (json.JSONDecodeError, TypeError):
        log.error(f"Invalid JSON in passback params: {data_item['passback_params']}\n\tItem:\n\t{data_item}")
        return None

    # passback fields
    passback_params_fields = set(passback_params.keys())
    if passback_params_fields != EXPECTED_RAW_PASSBACK_PARAMS_FIELDS:
        log.warning(f"Passback params mismatch: {passback_params_fields}\n\tItem:\n\t{data_item}")
        for absent_param in EXPECTED_RAW_PASSBACK_PARAMS_FIELDS.difference(passback_params_fields):
            passback_params[absent_param] = None

    lis_result_sourcedid = passback_params.get("lis_result_sourcedid")
    if isinstance(lis_result_sourcedid, str):
        match = pattern.match(lis_result_sourcedid)
    else:
        match = None

    if match:
        if user_id != match.group("user_id"):
            log.error(f"User ID mismatch:\n general: {user_id}\n in passback params: {match.group('user_id')}\n\tItem:\n\t{data_item}")
            return None
        course_name = match.group("course").replace("+", " ")
        course_parts = course_name.split(" ")
        course_alias = course_parts[1] if len(course_parts) > 1 else course_name
        target_id = match.group("target_id")
        target_alias = course_alias + " " + target_id[:3] + "..." + target_id[-3:]
    else:
        log.warning(f"Could not parse 'lis_result_sourcedid' passback param: {passback_params.get('lis_result_sourcedid')}\n\tItem:\n\t{data_item}")
        course_name = None
        course_alias = None
        target_id = None
        target_alias = None


    return Attempt(
        user_id=user_id,
        created_at=created_at,
        course_name=course_name,
        course_alias=course_alias,
        target_id=target_id,
        target_alias=target_alias,
        attempt_type=attempt_type,
        is_correct=is_correct,
        raw_oauth_consumer_key=passback_params.get("oauth_consumer_key"),
        raw_lis_result_sourcedid=passback_params.get("lis_result_sourcedid"),
        raw_lis_outcome_service_url=passback_params.get("lis_outcome_service_url")
    )
