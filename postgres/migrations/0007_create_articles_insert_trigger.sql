-- Trigger for articles table on INSERT
DROP TRIGGER IF EXISTS articles_insert_trigger ON articles;
CREATE TRIGGER articles_insert_trigger
AFTER INSERT ON articles
FOR EACH ROW
EXECUTE FUNCTION notify_data_change();

COMMENT ON TRIGGER articles_insert_trigger ON articles IS 'Calls notify_data_change() after a new row is inserted into articles.';