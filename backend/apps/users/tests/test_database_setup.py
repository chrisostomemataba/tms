from django.test import TransactionTestCase, override_settings
from django.db import connection
from django.contrib.auth import get_user_model
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

@override_settings(ROOT_URLCONF='apps.users.tests.urls')
class InitialDatabaseTest(TransactionTestCase):
    """Initial database setup verification"""
    
    def setUp(self):
        super().setUp()
        self.db_name = connection.settings_dict['NAME']
        logger.info(f"Testing with database: {self.db_name}")

    def test_01_database_connection(self):
        """Verify basic database connection"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.assertEqual(cursor.fetchone()[0], 1)
                logger.info("✓ Basic database connection successful")

                # Check if we're using test database
                cursor.execute("SELECT current_database();")
                current_db = cursor.fetchone()[0]
                self.assertTrue(
                    'test' in current_db,
                    "Not using test database!"
                )
                logger.info(f"✓ Using test database: {current_db}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def test_02_user_table_structure(self):
        """Verify user table structure"""
        try:
            with connection.cursor() as cursor:
                # Check if users table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users_user'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                self.assertTrue(table_exists, "Users table does not exist")
                logger.info("✓ Users table exists")

                # Check required columns
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users_user';
                """)
                columns = {col[0]: col[1] for col in cursor.fetchall()}
                logger.info(f"Found columns: {columns}")
                
                required_columns = [
                    'id', 'email', 'first_name', 'last_name', 
                    'is_active', 'role', 'created_at'
                ]

                for col in required_columns:
                    self.assertIn(
                        col, 
                        columns, 
                        f"Missing required column: {col}"
                    )
                logger.info("✓ User table structure verified")
        except Exception as e:
            logger.error(f"Table structure check failed: {e}")
            raise

    def test_03_basic_user_creation(self):
        """Test basic user model operation"""
        try:
            test_email = 'test@example.com'
            user = User.objects.create_user(
                email=test_email,
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            
            # Verify user creation
            self.assertEqual(user.email, test_email)
            self.assertTrue(user.check_password('testpass123'))
            
            # Verify profile creation
            self.assertTrue(hasattr(user, 'profile'))
            logger.info("✓ User creation and profile auto-creation successful")
            
            # Verify in database
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT email FROM users_user WHERE email = %s",
                    [test_email]
                )
                result = cursor.fetchone()
                self.assertIsNotNone(result)
                self.assertEqual(result[0], test_email)
            logger.info("✓ User verified in database")
            
        except Exception as e:
            logger.error(f"User creation test failed: {e}")
            raise

    def tearDown(self):
        logger.info(f"Completed database setup tests for {self.db_name}")
        super().tearDown()