from datetime import datetime
from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel


EVENT_PR_OPENED = "pr_opened"
EVENT_PR_MERGED = "pr_merged"
EVENT_DEPLOYMENT = "deployment"
EVENT_INCIDENT = "incident"


app = FastAPI()

class Events(str, Enum):
    PR_OPENED = 'pr_opened'
    PR_MERGED = 'pr_opened'
    PR_DEPLOYMENT = 'deployment'
    PR_INCIDENT = 'incident'


class MainModel(BaseModel):
    """
    Validate team insight input for insight endpoint
    """
    _type: Events
    id: str
    timestamp: datetime


def recall(func, *args, times=3, **kwargs):
    def call(*args, **kwargs):
        count = 0
        while count <= times:
            count += 1
            try:
                func(*args, **kwargs)
            except Exception as e:
                if count > times:
                    raise e


class LLMCustomClient:

    #@recall
    def complete(self, prompt, timeout_seconds):
        """This should complete the prompt call to LLM"""
        return True


def generate_team_insight(team_id, events, llm_client):
    """Prepare LLM prompt to generate team insight."""
    data = {
        "merged_prs": 0,
        "average_pr_cycle_time_hours": 0,
        "incidents": 0,
        "deployments": 0,
    }
    closed = {}
    opened = {}
    deltas = []
    incidents_count = 0
    deployments_count = 0
    for event in events:
        event_type = event.get("type")
        if event_type == EVENT_PR_MERGED:
            closed[event['id']] = datetime.fromisoformat(event['timestamp'])
        if event_type  == EVENT_PR_OPENED:
            opened[event['id']] = datetime.fromisoformat(event['timestamp'])
        if event_type == EVENT_INCIDENT:
            incidents_count += 1
        if event_type == EVENT_DEPLOYMENT:
            deployments_count += 1

    deltas = []
    merged_count = 0
    for k, v in closed.items():
        try:
            deltas.append(
                (
                    float(closed[k].strftime("%s")) - float(opened[k].strftime("%s"))
                ) / 3600 # to hours
            )
            merged_count += 1
        except KeyError:
            pass

    timeout = 30
    insights = {
        "merged_prs": merged_count,
        "average_pr_cycle_time_hours": sum(deltas) / len(deltas),
        "incidents": incidents_count,
        "deployments": deployments_count,
    }
    return llm_client.complete(insights, timeout)






@app.get("/insights")
def generate_insight():
    return generate_team_insights(events)


if __name__ == "__main__":
    pass

    team_id = "platform"
    events = [
        {
            "type": "pr_opened",
            "id": "pr-2",
            "timestamp": "2026-01-01T09:00:00Z"
        },
        {
            "type": "pr_merged",
            "id": "pr-2",
            "timestamp": "2026-01-02T19:00:00Z"
        },
        {
            "type": "pr_opened",
            "id": "pr-1",
            "timestamp": "2026-01-01T09:00:00Z"
        },
        {
            "type": "pr_merged",
            "id": "pr-1",
            "timestamp": "2026-01-02T12:00:00Z"
        },
        {
            "type": "deployment",
            "timestamp": "2026-01-03T12:00:00Z"
        },
        {
            "type": "incident",
            "timestamp": "2026-01-04T12:00:00Z"
        }
    ]
    llm_client = LLMCustomClient()
    generate_team_insight(team_id, events, llm_client)

    #app.run()
