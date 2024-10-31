# apps/users/tests/test_config.py - Add these if not present

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

TEST_USER = {
    'email': 'test@example.com',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'User'
}

TEST_ADMIN = {
    'email': 'admin@example.com',
    'password': 'adminpass123',
    'first_name': 'Admin',
    'last_name': 'User',
    'is_staff': True,
    'is_superuser': True
}