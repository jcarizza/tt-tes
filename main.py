from datetime import datetime
from fastapi import FastAPI


EVENT_PR_OPENED = "pr_opened"
EVENT_PR_MERGED = "pr_opened"
EVENT_DEPLOYMENT = "deployment"
EVENT_INCIDENT = "incident"



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


def recall(func, *args, **kwargs, times=3):
    def call(*args, **kwargs):
        count = 0
        while count <= times:
            count += 1
            try:
                func(*args, **kwargs):
            except Exception as e:
                if count > times:
                    raise e


class LLMCustomClient:

    @recall
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
    incidents = 0
    deployments = 0
    for event in events:
        # 1 Count events
        # calculate average between event pr open and closed
        if event['id'] == EVENT_PR_CLOSED:
            closed[event['id']] = event['timestamp']
        if event['id'] == EVENT_PR_OPENED:
            opened[event['id']] = event['timestamp']
        if event['id'] == EVENT_INCIDENT:
            incidents += 1
        if event['id'] == EVENT_DEPLOYMENT:
            incidents += 1


        

    return llm_client.complete()






@app.get("/insights")
def read_item(events: Events[]):
    return generate_team_insights(events)


if __name__ == "__main__":
    pass

    team_id = "platform"
    events = [
        {
            "type": "pr_opened",
            "id": "pr-1",
            "timestamp": "2026-01-01T09:00:00Z"
        },
        {
            "type": "pr_merged",
            "id": "pr-1",
            "timestamp": "2026-01-02T09:00:00Z"
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

    #app = FastAPI()
    #app.run()
