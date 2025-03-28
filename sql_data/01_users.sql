-- Delete existing test users if they exist
DELETE FROM auth_user WHERE username IN ('salah_farmer', 'mohamed_farmer', 'houssin_farmer', 'abdelhamid_farmer', 'ahmed_sponsor', 'jihad_sponsor', 'houssem_sponsor');

-- Create User accounts for Farmers
INSERT INTO auth_user (username, first_name, last_name, email, password, is_staff, is_active, is_superuser, date_joined)
VALUES 
('salah_farmer', 'Salah', 'Ben Ali', 'salah@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now')),
('mohamed_farmer', 'Mohamed', 'Trabelsi', 'mohamed@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now')),
('houssin_farmer', 'Houssin', 'Mejri', 'houssin@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now')),
('abdelhamid_farmer', 'Abd el Hamid', 'Karoui', 'abdelhamid@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now'));

-- Create User accounts for Sponsors
INSERT INTO auth_user (username, first_name, last_name, email, password, is_staff, is_active, is_superuser, date_joined)
VALUES 
('ahmed_sponsor', 'Ahmed', 'Bouazizi', 'ahmed@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now')),
('jihad_sponsor', 'Jihad', 'Khelifi', 'jihad@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now')),
('houssem_sponsor', 'Houssem', 'Lahmar', 'houssem@example.com', 'pbkdf2_sha256$260000$abcdefghijklmnopqrstuvwxyz123456789', 0, 1, 0, datetime('now'));
