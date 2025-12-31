import os
from agentset import Agentset

a = Agentset(
  namespace_id="ns_123",
  token=os.environ['AGENTSET_API_KEY'],
)

res = a.ingest_jobs.create(
  payload={
    "type": "FILE",
    "fileUrl": "https://example.com/annual-report-2024.pdf",
    "name": "Annual Report 2024",
  },
  config={
    "metadata": {
      "documentType": "financial",
      "year": 2024,
    },
  },
)

print(f"Job created with ID: {res.data.id}")