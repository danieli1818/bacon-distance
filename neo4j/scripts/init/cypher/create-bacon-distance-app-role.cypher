CREATE ROLE bacon_distance_app_role;
GRANT READ, WRITE ON DATABASE movies_db TO bacon_distance_app_role;
GRANT CREATE RELATIONSHIP ON DATABASE movies_db TO bacon_distance_app_role;
