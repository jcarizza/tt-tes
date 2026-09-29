import json
import logging
import time
import functools


from datetime import datetime
from enum import Enum


import litellm
from litellm import completion
from pydantic import BaseModel, Field
from fastapi import FastAPI, Body

logger = logging.getLogger()

MODEL = "gpt-4o"
EVENT_PR_OPENED = "pr_opened"
EVENT_PR_MERGED = "pr_merged"
EVENT_DEPLOYMENT = "deployment"
EVENT_INCIDENT = "incident"
INTENTS = 5


app = FastAPI()


class EnumEvents(str, Enum):
    PR_OPENED = 'pr_opened'
    PR_MERGED = 'pr_merged'
    PR_DEPLOYMENT = 'deployment'
    PR_INCIDENT = 'incident'


class LLMResponseParsingError(Exception):
    pass


class Events(BaseModel):
    """
    Validate team insight input for insight endpoint
    """
    type_: EnumEvents = Field(alias="type")
    id: str | None = None
    timestamp: datetime


class LLMCustomClient:

    @functools.cache
    def complete(self, prompt, timeout_seconds):
        """This should complete the prompt call to LLM
        TODO:
          - cache only work for 1 vps if want shared cache use redis
        """

        instructions = (
                """
You are assisting with team-level engineering productivity insights. 
Please limit your answers to this items that are provided:
 - Opened PRs
 - Closed PRs
 - Incident count
 - Deployment count
Set a friendly tone but be consice
Connect or search in web is forbidden
Do not evaluate individuals, infer personal performance, or invent data. 
Use only the following aggregated metrics. Return JSON with exactly as the example
we provide here.\n\n

Input example:
```json
{
    "team_id": "platform",
    "events": [
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
}
```


Answer example:

```json
    {
  "team_id": "platform",
  "metrics": {
    "merged_prs": 1,
    "average_pr_cycle_time_hours": 24.0,
    "deployments": 1,
    "incidents": 1
  },
  "insight": {
    "summary": "The team merged one pull request with an average cycle time of 24 hours.",
    "recommendations": [
      "Continue monitoring pull request cycle time."
    ]
  }
}
```
            """
        )
        response = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        try:
            return json.loads(response.choices[0].message.content[8:-3])
        except Exception as e:
            raise LLMResponseParsingError("Error parsing response")

    def parse_llm_response(self):
        """Parse response."""
        pass


def build_prompt(team_id, metrics):
    metrics_json = json.dumps(metrics, sort_keys=True)
    user_input = (
        "User input"
        f"Team: {team_id}\n"
        f"Aggregated metrics: {metrics_json} \n\n"
    )
    return user_input


def generate_team_insight(team_id, events, llm_client):
    """Prepare LLM prompt to generate team insight."""
    closed = {}
    opened = {}
    deltas = []
    incidents_count = 0
    deployments_count = 0
    for event in events:
        event_type = event.type_
        if event_type == EVENT_PR_MERGED:
            closed[event.id] = event.timestamp
        if event_type  == EVENT_PR_OPENED:
            opened[event.id] = event.timestamp
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
    prompt = build_prompt(team_id, insights)

    attempt = 0
    for intent in range(INTENTS):
        try:
            return llm_client.complete(prompt, timeout)
            break
        except Exception as e:
            logger.error("LLM response error intent=%s", intent)
            time.sleep(.8 * intent) # simulate a backoff
        except LLMResponseParsingError:
            logger.error("LLM failed parsing response.")
            break
            




llm_client = LLMCustomClient()


@app.post("/insights/{team_id}")
def generate_insight(team_id: str, events: list[Events] = Body(embed=True)):
    """Generate team insight based on input date.

    TODO:
      - Protect endpoint with auth dependency
      - Limite requests per second
    """
    return generate_team_insight(team_id, events, llm_client)





#if __name__ == "__main__":
#    pass
#
#    team_id = "platform"
#    events = [
#        {
#            "type": "pr_opened",
#            "id": "pr-2",
#            "timestamp": "2026-01-01T09:00:00Z"
#        },
#        {
#            "type": "pr_merged",
#            "id": "pr-2",
#            "timestamp": "2026-01-02T19:00:00Z"
#        },
#        {
#            "type": "pr_opened",
#            "id": "pr-1",
#            "timestamp": "2026-01-01T09:00:00Z"
#        },
#        {
#            "type": "pr_merged",
#            "id": "pr-1",
#            "timestamp": "2026-01-02T12:00:00Z"
#        },
#        {
#            "type": "deployment",
#            "timestamp": "2026-01-03T12:00:00Z"
#        },
#        {
#            "type": "incident",
#            "timestamp": "2026-01-04T12:00:00Z"
#        }
#    ]
#    llm_client = LLMCustomClient()
#    generate_team_insight(team_id, events, llm_client)
#
#    #app.run()
