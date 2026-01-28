from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceSheet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('asset_id', models.UUIDField(db_index=True)),
                ('symbol', models.CharField(db_index=True, max_length=20)),
                ('report_date', models.DateField(db_index=True)),
                ('fiscal_year', models.IntegerField(db_index=True)),
                ('fiscal_quarter', models.IntegerField()),
                ('fiscal_period', models.CharField(max_length=20)),
                ('source', models.CharField(default='manual', max_length=100)),
                ('confidence_score', models.DecimalField(decimal_places=2, default=models.DecimalField(default=1.0), max_digits=3)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('total_assets', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('total_liabilities', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('total_equity', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('cash_and_equivalents', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('short_term_investments', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('accounts_receivable', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('inventory', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('total_current_assets', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('ppe', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('goodwill', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('intangibles', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('accounts_payable', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('short_term_debt', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('total_current_liabilities', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('long_term_debt', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
                ('deferred_revenue', models.DecimalField(decimal_places=2, max_digits=30, null=True)),
            ],
            options={
                'db_table': 'fundamentals_balance_sheet',
                'ordering': ['-report_date'],
            },
        ),
    ]
