"""
File-based job store for managing long-running Flowise tasks.
"""
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

class Job:
    """Represents a single long-running job."""

    def __init__(self, job_id: str, query: str, chatflow_id: str, session_id: str, status: str = "pending", result: Optional[str] = None):
        self.job_id = job_id
        self.query = query
        self.chatflow_id = chatflow_id
        self.session_id = session_id
        self.status = status
        self.result = result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "query": self.query,
            "chatflow_id": self.chatflow_id,
            "session_id": self.session_id,
            "status": self.status,
            "result": self.result
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        return cls(
            job_id=data["job_id"],
            query=data["query"],
            chatflow_id=data["chatflow_id"],
            session_id=data.get("session_id", data["job_id"]),  # Backward compatibility
            status=data["status"],
            result=data.get("result")
        )

class JobStore:
    """Manages the persistence of jobs in a JSON file."""

    def __init__(self, file_path: str = "jobs.json"):
        self.file_path = Path(file_path)
        self.jobs: Dict[str, Job] = self._load()

    def _load(self) -> Dict[str, Job]:
        if not self.file_path.exists():
            return {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {job_id: Job.from_dict(job_data) for job_id, job_data in data.items()}

    def _save(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump({job_id: job.to_dict() for job_id, job in self.jobs.items()}, f, indent=4)

    def create_job(self, query: str, chatflow_id: str) -> Job:
        job_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        job = Job(job_id=job_id, query=query, chatflow_id=chatflow_id, session_id=session_id)
        self.jobs[job_id] = job
        self._save()
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        return list(self.jobs.values())

    def update_job_status(self, job_id: str, status: str, result: Optional[str] = None) -> None:
        if job_id in self.jobs:
            self.jobs[job_id].status = status
            if result:
                self.jobs[job_id].result = result
            self._save() 