MERGE `data-engineering-479617.issues_ds.issues_current` T
USING (
  SELECT
    issue_id,
    new_status AS status,
    priority,
    source,
    changed_at AS updated_at
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (
             PARTITION BY issue_id
             ORDER BY changed_at DESC
           ) AS rn
    FROM `data-engineering-479617.issues_ds.issues_status_history`
  )
  WHERE rn = 1
) S
ON T.issue_id = S.issue_id

WHEN MATCHED THEN
  UPDATE SET
    status = S.status,
    priority = S.priority,
    source = S.source,
    updated_at = S.updated_at

WHEN NOT MATCHED THEN
  INSERT (issue_id, status, priority, source, updated_at)
  VALUES (issue_id, status, priority, source, updated_at);
