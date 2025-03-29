-- Insert Buyer profiles into marketplace_buyer
INSERT INTO marketplace_buyer (user_id, phone_number, location, created_at, updated_at)
VALUES 
((SELECT id FROM auth_user WHERE username = 'ahmed_sponsor'), '+216 99 111 222', 'Tunis', '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
((SELECT id FROM auth_user WHERE username = 'jihad_sponsor'), '+216 99 222 333', 'Sfax', '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
((SELECT id FROM auth_user WHERE username = 'houssem_sponsor'), '+216 99 333 444', 'Bizerte', '2023-01-01 00:00:00', '2023-01-01 00:00:00');