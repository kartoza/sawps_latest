from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from property.models import Province
from regulatory_permit.models import DataUsePermission
from stakeholder.factories import (
    loginStatusFactory,
    organisationFactory,
    organisationRepresentativeFactory,
    organisationUserFactory,
    userLoginFactory,
    userProfileFactory,
    userRoleTypeFactory,
    userTitleFactory,
)
from stakeholder.models import (
    LoginStatus,
    Organisation,
    OrganisationInvites,
    OrganisationRepresentative,
    OrganisationUser,
    Reminders,
    UserLogin,
    UserProfile,
    UserRoleType,
    UserTitle,
)


class TestUserRoleType(TestCase):
    """Test user's role type model."""

    @classmethod
    def setUpTestData(cls):
        cls.UserRoleTypeFactory = userRoleTypeFactory()

    def test_create_new_role(self):
        """Test creating new role."""
        self.assertEqual(UserRoleType.objects.count(), 1)
        self.assertTrue(
            self.UserRoleTypeFactory.name
            in ['base user', 'admin', 'super user']
        )

    def test_update_role(self):
        """Test updating a role."""
        self.UserRoleTypeFactory.name = 'admin'
        self.UserRoleTypeFactory.save()
        UserRoleObject = UserRoleType.objects.get(
            id=self.UserRoleTypeFactory.id
        )
        self.assertEqual(UserRoleObject.name, 'admin')

    def test_delete_role(self):
        """Test deleting new role."""
        self.UserRoleTypeFactory.delete()
        self.assertEqual(UserRoleType.objects.count(), 0)


class UserTitleTestCase(TestCase):
    """User title test case."""

    @classmethod
    def setUpTestData(cls):
        cls.userTitle = userTitleFactory()

    def test_create_new_title(self):
        """Test creating new title."""
        self.assertEqual(UserTitle.objects.count(), 1)
        self.assertTrue(self.userTitle.name in ['mr', 'mrs', 'miss', 'dr'])

    def test_update_title(self):
        """Test updating a title."""
        self.userTitle.name = 'mr'
        userTitle = UserTitle.objects.get(id=self.userTitle.id)
        self.assertTrue(userTitle.name, 'mr')

    def test_delete_new_title(self):
        """Test deleting a title."""
        self.userTitle.delete()
        self.assertEqual(UserTitle.objects.count(), 0)


class LoginStatusTestCase(TestCase):
    """User login status test case."""

    @classmethod
    def setUpTestData(cls):
        cls.loginStatus = loginStatusFactory()

    def test_create_login_status(self):
        """Test creating login status."""
        self.assertEqual(LoginStatus.objects.count(), 1)
        self.assertTrue(
            isinstance(self.loginStatus, LoginStatus)
        )
        self.assertTrue(self.loginStatus.name in ['logged in', 'logged out'])

    def test_update_login_status(self):
        """Test updating a login status."""
        self.loginStatus.name = 'logged in'
        loginStatus = LoginStatus.objects.get(
            id=self.loginStatus.id
        )
        self.assertTrue(loginStatus.name, 'logged in')
        self.loginStatus.name = 'logged out'
        loginStatus = LoginStatus.objects.get(
            id=self.loginStatus.id
        )
        self.assertTrue(loginStatus.name, 'logged out')

    def test_delete_login_status(self):
        """Test deleting a login status."""
        self.loginStatus.delete()
        self.assertEqual(LoginStatus.objects.count(), 0)


class TestUser(TestCase):
    """Test the main user model relation to the profie model."""

    @classmethod
    def setUpTestData(cls):
        cls.profileFactory = userProfileFactory()

    def test_create_new_user_with_new_profile(self):
        """Test creating new user when new profile is created."""
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(
            User.objects.count(), 2
        )  # Anon user is created by default

    def test_update_user_profile(self):
        """Test updating user through profile."""
        self.profileFactory.user.username = 'test'
        self.profileFactory.user.first_name = 'test123'
        self.profileFactory.user.save()
        self.assertEqual(
            User.objects.get(username='test').first_name, 'test123'
        )

    def test_delete_role(self):
        """Test deleting user when a profile is deleted."""
        self.profileFactory.delete()
        self.assertEqual(User.objects.count(), 1)


class TestUserLogin(TestCase):
    """"User login testcase."""

    @classmethod
    def setUpTestData(cls):
        cls.user_login = userLoginFactory()

    def create_user_login(self):
        """Test creating new user login."""
        self.assertEqual(UserLogin.objects.count(), 1)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user_login(self):
        """Test updating user login."""
        self.user_login.login_status.name = 'logged out'
        self.user_login.login_status.save()
        self.assertEqual(
            UserLogin.objects.get(id=self.user_login.id).login_status.name,
            'logged out'
        )

    def test_delete_user_login(self):
        """Test deleting user login."""
        self.user_login.delete()
        self.assertEqual(UserLogin.objects.count(), 0)
        self.assertEqual(User.objects.count(), 2)


