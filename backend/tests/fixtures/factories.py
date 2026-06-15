"""
Factory Boy factories for generating test data.

Usage in tests:
    from tests.fixtures.factories import UserFactory, DocumentFactory
    user = UserFactory.build()  # in-memory only
"""
import uuid
import factory
from app.models.user import User, RoleEnum
from app.models.document import Document, DocumentStatusEnum
from app.models.audit_log import AuditLog
from app.models.duplicate_check import DuplicateCheck
from app.core.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    password_hash = factory.LazyFunction(lambda: get_password_hash("password123"))
    full_name = factory.Faker("name")
    role = RoleEnum.viewer
    is_active = True


class DocumentFactory(factory.Factory):
    class Meta:
        model = Document

    id = factory.LazyFunction(uuid.uuid4)
    file_name = factory.Sequence(lambda n: f"invoice_{n}.pdf")
    file_url = factory.LazyAttribute(lambda o: f"https://storage.example.com/{o.file_name}")
    file_hash = factory.LazyFunction(lambda: uuid.uuid4().hex)
    document_type = "invoice"
    vendor_name = factory.Faker("company")
    invoice_number = factory.Sequence(lambda n: f"INV-{n:05d}")
    total_amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    vat_amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    subtotal_amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    currency = "USD"
    status = DocumentStatusEnum.pending_review
    uploaded_by = factory.LazyFunction(uuid.uuid4)


class AuditLogFactory(factory.Factory):
    class Meta:
        model = AuditLog

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    action = "upload"
    entity_type = "Document"
    entity_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    old_value = None
    new_value = None


class DuplicateCheckFactory(factory.Factory):
    class Meta:
        model = DuplicateCheck

    id = factory.LazyFunction(uuid.uuid4)
    document_id = factory.LazyFunction(uuid.uuid4)
    duplicate_type = "exact_hash"
    confidence_score = 1.0
    matched_document_id = factory.LazyFunction(uuid.uuid4)
    risk_level = "high"
