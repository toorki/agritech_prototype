-- SQL Insert statements for Orders
INSERT INTO marketplace_order (buyer_id, produce_id, quantity, unit_price, platform_fee, total_amount, status, delivery_location, delivery_notes, created_at, updated_at)
VALUES 
-- Order for Salah's olives
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) LIMIT 1),
 200, 2.0, 8.0, 408.0, 'completed', 'Tunis', 'Standard delivery', datetime('now', '-2 weeks'), datetime('now', '-2 weeks')),

-- Order for Mohamed's potatoes
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor')),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'mohamed_farmer'))LIMIT 1),
 500, 1.0, 10.0, 510.0, 'completed', 'Tunis', 'Standard delivery', datetime('now', '-3 weeks'), datetime('now', '-3 weeks')),

-- Order for Abd el Hamid's dates
((SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')),
 (SELECT id FROM marketplace_produce WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer'))LIMIT 1),
 1000, 2.5, 50.0, 2550.0, 'processing', 'Bizerte', 'Standard delivery', datetime('now', '-1 week'), datetime('now', '-1 week'));

-- SQL Insert statements for Sponsorship Payments
INSERT INTO marketplace_sponsorshippayment (sponsorship_id, amount, payment_type, transaction_id, payment_date)
VALUES 
-- Payment for Salah's sponsorship with Ahmed
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 1000, 'investment', 'TRX123456789', datetime('now', '-1 month')),

-- Payment for Salah's sponsorship with Jihad
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor')),
 2000, 'investment', 'TRX987654321', datetime('now', '-2 months')),

-- Payment for Abd el Hamid's sponsorship with Houssem
((SELECT id FROM marketplace_sponsorship WHERE farmer_id = (SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')) AND sponsor_id = (SELECT id FROM auth_user WHERE username = 'houssem_sponsor')),
 5000, 'investment', 'TRX567891234', datetime('now', '-3 months'));

-- SQL Insert statements for Ratings (simplified)
INSERT INTO marketplace_rating (farmer_id, buyer_id, order_id, score, comment, created_at)
VALUES 
-- Rating for Salah from Ahmed
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')),
 (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')),
 (SELECT id FROM marketplace_order WHERE buyer_id = (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'ahmed_sponsor')) LIMIT 1),
 5, 'Excellent quality olives, very satisfied with the purchase', datetime('now', '-1 week')),

-- Rating for Mohamed from Jihad
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'mohamed_farmer')),
 (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor')),
 (SELECT id FROM marketplace_order WHERE buyer_id = (SELECT id FROM marketplace_buyer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'jihad_sponsor')) LIMIT 1),
 5, 'Great potatoes, delivered on time and in perfect condition', datetime('now', '-2 weeks'));
