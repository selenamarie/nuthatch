
High level:
* Return JSON for everything (consider csv)
* Read only transactions
* Refresh a maximum of every minute

API design: 
/database/queries/new
* POST SQL, return URL for getting data
 * options: run_once (otherwise, re-run query every time we post)
 * not updateable, if you made a mistake in the query, re-post to /new to get a new URL

/database/queries
* GET list of queries you have access to

/database/queries/[id]
* GET result
* DELETE to delete this query

/database/queries/[id]/run
* POST to re-run (if run_once is not set)

/database/queries/[id]/status
* GET tells us if a query is started/waiting (enqueued but not started)/finished (timestamp)

/database/queries/[id]/settings
* GET settings (exact query, run_once)

/database/schemas
* GET schema


Errors:
* Re-running a job too quickly
* Job already running, can't re-run yet
* Query doesn't parse 
* Query takes too long to run
