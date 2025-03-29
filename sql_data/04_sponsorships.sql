-- Insert Sponsor profiles into marketplace_sponsor (skip if already exists)
INSERT OR IGNORE INTO marketplace_sponsor (user_id, phone_number, organization, created_at, updated_at)
VALUES 
((SELECT id FROM auth_user WHERE username = 'ahmed_sponsor'), '+216 99 111 222', 'GreenFuture', '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
((SELECT id FROM auth_user WHERE username = 'jihad_sponsor'), '+216 99 222 333', 'EcoInvest', '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
((SELECT id FROM auth_user WHERE username = 'houssem_sponsor'), '+216 99 333 444', 'AgriSupport', '2023-01-01 00:00:00', '2023-01-01 00:00:00');

-- SQL Insert statements for Sponsorships
INSERT INTO marketplace_sponsorship (farmer_id, sponsor_id, title, description, amount_requested, expected_yield, expected_completion_date, status, created_at)
VALUES 
-- Salah's olive sponsorship with Ahmed
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1),
 'Olive Harvest Expansion', 
 'Funding needed to expand olive production and implement improved harvesting techniques',
 1000, 500, '2023-07-01', 'active', '2023-01-01 00:00:00'),

-- Salah's olive sponsorship with Jihad
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1),
 'Organic Olive Certification', 
 'Investment to obtain organic certification for premium olive production',
 2000, 1000, '2023-09-01', 'active', '2023-01-01 00:00:00'),

-- Abd el Hamid's date sponsorship with Houssem
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1),
 'Date Palm Expansion Project', 
 'Funding to plant additional date palms and improve irrigation systems',
 5000, 2500, '2024-01-01', 'active', '2023-01-01 00:00:00');

-- SQL Insert statements for Sponsorship Milestones
INSERT INTO marketplace_sponsorshipmilestone (sponsorship_id, title, description, due_date, status, verification_notes, verified_by_id)
VALUES
-- Milestones for Salah's sponsorship with Ahmed
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1) LIMIT 1),
 'Land Preparation', 
 'Prepare additional land for olive tree planting',
 '2023-02-01', 
 'completed', 
 'Land successfully prepared with proper drainage systems installed',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1) LIMIT 1),
 'Tree Planting', 
 'Plant new olive tree saplings',
 '2023-03-01', 
 'pending', 
 '',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1) LIMIT 1),
 'Harvest', 
 'Complete olive harvest',
 '2023-07-01', 
 'pending', 
 '',
 NULL),

-- Milestones for Abd el Hamid's sponsorship with Houssem
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1) LIMIT 1),
 'Irrigation System Installation', 
 'Install improved drip irrigation system',
 '2023-03-01', 
 'completed', 
 'Modern drip irrigation system successfully installed',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1) LIMIT 1),
 'Palm Planting', 
 'Plant additional date palm trees',
 '2023-05-01', 
 'pending', 
 '',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1) LIMIT 1),
 'First Harvest', 
 'Complete first harvest from new trees',
 '2024-01-01', 
 'pending', 
 '',
 NULL);