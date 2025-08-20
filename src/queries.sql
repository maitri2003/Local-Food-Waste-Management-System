-- 1. Number of providers and receivers in each city
SELECT city, COUNT(DISTINCT provider_id) AS num_providers
FROM providers GROUP BY city;

SELECT city, COUNT(DISTINCT receiver_id) AS num_receivers
FROM receivers GROUP BY city;

-- 2. Type of provider contributing the most by quantity
SELECT provider_type, SUM(quantity) AS total_qty
FROM food_listings
GROUP BY provider_type
ORDER BY total_qty DESC
LIMIT 1;

-- 3. Contact info of providers in a given city
SELECT name, contact, address
FROM providers
WHERE city = 'Mumbai';

-- 4. Receivers with most claims
SELECT r.receiver_id, r.name, COUNT(c.claim_id) AS claims_count
FROM claims c
JOIN receivers r ON c.receiver_id = r.receiver_id
GROUP BY r.receiver_id
ORDER BY claims_count DESC;

-- 5. Total quantity of food available
SELECT SUM(quantity) AS total_quantity FROM food_listings;

-- 6. City with highest number of food listings
SELECT location, COUNT(*) AS num_listings
FROM food_listings
GROUP BY location
ORDER BY num_listings DESC
LIMIT 1;

-- 7. Most common food types
SELECT food_type, COUNT(*) AS type_count
FROM food_listings
GROUP BY food_type
ORDER BY type_count DESC;

-- 8. Claims per food item
SELECT f.food_id, f.food_name, COUNT(c.claim_id) AS claim_count
FROM food_listings f
LEFT JOIN claims c ON f.food_id = c.food_id
GROUP BY f.food_id;

-- 9. Provider with highest number of completed claims
SELECT p.provider_id, p.name, COUNT(c.claim_id) AS completed_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN providers p ON f.provider_id = p.provider_id
WHERE c.status = 'Completed'
GROUP BY p.provider_id
ORDER BY completed_claims DESC
LIMIT 1;

-- 10. Percentage of claims by status
SELECT status,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
FROM claims
GROUP BY status;

-- 11. Average quantity claimed per receiver
SELECT r.receiver_id, r.name, AVG(f.quantity) AS avg_quantity
FROM claims c
JOIN receivers r ON c.receiver_id = r.receiver_id
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY r.receiver_id;

-- 12. Meal type claimed the most
SELECT f.meal_type, COUNT(c.claim_id) AS claim_count
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY f.meal_type
ORDER BY claim_count DESC
LIMIT 1;

-- 13. Total quantity donated by each provider
SELECT p.provider_id, p.name, SUM(f.quantity) AS total_donated
FROM providers p
JOIN food_listings f ON p.provider_id = f.provider_id
GROUP BY p.provider_id
ORDER BY total_donated DESC;

-- 14. Food expiring in next 3 days
SELECT * FROM food_listings
WHERE expiry_date BETWEEN DATE('now') AND DATE('now', '+3 days')
ORDER BY expiry_date;

-- 15. Top receivers by total quantity claimed
SELECT r.receiver_id, r.name, SUM(f.quantity) AS total_claimed
FROM claims c
JOIN receivers r ON c.receiver_id = r.receiver_id
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY r.receiver_id
ORDER BY total_claimed DESC;
