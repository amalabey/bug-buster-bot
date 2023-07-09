from pydantic import BaseModel, Field
from typing import Sequence


class MethodInfo(BaseModel):
    """Represents a method or a function in a programming language"""
    name: str = Field(..., description="The name of the function or the method")
    startLine: int = Field(..., description="The start line of the function/method in the given code file")
    endLine: int = Field(..., description="The end line of the function/method in the given code file")


class Methods(BaseModel):
    """List of methods/functions in a given code file"""
    methods: Sequence[MethodInfo] = Field(..., description="List of methods")


class ChangeSet(BaseModel):
    """Represents code file changes"""
    path: str = Field(..., description="Repository relative path to the code file")
    contents: int = Field(..., description="Code file contents to be reviewed")
    changed_line_nums: int = Field(..., description="List of line numbers that were changed")
    is_new_file: bool = Field(..., description="Was this file newly added")