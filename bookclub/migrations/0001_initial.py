# Generated by Django 3.2.5 on 2022-02-13 16:52

import bookclub.custom_managers
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('public_bio', models.CharField(blank=True, max_length=512)),
                ('favourite_genre', models.CharField(blank=True, max_length=30)),
                ('location', models.CharField(max_length=96)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', bookclub.custom_managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(max_length=12, unique=True)),
                ('title', models.CharField(max_length=512)),
                ('author', models.CharField(max_length=512)),
                ('pub_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2022)])),
                ('publisher', models.CharField(max_length=512)),
                ('small_url', models.URLField(max_length=512)),
                ('medium_url', models.URLField(max_length=512)),
                ('large_url', models.URLField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=48, unique=True)),
                ('description', models.CharField(blank=True, max_length=512)),
                ('location', models.CharField(max_length=96)),
                ('members', models.ManyToManyField(related_name='member_of', to=settings.AUTH_USER_MODEL)),
                ('organisers', models.ManyToManyField(related_name='organiser_of', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_of', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclub.club')),
            ],
        ),
    ]
