INSERT INTO users (id, first_name, last_name, email, password, is_admin, created_at, updated_at)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$LJ3m4ys3GnXLbpFP5z7UfOJPDYXnJMfSCL93hG1XkOzMSHxRqWaHW',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT INTO amenities (id, name, created_at, updated_at)
VALUES
    ('6fa459ea-ee8a-3ca4-894e-db77e160355e', 'WiFi', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b', 'Swimming Pool', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('3c6e0b8a-9c0a-45b7-b6e0-4a7c1c8b2f3d', 'Air Conditioning', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);