-- SQL Insert statements for Product Categories
INSERT INTO marketplace_producecategory (name, description)
VALUES 
('Fruits', 'Fresh fruits grown in Tunisia'),
('Vegetables', 'Fresh vegetables grown in Tunisia'),
('Dates', 'Premium Tunisian dates'),
('Olives', 'High-quality Tunisian olives');

-- SQL Insert statements for Farmer profiles
INSERT INTO marketplace_farmer (user_id, phone_number, location, rating, total_ratings, created_at, updated_at)
VALUES 
((SELECT id FROM auth_user WHERE username = 'salah_farmer'), '+216 98 765 432', 'Sfax', 5.0, 10, datetime('now'), datetime('now')),
((SELECT id FROM auth_user WHERE username = 'mohamed_farmer'), '+216 98 123 456', 'Beja', 5.0, 8, datetime('now'), datetime('now')),
((SELECT id FROM auth_user WHERE username = 'houssin_farmer'), '+216 97 654 321', 'Nabeul', 3.0, 5, datetime('now'), datetime('now')),
((SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer'), '+216 99 888 777', 'Tozeur', 4.0, 12, datetime('now'), datetime('now'));

-- SQL Insert statements for Produce items
INSERT INTO marketplace_produce (farmer_id, category_id, title, description, quantity, unit, price_per_unit, location, is_available, created_at, updated_at)
VALUES 
((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'salah_farmer')),
 (SELECT id FROM marketplace_producecategory WHERE name = 'Olives'),
 'Premium Olives', 'High-quality olives harvested at peak ripeness, perfect for oil production or table consumption', 
 1000, 'kg', 2.0, 'Sfax', 1, datetime('now'), datetime('now')),

((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'mohamed_farmer')),
 (SELECT id FROM marketplace_producecategory WHERE name = 'Vegetables'),
 'Fresh Potatoes', 'Locally grown potatoes, perfect for cooking and frying. Harvested recently for maximum freshness', 
 2000, 'kg', 1.0, 'Beja', 1, datetime('now'), datetime('now')),

((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'houssin_farmer')),
 (SELECT id FROM marketplace_producecategory WHERE name = 'Fruits'),
 'Sweet Oranges', 'Juicy and sweet oranges grown in the fertile soil of Nabeul. Rich in vitamin C and perfect for juicing', 
 1500, 'kg', 3.0, 'Nabeul', 1, datetime('now'), datetime('now')),

((SELECT id FROM marketplace_farmer WHERE user_id = (SELECT id FROM auth_user WHERE username = 'abdelhamid_farmer')),
 (SELECT id FROM marketplace_producecategory WHERE name = 'Dates'),
 'Premium Dates', 'High-quality dates from Tozeur, known for their sweetness and soft texture. Perfect for direct consumption or cooking', 
 5000, 'kg', 2.5, 'Tozeur', 1, datetime('now'), datetime('now'));
