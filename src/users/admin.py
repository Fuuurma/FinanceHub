from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from users.models.user import User
from users.models.account_type import AccountType
from users.models.permission import Permission
from users.models.role import Role
from users.models.session import LoginHistory
from users.models.session import LoginHistory
from users.models.user_profile import UserProfile
from users.models.user_session import UserSession
from users.models.user_status import UserStatus

admin.site.register(User, UserAdmin)
admin.site.register(UserStatus)
admin.site.register(AccountType)
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(LoginHistory)
admin.site.register(UserSession)
