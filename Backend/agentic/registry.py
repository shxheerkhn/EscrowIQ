"""Allowlisted, read-only marketplace tools for the hiring assistant."""


class AgentToolError(ValueError):
    pass


class AgentToolRegistry:
    """Provides a deliberately small, validated read-only tool surface."""

    ALLOWED_TOOLS = {"list_client_jobs", "get_job_candidates", "get_pending_proposals"}

    def __init__(self, query_db, hybrid_matcher):
        self._query_db = query_db
        self._hybrid_matcher = hybrid_matcher

    def tool_descriptions(self):
        return {
            "list_client_jobs": "List the current client's open jobs.",
            "get_job_candidates": "Rank suitable freelancers for an owned open job. Requires job_id.",
            "get_pending_proposals": "List pending proposals for an owned job. Requires job_id.",
        }

    def execute(self, tool_name, arguments, client_id):
        if tool_name not in self.ALLOWED_TOOLS:
            raise AgentToolError("Tool is not allowed")
        if not isinstance(arguments, dict):
            raise AgentToolError("Tool arguments must be an object")
        if tool_name == "list_client_jobs":
            return self._list_client_jobs(client_id)

        job_id = arguments.get("job_id")
        if not isinstance(job_id, int) or isinstance(job_id, bool) or job_id <= 0:
            raise AgentToolError("job_id must be a positive integer")
        job = self._query_db(
            "SELECT id, title, description, skills_required, budget, deadline, status "
            "FROM jobs WHERE id=? AND client_id=?",
            [job_id, client_id], one=True,
        )
        if not job:
            raise AgentToolError("Job not found")
        if job["status"] != "open":
            raise AgentToolError("Only open jobs can be reviewed for hiring")
        if tool_name == "get_pending_proposals":
            return self._get_pending_proposals(job)
        return self._get_job_candidates(job)

    def _list_client_jobs(self, client_id):
        return self._query_db(
            "SELECT id, title, skills_required, budget, deadline, status FROM jobs "
            "WHERE client_id=? AND status='open' ORDER BY created_at DESC, id DESC LIMIT 20",
            [client_id],
        )

    def _get_pending_proposals(self, job):
        return self._query_db(
            """
            SELECT p.id, p.freelancer_id, p.bid_amount, p.timeline, p.cover_letter,
                   COALESCE(u.full_name, u.username) AS freelancer_name, u.skills, u.rating, u.total_reviews
            FROM proposals p JOIN users u ON u.id=p.freelancer_id
            WHERE p.job_id=? AND p.status='pending'
            ORDER BY p.created_at ASC, p.id ASC
            """, [job["id"]],
        )

    def _get_job_candidates(self, job):
        freelancers = self._query_db(
            "SELECT id, username, full_name, skills, bio, rating, total_reviews "
            "FROM users WHERE role='freelancer' AND email_verified=TRUE"
        )
        candidates = self._hybrid_matcher(job, freelancers)
        return [{
            "freelancer_id": candidate["id"],
            "name": candidate.get("full_name", ""),
            "skills": candidate.get("skills", ""),
            "match_score": candidate.get("hybrid_score", 0),
            "rating": candidate.get("rating", 0),
            "total_reviews": candidate.get("total_reviews", 0),
        } for candidate in candidates[:5]]
