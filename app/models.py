from pydantic import BaseModel, Field
from typing import Optional, Sequence


class MethodInfo(BaseModel):
    """Represents a method or a function in a programming language"""
    name: str = Field(..., description="The name of the function or the method")
    startLine: int = Field(..., description="The start line of the function/method in the given code file")
    endLine: int = Field(..., description="The end line of the function/method in the given code file")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


class Methods(BaseModel):
    """List of methods/functions in a given code file"""
    methods: Sequence[MethodInfo] = Field(..., description="List of methods")


class ChangeSet(BaseModel):
    """Represents code file changes"""
    path: str = Field(..., description="Repository relative path to the code file")
    contents: str = Field(..., description="Code file contents to be reviewed")
    is_new_file: bool = Field(..., description="Was this file newly added")
    original_contents: Optional[str] = Field(default=None, description="Was this file newly added")


class SemanticChangeSet(ChangeSet):
    """Represents a reviewable code changes"""
    changed_methods: list[MethodInfo] = Field(..., description="List of methods to be reviewed")

    @classmethod
    def from_changeset(cls, changeset: ChangeSet, methods: list[MethodInfo]):
        return SemanticChangeSet(path=changeset.path,
                                 contents=changeset.contents,
                                 is_new_file=changeset.is_new_file,
                                 changed_methods=methods)
