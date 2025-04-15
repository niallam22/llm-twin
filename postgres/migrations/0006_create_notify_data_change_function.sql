-- Function to send notification on data change
CREATE OR REPLACE FUNCTION notify_data_change()
RETURNS TRIGGER AS $$
DECLARE
  payload JSONB;
  notification_channel TEXT := 'data_changes'; -- Channel name
BEGIN
  -- Construct the JSON payload including table name, operation type, and new row data
  payload := jsonb_build_object(
    'table', TG_TABLE_NAME,
    'operation', TG_OP, -- INSERT, UPDATE, DELETE
    'data', row_to_json(NEW)::JSONB -- Use NEW for INSERT/UPDATE
  );

  -- Send notification
  PERFORM pg_notify(notification_channel, payload::TEXT);

  RETURN NEW; -- Return value is ignored for AFTER triggers, but required syntax
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION notify_data_change() IS 'Sends a JSON payload notification on the data_changes channel upon data insertion.';