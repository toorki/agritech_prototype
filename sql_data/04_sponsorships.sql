-- SQL Insert statements for Sponsorships
INSERT INTO marketplace_sponsorship (farmer_id, sponsor_id, title, description, amount_requested, expected_yield, expected_completion_date, status, created_at)
VALUES 
-- Salah's olive sponsorship with Ahmed
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')),
 (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor'),
 'Olive Harvest Expansion', 
 'Funding needed to expand olive production and implement improved harvesting techniques',
 1000, 500, datetime('now', '+6 months'), 'active', datetime('now')),

-- Salah's olive sponsorship with Jihad
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')),
 (SELECT id FROM auth_user WHERE username = 'jihad_sponsor'),
 'Organic Olive Certification', 
 'Investment to obtain organic certification for premium olive production',
 2000, 1000, datetime('now', '+8 months'), 'active', datetime('now')),

-- Abd el Hamid's date sponsorship with Houssem
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')),
 (SELECT id FROM auth_user WHERE username = 'houssem_sponsor'),
 'Date Palm Expansion Project', 
 'Funding to plant additional date palms and improve irrigation systems',
 5000, 2500, datetime('now', '+12 months'), 'active', datetime('now'));

-- SQL Insert statements for Sponsorship Milestones
INSERT INTO marketplace_sponsorshipmilestone (sponsorship_id, title, description, due_date, status, verification_notes, verified_by_id)
VALUES
-- Milestones for Salah's sponsorship with Ahmed
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 'Land Preparation', 
 'Prepare additional land for olive tree planting',
 datetime('now', '+1 month'), 
 'completed', 
 'Land successfully prepared with proper drainage systems installed',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 'Tree Planting', 
 'Plant new olive tree saplings',
 datetime('now', '+2 months'), 
 'pending', 
 '',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 'Harvest', 
 'Complete olive harvest',
 datetime('now', '+6 months'), 
 'pending', 
 '',
 NULL),

-- Milestones for Abd el Hamid's sponsorship with Houssem
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')),
 'Irrigation System Installation', 
 'Install improved drip irrigation system',
 datetime('now', '+2 months'), 
 'completed', 
 'Modern drip irrigation system successfully installed',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')),
 'Palm Planting', 
 'Plant additional date palm trees',
 datetime('now', '+4 months'), 
 'pending', 
 '',
 NULL),

((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')),
 'First Harvest', 
 'Complete first harvest from new trees',
 datetime('now', '+12 months'), 
 'pending', 
 '',
 NULL);
