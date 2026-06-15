from locust import HttpUser, task, between
import random

class InvoiceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Register/login to get token
        pass
        
    @task(3)
    def list_documents(self):
        self.client.get("/api/v1/documents/")
        
    @task(1)
    def view_reports(self):
        self.client.get("/api/v1/reports/spend-summary")