class OrganizationTestCase(TestCase):
    """Organization test case."""

    @classmethod
    def setUpTestData(cls):
        cls.organization = organisationFactory()

    def test_create_organization(self):
        """Test creating organization."""
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertTrue(isinstance(self.organization, Organisation))
        self.assertTrue(self.organization.name, Organisation.objects.get(
            id=self.organization.id).name)

    def test_update_organization(self):
        """Test updating organization."""
        province, created = Province.objects.get_or_create(
                    name="Limpopo"
        )
        self.organization.name = 'test'
        self.organization.national = True
        self.organization.province = province
        self.organization.save()
        self.assertEqual(Organisation.objects.get(
            id=self.organization.id).name, 'test')
        self.assertEqual(Organisation.objects.filter(
            national=True).count(), 1)
        self.assertEqual(Organisation.objects.filter(
            province__name="Limpopo").count(), 1)

    def test_delete_organization(self):
        """Test deleting organization."""
        self.organization.delete()
        self.assertEqual(Organisation.objects.count(), 0)


class OrganizationUserTestCase(TestCase):
    """Test case for organization user."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    @classmethod
    def setUpTestData(cls):
        """Setup test data for organisation user model."""
        cls.organizationUser = organisationUserFactory()

    def test_create_organisation_user(self):
        """Test creating organisation user."""
        self.assertEqual(OrganisationUser.objects.count(), 1)
        self.assertTrue(isinstance(self.organizationUser, OrganisationUser))

    def test_update_organisation_user(self):
        """ Test updating organisation user."""
        self.organizationUser.user.username = 'test'
        self.organizationUser.user.save()
        self.assertEqual(
            self.organizationUser.user.username,
            'test'
        )

    def test_delete_organisation_user(self):
        """Test deleting organisation user."""
        self.organizationUser.delete()
        self.assertEqual(OrganisationUser.objects.count(), 0)


class OrganizationRepresentativeTestCase(TestCase):
    """Test case for organization representative."""

    @classmethod
    def setUpTestData(cls):
        """Setup test data for organisation representative model."""
        cls.organizationRep = organisationRepresentativeFactory()

    def test_create_organisation_user(self):
        """Test creating organisation representative."""
        self.assertEqual(OrganisationRepresentative.objects.count(), 1)
        self.assertTrue(
            isinstance(
                self.organizationRep,
                OrganisationRepresentative
            )
        )

    def test_update_organisation_user(self):
        """ Test updating organisation representative."""
        self.organizationRep.user.username = 'test'
        self.organizationRep.user.save()
        self.assertEqual(
            self.organizationRep.user.username,
            'test'
        )

    def test_delete_organisation_user(self):
        """Test deleting organisation representative."""
        self.organizationRep.delete()
        self.assertEqual(OrganisationRepresentative.objects.count(), 0)


class OrganisationInvitesModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.data_use_permission = DataUsePermission.objects.create(
            name="test")
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )
        self.organisation_user = OrganisationUser.objects.create(
            organisation=self.organisation,
            user=self.user
        )

    def test_create_organisation_invite(self):
        """Test create organisation invite."""
        invite = OrganisationInvites.objects.create(
            organisation=self.organisation, email='test@kartoza.com')
        self.assertEqual(invite.organisation, self.organisation)
        self.assertEqual(invite.email, 'test@kartoza.com')

    def test_read_organisation_invite(self):
        """Test read organisation invite."""
        invite = OrganisationInvites.objects.create(
            organisation=self.organisation, email='test@kartoza.com')
        saved_invite = OrganisationInvites.objects.get(pk=invite.pk)
        self.assertEqual(saved_invite.organisation, self.organisation)
        self.assertEqual(saved_invite.email, 'test@kartoza.com')

    def test_update_organisation_invite(self):
        """Test update organisation invite."""
        invite = OrganisationInvites.objects.create(
            organisation=self.organisation, email='test@kartoza.com')
        invite.organisation = self.organisation
        invite.save()
        updated_invite = OrganisationInvites.objects.get(pk=invite.pk)
        self.assertEqual(updated_invite.organisation, self.organisation)

    def test_delete_organisation_invite(self):
        """Test delete organisation invite."""
        invite = OrganisationInvites.objects.create(
            organisation=self.organisation, email='test@kartoza.com')
        invite.delete()
        self.assertFalse(
            OrganisationInvites.objects.filter(pk=invite.pk).exists())


class RemindersModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )
        self.organisation_user = OrganisationUser.objects.create(
            organisation=self.organisation,
            user=self.user
        )
        self.reminder = Reminders.objects.create(
            title='test',
            user=self.user,
            organisation=self.organisation,
            reminder='reminder'
        )

    def test_create_reminder(self):
        reminder = Reminders.objects.create(
            organisation=self.organisation,
            user=self.user
        )
        self.assertEqual(reminder.organisation, self.organisation)
        self.assertEqual(reminder.user, self.user)

    def test_get_reminder(self):
        reminder = Reminders.objects.get(
            organisation=self.organisation,
            user=self.user
        )
        self.assertEqual(reminder.organisation, self.organisation)
        self.assertEqual(reminder.title, self.reminder.title)

    def test_update_reminder(self):
        reminder = Reminders.objects.get(
            organisation=self.organisation,
            user=self.user
        )
        reminder.title = 'new'
        reminder.save()
        self.assertEqual(reminder.title, 'new')

    def test_delete_reminder_or_notif(self):
        reminder = Reminders.objects.get(
            organisation=self.organisation,
            user=self.user
        )
        reminder.delete()
        self.assertEqual(
            Reminders.objects.filter(
                user=self.user,
                organisation=self.organisation
            ).exists(), False)

    def test_search_remider_or_notification(self):
        reminders = Reminders.objects.filter(
            Q(user=self.user),
            Q(organisation=self.organisation),
            Q(title__icontains='t') | Q(
                reminder__icontains='t')
        )

        self.assertEqual(len(reminders), 1)
