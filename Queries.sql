USE search_restaurants;
CREATE TABLE restaurants_details (
	name VARCHAR(40)
    ,place_id VARCHAR(40) PRIMARY KEY
    ,business_status VARCHAR(30)
    ,location VARCHAR (30)
    ,raiting int
    ,price_level double
    ,total_reviews bigint
    ,direction VARCHAR(80)
);

CREATE TABLE restaurants_reviews (
	review_id INT PRIMARY KEY
    ,place_id VARCHAR(40),
    review_text VARCHAR(10000)
);