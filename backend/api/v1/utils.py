def check_field(self, obj):
    user = self.context.get('request').user
    return user.is_authenticated and obj.filter(user=user).exists()
