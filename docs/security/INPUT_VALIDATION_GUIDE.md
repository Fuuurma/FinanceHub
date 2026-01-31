# Input Validation Best Practices

**Date:** 2026-01-31
**Author:** Charo (Security Engineer)
**Version:** 1.0

---

## Overview

This document provides input validation patterns and examples for the FinanceHub application. Proper input validation is critical for preventing injection attacks, data corruption, and security vulnerabilities.

---

## Validation Principles

### 1. Validate on Entry

Validate input as soon as it enters your application, not after processing.

```python
# ❌ Bad - Validate after processing
def process_user_input(data):
    parsed = json.loads(data)  # Could fail
    # ... processing ...
    validate_user(parsed)  # Too late

# ✅ Good - Validate first
def process_user_input(data):
    validate_input_schema(data)  # Validate first
    parsed = json.loads(data)  # Now safe to process
    # ... processing ...
```

### 2. Whitelist over Blacklist

Allow only known good patterns, not block known bad patterns.

```python
# ❌ Bad - Blacklist approach
def validate_username(username):
    if any(bad in username for bad in ['admin', 'root', 'system']):
        raise ValidationError("Username not allowed")
    return True

# ✅ Good - Whitelist approach
import re
def validate_username(username):
    pattern = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
    if not pattern.match(username):
        raise ValidationError("Username must be 3-30 alphanumeric characters")
    return True
```

### 3. Defense in Depth

Validate at multiple layers: client, server, database.

```python
# Client-side (UX only, not security)
# JavaScript validation
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

# Server-side (Security critical)
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

def validate_email(email):
    validator = EmailValidator()
    try:
        validator(email)
    except ValidationError:
        raise ValueError("Invalid email address")

# Database level (Last line of defense)
# Use parameterized queries (automatic in Django ORM)
```

---

## Django Validation Patterns

### Model Validation

```python
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    initial_value = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        """Validate model before save"""
        super().clean()
        
        # Validate name
        if not self.name or len(self.name.strip()) < 3:
            raise ValidationError({
                'name': 'Portfolio name must be at least 3 characters'
            })
        
        # Validate initial value
        if self.initial_value < 0:
            raise ValidationError({
                'initial_value': 'Initial value cannot be negative'
            })
        
        # Validate user exists
        if not self.user_id:
            raise ValidationError({
                'user': 'Portfolio must be associated with a user'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

### Form Validation

```python
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class TradeForm(forms.Form):
    symbol = forms.CharField(max_length=10, min_length=1)
    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000000
    )
    price = forms.DecimalField(
        max_digits=15,
        decimal_places=4,
        min_value=0.0001
    )
    order_type = forms.ChoiceField(
        choices=[('market', 'Market'), ('limit', 'Limit')]
    )
    
    def clean_symbol(self):
        symbol = self.cleaned_data['symbol'].upper()
        
        # Validate format
        if not re.match(r'^[A-Z]{1,10}$', symbol):
            raise forms.ValidationError("Invalid symbol format")
        
        # Check against allowed symbols
        allowed_symbols = get_allowed_symbols()
        if symbol not in allowed_symbols:
            raise forms.ValidationError(f"Symbol {symbol} not available for trading")
        
        return symbol
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        
        # Business logic validation
        max_tradable = get_max_tradable_quantity(symbol=self.cleaned_data.get('symbol'))
        if quantity > max_tradable:
            raise forms.ValidationError(
                f"Maximum tradable quantity is {max_tradable}"
            )
        
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Cross-field validation
        order_type = cleaned_data.get('order_type')
        price = cleaned_data.get('price')
        
        if order_type == 'limit' and price <= 0:
            raise forms.ValidationError({
                'price': 'Limit orders require a valid price'
            })
        
        return cleaned_data
```

### Serializer Validation (DRF)

```python
from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'user', 'symbol', 'alert_type', 'condition_value', 'is_active']
    
    def validate_symbol(self, value):
        """Validate symbol format and availability"""
        # Format validation
        if not re.match(r'^[A-Z]{1,10}$', value.upper()):
            raise serializers.ValidationError("Invalid symbol format")
        
        # Check if symbol exists
        if not symbol_exists(value.upper()):
            raise serializers.ValidationError(f"Symbol {value} not found")
        
        return value.upper()
    
    def validate_condition_value(self, value):
        """Validate alert condition value"""
        if value <= 0:
            raise serializers.ValidationError(
                "Alert condition value must be positive"
            )
        
        # Maximum reasonable value for any asset
        if value > 1000000000:
            raise serializers.ValidationError(
                "Alert value exceeds maximum allowed"
            )
        
        return value
    
    def validate_alert_type(self, value):
        """Validate alert type"""
        valid_types = ['above', 'below', 'percent_change']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid alert type. Must be one of: {valid_types}"
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Prevent alerts on inactive symbols
        symbol = data.get('symbol') or getattr(self.instance, 'symbol', None)
        if symbol and not is_symbol_active(symbol):
            raise serializers.ValidationError(
                "Cannot create alert for inactive symbol"
            )
        
        return data
