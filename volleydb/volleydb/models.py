from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'surname']

class DatabaseManager(User):
    
    class Meta:
        verbose_name = 'Database Manager'
        verbose_name_plural = 'Database Managers'

    def save(self, *args, **kwargs):
        self.is_staff = True  
        self.is_superuser = True  
        super().save(*args, **kwargs)


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    weight = models.FloatField()
    height = models.FloatField()

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nationality = models.CharField(max_length=20)

class Jury(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nationality = models.CharField(max_length=20)


class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    position_name = models.CharField(max_length=20)

class PlayerPositios(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('player', 'position')

class Channel(models.Model):
    channel_id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=20, unique=True)

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=20)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    contract_start = models.DateField()
    contract_end = models.DateField()

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.contract_start > self.contract_end:
            raise ValidationError("Start of contract must be before end of contract.")

class PlayerTeams(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('team', 'player')

class Stadium(models.Model):
    stadium_id = models.AutoField(primary_key=True)
    stadium_name = models.CharField(max_length=20)
    stadium_country = models.CharField(max_length=20)
    class Meta:
        unique_together = ('stadium_country', 'stadium_id')

class MatchSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    time_slot = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    date = models.DateField()
    assigned_jury = models.ForeignKey(Jury, on_delete=models.CASCADE)
    rating = models.FloatField()

    class Meta:
        unique_together = ('stadium', 'time_slot')

class SessionSquads(models.Model):
    session = models.ForeignKey(MatchSession, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('session', 'player')

class Agreement(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
