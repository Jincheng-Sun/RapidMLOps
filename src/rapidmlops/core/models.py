from dataclasses import dataclass, asdict
from typing import Optional, Dict


@dataclass
class GitOpsLineageTags:
    """Standardized metadata tags across all MLOps platforms."""

    repo_name: Optional[str] = None
    git_commit_sha: Optional[str] = None
    git_commmit_sha_short: Optional[str] = None
    pr_id: Optional[str] = None
    source_branch: Optional[str] = None
    build_id: Optional[str] = None
    environment: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_owner: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    approver_name: Optional[str] = None

    def __post_init__(self):
        if self.git_commit_sha:
            self.git_commmit_sha_short = self.git_commit_sha[:8]

    def to_dict(self) -> Dict[str, str]:
        """Returns only populated tags as a dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}
