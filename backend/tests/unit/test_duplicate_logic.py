import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tasks.duplicate import check_duplicates_async
from app.models.document import DocumentStatusEnum, Document
from app.models.duplicate_check import DuplicateCheck
from tests.fixtures.factories import DocumentFactory

@pytest.mark.asyncio
async def test_exact_hash_match_flags_duplicate(db_session: AsyncSession):
    hash_val = uuid.uuid4().hex
    doc1 = DocumentFactory.build(file_hash=hash_val, status=DocumentStatusEnum.approved)
    doc2 = DocumentFactory.build(file_hash=hash_val, status=DocumentStatusEnum.pending_review)
    db_session.add_all([doc1, doc2])
    await db_session.commit()
    await db_session.refresh(doc1)
    await db_session.refresh(doc2)

    await check_duplicates_async(str(doc2.id))

    await db_session.refresh(doc2)
    assert doc2.status == DocumentStatusEnum.duplicate_flagged

    dup = (await db_session.execute(select(DuplicateCheck).where(DuplicateCheck.document_id == doc2.id))).scalar_one()
    assert dup.duplicate_type == "exact_hash"
    assert dup.matched_document_id == doc1.id
    assert float(dup.confidence_score) == 1.0

@pytest.mark.asyncio
async def test_invoice_number_vendor_match(db_session: AsyncSession):
    doc1 = DocumentFactory.build(file_hash="h1", vendor_name="Acme", invoice_number="123")
    doc2 = DocumentFactory.build(file_hash="h2", vendor_name="Acme", invoice_number="123")
    db_session.add_all([doc1, doc2])
    await db_session.commit()
    await db_session.refresh(doc1)
    await db_session.refresh(doc2)

    await check_duplicates_async(str(doc2.id))

    await db_session.refresh(doc2)
    assert doc2.status == DocumentStatusEnum.duplicate_flagged

    dup = (await db_session.execute(select(DuplicateCheck).where(DuplicateCheck.document_id == doc2.id))).scalar_one()
    assert dup.duplicate_type == "invoice_match"
    assert dup.matched_document_id == doc1.id
    assert float(dup.confidence_score) == 0.9

@pytest.mark.asyncio
async def test_no_duplicate_found(db_session: AsyncSession):
    doc1 = DocumentFactory.build()
    db_session.add(doc1)
    await db_session.commit()
    await db_session.refresh(doc1)

    await check_duplicates_async(str(doc1.id))

    await db_session.refresh(doc1)
    assert doc1.status == DocumentStatusEnum.pending_review

@pytest.mark.asyncio
async def test_missing_invoice_number_skips_invoice_check(db_session: AsyncSession):
    doc1 = DocumentFactory.build(invoice_number=None, vendor_name="Acme")
    doc2 = DocumentFactory.build(invoice_number=None, vendor_name="Acme")
    db_session.add_all([doc1, doc2])
    await db_session.commit()
    await db_session.refresh(doc1)
    await db_session.refresh(doc2)

    await check_duplicates_async(str(doc2.id))

    await db_session.refresh(doc2)
    assert doc2.status == DocumentStatusEnum.pending_review
