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
DROP TABLE restaurants_reviews;
CREATE TABLE restaurants_reviews (
	review_id INT PRIMARY KEY
    ,place_id VARCHAR(40)
    ,review_text VARCHAR(10000)
    ,review_rate int
    ,review_time bigint
);

CREATE TABLE restaurants_more_details (
	place_id INT PRIMARY KEY
    ,dine_in boolean
    ,reservable boolean
    ,serves_beer boolean
    ,serves_wine boolean
    ,vegeterian boolean
    ,takeout boolean
    ,wheel_chair_acc boolean
    ,mon_hours varchar(30)
    ,tue_hours varchar(30)
    ,wed_hours varchar(30)
    ,thu_hours varchar(30)
    ,fri_hours varchar(30)
    ,sat_hours varchar(30)
    ,sun_hours varchar(30)
);
