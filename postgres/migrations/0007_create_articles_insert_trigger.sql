-- Trigger for articles table on INSERT
CREATE TRIGGER articles_insert_trigger
AFTER INSERT ON public.articles -- Ensure schema is specified if needed
FOR EACH ROW
EXECUTE FUNCTION notify_data_change();

COMMENT ON TRIGGER articles_insert_trigger ON public.articles IS 'Calls notify_data_change() after a new row is inserted into articles.';