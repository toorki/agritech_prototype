-- SQL Insert statements for Orders
INSERT INTO marketplace_order (buyer_id, produce_id, quantity, unit_price, platform_fee, total_amount, status, delivery_location, delivery_notes, created_at, updated_at)
VALUES 
-- Order for Salah's olives
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) LIMIT 1),
 200, 2.0, 8.0, 408.0, 'completed', 'Tunis', 'Standard delivery', '2023-03-14 00:00:00', '2023-03-14 00:00:00'),

-- Order for Mohamed's potatoes
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'mohamed_farmer') LIMIT 1) LIMIT 1),
 500, 1.0, 10.0, 510.0, 'completed', 'Tunis', 'Standard delivery', '2023-03-07 00:00:00', '2023-03-07 00:00:00'),

-- Order for Abd el Hamid's dates
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1) LIMIT 1),
 1000, 2.5, 50.0, 2550.0, 'processing', 'Bizerte', 'Standard delivery', '2023-03-21 00:00:00', '2023-03-21 00:00:00');

-- SQL Insert statements for Sponsorship Payments
INSERT INTO marketplace_sponsorshippayment (sponsorship_id, sponsor_id, amount, payment_type, transaction_id, payment_date)
VALUES 
-- Payment for Salah's sponsorship with Ahmed
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1) LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1),
 1000, 'investment', 'TRX123456789', '2023-02-28 00:00:00'),

-- Payment for Salah's sponsorship with Jihad
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1) LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1),
 2000, 'investment', 'TRX987654321', '2023-01-28 00:00:00'),

-- Payment for Abd el Hamid's sponsorship with Houssem
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer') LIMIT 1) AND sponsor_id = (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1) LIMIT 1),
 (SELECT id FROM marketplace_sponsor WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor') LIMIT 1),
 5000, 'investment', 'TRX567891234', '2022-12-28 00:00:00');

-- SQL Insert statements for Ratings
INSERT INTO marketplace_rating (farmer_id, buyer_id, order_id, score, comment, created_at)
VALUES 
-- Rating for Salah from Ahmed
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer') LIMIT 1),
 (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1),
 (SELECT id FROM marketplace_order WHERE buyer_id = (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor') LIMIT 1) LIMIT 1),
 5, 'Excellent quality olives, very satisfied with the purchase', '2023-03-21 00:00:00'),

-- Rating for Mohamed from Jihad
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'mohamed_farmer') LIMIT 1),
 (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1),
 (SELECT id FROM marketplace_order WHERE buyer_id = (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor') LIMIT 1) LIMIT 1),
 5, 'Great potatoes, delivered on time and in perfect condition', '2023-03-14 00:00:00');