from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.document import Document, DocumentStatusEnum
from typing import Optional
from datetime import datetime

class ReportingAgent:
    
    @staticmethod
    def _apply_filters(query, start_date: Optional[str], end_date: Optional[str], vendor_name: Optional[str], status: Optional[str], default_status: Optional[str] = None):
        if start_date:
            try:
                dt = datetime.strptime(start_date[:10], "%Y-%m-%d")
                query = query.where(Document.created_at >= dt)
            except ValueError:
                pass
        if end_date:
            try:
                dt = datetime.strptime(end_date[:10], "%Y-%m-%d")
                query = query.where(Document.created_at <= dt)
            except ValueError:
                pass
        if vendor_name:
            query = query.where(Document.vendor_name.ilike(f"%{vendor_name}%"))
        if status:
            try:
                query = query.where(Document.status == DocumentStatusEnum(status))
            except ValueError:
                pass
        elif default_status:
            try:
                query = query.where(Document.status == DocumentStatusEnum(default_status))
            except ValueError:
                pass
        return query

    @staticmethod
    async def get_spend_summary(db: AsyncSession, start_date=None, end_date=None, vendor_name=None, status=None):
        query = select(
            Document.vendor_name,
            func.sum(Document.total_amount).label('total_spend')
        ).where(Document.total_amount != None)
        
        query = ReportingAgent._apply_filters(query, start_date, end_date, vendor_name, status, default_status="approved")
        query = query.group_by(Document.vendor_name)
        
        result = await db.execute(query)
        data = [{"vendor": row[0], "total_spend": float(row[1] or 0)} for row in result.all()]
        
        total_query = select(func.sum(Document.total_amount)).where(Document.total_amount != None)
        total_query = ReportingAgent._apply_filters(total_query, start_date, end_date, vendor_name, status, default_status="approved")
        total_result = await db.execute(total_query)
        total = float(total_result.scalar() or 0)
        
        return {
            "total_spend": total,
            "spend_by_vendor": data
        }

    @staticmethod
    async def get_vendor_analysis(db: AsyncSession, start_date=None, end_date=None, vendor_name=None, status=None):
        query = select(
            Document.vendor_name,
            func.sum(Document.total_amount).label('total_spend'),
            func.count(Document.id).label('document_count'),
            func.avg(Document.total_amount).label('average_invoice_value')
        ).where(Document.vendor_name != None)
        
        query = ReportingAgent._apply_filters(query, start_date, end_date, vendor_name, status, default_status="approved")
        query = query.group_by(Document.vendor_name)
        
        result = await db.execute(query)
        data = [{
            "vendor_name": row[0], 
            "total_spend": float(row[1] or 0),
            "document_count": int(row[2] or 0),
            "average_invoice_value": float(row[3] or 0)
        } for row in result.all()]
        
        return {"vendor_analysis": data}

    @staticmethod
    async def get_approval_status(db: AsyncSession, start_date=None, end_date=None, vendor_name=None, status=None):
        query = select(
            Document.status,
            func.count(Document.id).label('count')
        )
        
        query = ReportingAgent._apply_filters(query, start_date, end_date, vendor_name, status)
        query = query.group_by(Document.status)
        
        result = await db.execute(query)
        data = [{"status": row[0].value if hasattr(row[0], 'value') else row[0], "count": int(row[1] or 0)} for row in result.all()]
        
        return {"approval_status": data}

    @staticmethod
    async def get_tax_report(db: AsyncSession, start_date=None, end_date=None, vendor_name=None, status=None):
        query = select(
            Document.vendor_name,
            func.sum(Document.vat_amount).label('total_vat')
        ).where(Document.vat_amount != None)
        
        query = ReportingAgent._apply_filters(query, start_date, end_date, vendor_name, status, default_status="approved")
        query = query.group_by(Document.vendor_name)
        
        result = await db.execute(query)
        data = [{"vendor_name": row[0], "total_vat": float(row[1] or 0)} for row in result.all()]
        
        total_query = select(func.sum(Document.vat_amount)).where(Document.vat_amount != None)
        total_query = ReportingAgent._apply_filters(total_query, start_date, end_date, vendor_name, status, default_status="approved")
        total_result = await db.execute(total_query)
        total_vat = float(total_result.scalar() or 0)
        
        return {
            "total_vat": total_vat,
            "vat_by_vendor": data
        }
