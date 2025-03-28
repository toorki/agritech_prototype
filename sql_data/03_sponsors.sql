-- Delete existing buyer profiles for these users if they exist
DELETE FROM marketplace_buyer WHERE user_id IN (
    (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor'),
    (SELECT id FROM auth_user WHERE username = 'jihad_sponsor'),
    (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')
);

-- SQL Insert statements for Buyer profiles (for sponsors)
INSERT INTO marketplace_buyer (user_id, phone_number, location, created_at, updated_at)
VALUES 
((SELECT id FROM auth_user WHERE username = 'ahmed_sponsor'), '+216 55 123 456', 'Tunis', datetime('now'), datetime('now')),
((SELECT id FROM auth_user WHERE username = 'jihad_sponsor'), '+216 55 789 012', 'Tunis', datetime('now'), datetime('now')),
((SELECT id FROM auth_user WHERE username = 'houssem_sponsor'), '+216 56 432 109', 'Bizerte', datetime('now'), datetime('now'));
