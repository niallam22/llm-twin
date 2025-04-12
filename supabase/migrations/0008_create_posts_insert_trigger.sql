-- Trigger for posts table on INSERT
CREATE TRIGGER posts_insert_trigger
AFTER INSERT ON public.posts -- Ensure schema is specified if needed
FOR EACH ROW
EXECUTE FUNCTION notify_data_change();

COMMENT ON TRIGGER posts_insert_trigger ON public.posts IS 'Calls notify_data_change() after a new row is inserted into posts.';