```

---

## String Validation

### Sanitization

```python
import re
import html
from bleach import clean

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # HTML escape (for display)
    text = html.escape(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text

def sanitize_for_html(text: str) -> str:
    """Allow only safe HTML tags"""
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    allowed_attributes = {}
    
    cleaned = clean(text, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-.]', '_', filename)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename
```

### Format Validation

```python
import re
from typing import Optional

class InputValidator:
    """Reusable input validation utilities"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{6,14}$')
    URL_PATTERN = re.compile(r'^https?://[^\s]+$')
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,10}$')
    IPV4_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or len(symbol) > 10:
            return False
        return bool(cls.SYMBOL_PATTERN.match(symbol))
    
    @classmethod
    def validate_amount(cls, amount: float, min_val: float = 0,
                       max_val: float = float('inf')) -> bool:
        """Validate monetary amount"""
        if amount < min_val or amount > max_val:
            return False
        # Check for precision issues (max 8 decimal places)
        if round(amount, 8) != amount:
            return False
        return True
    
    @classmethod
    def validate_percentage(cls, value: float) -> bool:
        """Validate percentage value"""
        return 0 <= value <= 100
    
    @classmethod
    def validate_date_range(cls, start_date, end_date) -> bool:
        """Validate date range"""
        from datetime import datetime
        if start_date >= end_date:
            return False
        if start_date > datetime.now():
            return False
        return True
```

---

## Numeric Validation

```python
from decimal import Decimal, InvalidOperation
from typing import Union

def validate_decimal(value: Union[str, int, float, Decimal],
                    min_value: Decimal = None,
                    max_value: Decimal = None,
                    decimals: int = None) -> Decimal:
    """Validate and convert to Decimal"""
    
    try:
        if isinstance(value, Decimal):
            result = value
        else:
            result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid decimal value: {value}")
    
    if min_value is not None and result < min_value:
        raise ValueError(f"Value must be >= {min_value}")
    
    if max_value is not None and result > max_value:
        raise ValueError(f"Value must be <= {max_value}")
    
    if decimals is not None:
        if abs(result.as_tuple().exponent) > decimals:
            raise ValueError(
                f"Value must have at most {decimals} decimal places"
            )
    
    return result

def validate_positive_decimal(value, max_value=None) -> Decimal:
    """Validate positive decimal value"""
    result = validate_decimal(value, min_value=Decimal('0'))
    if max_value and result > max_value:
        raise ValueError(f"Value must be <= {max_value}")
    return result

# Usage examples
try:
    price = validate_decimal(
        "150.25",
        min_value=Decimal('0.01'),
        max_value=Decimal('1000000'),
        decimals=4
    )
except ValueError as e:
    print(f"Invalid price: {e}")
```

---

## File Upload Validation

```python
import os
import magic
from django.core.files.uploadedfile import UploadedFile

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.json', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    'text/csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/json',
    'application/pdf'
}

def validate_file_upload(uploaded_file: UploadedFile) -> bool:
    """Validate uploaded file"""
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size exceeds maximum allowed ({MAX_FILE_SIZE // 1024 // 1024}MB)"
        )
    
    # Check extension
    _, ext = os.path.splitext(uploaded_file.name)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    file_content = uploaded_file.read(8192)
    uploaded_file.seek(0)  # Reset file position
    
    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"Invalid file type: {mime_type}")
    
    # Scan for malware (if ClamAV available)
    if scan_for_malware(uploaded_file):
        raise ValidationError("File failed security scan")
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename"""
    # Get basename (prevent directory traversal)
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-.]', '_', filename)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename
```

---

## API Request Validation

```python
from django.http import JsonResponse
from functools import wraps
import json
import re

def validate_json_request(required_fields=None):
    """Decorator to validate JSON request body"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check content type
            content_type = request.content_type
            if not content_type or 'application/json' not in content_type:
                return JsonResponse({
                    'error': 'Content-Type must be application/json'
                }, status=400)
            
            # Parse body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON in request body'
                }, status=400)
            
            # Validate required fields
            if required_fields:
                missing = [f for f in required_fields if f not in data]
                if missing:
                    return JsonResponse({
                        'error': f'Missing required fields: {", ".join(missing)}'
                    }, status=400)
            
            # Attach validated data to request
            request.validated_data = data
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@validate_json_request(required_fields=['symbol', 'quantity', 'price'])
def create_order(request):
    data = request.validated_data
    # Now safe to use data
    return JsonResponse({'order_id': create_order_from_data(data)})
```

---

## Validation Testing

```python
import pytest
from django.core.exceptions import ValidationError

class TestInputValidation:
    """Test input validation functions"""
    
    def test_valid_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("user.name+tag@example.co.uk") is True
    
    def test_invalid_email(self):
        assert validate_email("") is False
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
    
    def test_valid_symbol(self):
        assert validate_symbol("AAPL") is True
        assert validate_symbol("BTC") is True
        assert validate_symbol("ETH") is True
    
    def test_invalid_symbol(self):
        assert validate_symbol("") is False
        assert validate_symbol("aapl") is False  # Lowercase
        assert validate_symbol("AAPL123456789") is False  # Too long
        assert validate_symbol("A-PL") is False  # Hyphen
    
    def test_positive_decimal(self):
        assert validate_positive_decimal("100.50") == Decimal("100.50")
        assert validate_positive_decimal(0) == Decimal("0")
    
    def test_negative_decimal_rejected(self):
        with pytest.raises(ValueError):
            validate_positive_decimal("-100")
    
    def test_file_extension_validation(self):
        assert sanitize_filename("data.csv") == "data.csv"
        assert sanitize_filename("../etc/passwd") == "passwd"
        assert sanitize_filename("file with spaces.pdf") == "file_with_spaces.pdf"
```

---

## Quick Reference

| Input Type | Validation Method | Example |
|------------|-------------------|---------|
| Email | Regex pattern | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` |
| Symbol | Uppercase alphanumeric | `^[A-Z]{1,10}$` |
| Amount | Decimal with bounds | `0 < value < 1000000000` |
| Percentage | 0-100 range | `0 <= value <= 100` |
| Filename | Sanitize path chars | Remove `/`, `\`, `..` |
| JSON | Parse + schema check | `json.loads()` + jsonschema |
| HTML | Whitelist tags | `bleach.clean()` |

---

**Document Version:** 1.0
**Last Updated:** 2026-01-31
