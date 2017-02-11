use microwave;
BEGIN;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE `app_user_tracks`;
TRUNCATE `app_track`;
TRUNCATE `app_user`;
SET FOREIGN_KEY_CHECKS = 1;
COMMIT;