-- Trigger for repositories table on INSERT
CREATE TRIGGER repositories_insert_trigger
AFTER INSERT ON public.repositories -- Ensure schema is specified if needed
FOR EACH ROW
EXECUTE FUNCTION notify_data_change();

COMMENT ON TRIGGER repositories_insert_trigger ON public.repositories IS 'Calls notify_data_change() after a new row is inserted into repositories.';