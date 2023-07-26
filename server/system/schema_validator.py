import datetime
import uuid
from flask import request
from functools import wraps

from pydantic import BaseModel, constr, validator
from pydantic.types import conint

from server.util.common_validator import email_validator
from typing import Dict


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class Job(BaseModel):
    title: constr(min_length=1)
    description: constr(min_length=1)
    responsibilities: constr(min_length=1)
    qualifications: constr(min_length=1)
    work_mode: constr(min_length=1)


def parse_query_params(request_args: Dict) -> Dict:
    page = int(request_args.get("page", 1))
    per_page = int(request_args.get("per_page", 20))
    search_query = request_args.get("search", "")
    sort_by = request_args.get("sort_by", "")

    return {
        "page": page,
        "per_page": per_page,
        "search_query": search_query,
        "sort_by": sort_by,
    }


class QueryParams(BaseModel):
    page: conint(gt=0) = 1
    per_page: conint(gt=0) = 20
    search_query: str = ""
    sort_by: str = ""

    @validator("sort_by")
    def validate_sort_by(cls, sort_by):
        valid_sort_fields = {
            # field of Job model
            "title",
            "description",
            "responsibilities",
            "qualifications",
            "work_mode",
            "updated_at",
            "created-at",
        }
        if sort_by and sort_by.lstrip("-") not in valid_sort_fields:
            raise ValueError(
                f"Invalid sort_by field. Valid fields are: {', '.join(valid_sort_fields)}"
            )
        return sort_by


def valid_params(query_params: Dict) -> str:
    try:
        QueryParams(**query_params)
        return ""
    except ValueError as e:
        return str(e)
