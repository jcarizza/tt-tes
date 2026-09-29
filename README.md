


## Getting started
```
# Install requirements
pip install requirements.txt

# Set OPENAI apikey
export OPENAI_API_KEY=<your-openai-api-key>

# Run fastapi server
fastapi run main.py
```


##
```curl
curl -X POST "http://localhost:8000/insights/awesome-team"   -H "Content-Type: application/json"   -d '{
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
  }'

```
