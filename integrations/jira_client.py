import uuid

class JiraClient:
    """Mock Jira Client for creating and updating case tickets."""
    
    @staticmethod
    def create_ticket(summary: str, description: str, issue_type: str = "Investigation") -> str:
        """Simulate creating a Jira ticket."""
        ticket_id = f"AML-{uuid.uuid4().hex[:6].upper()}"
        print(f"[JIRA MOCK] Created Ticket: {ticket_id} | Summary: {summary}")
        return ticket_id
        
    @staticmethod
    def update_ticket(ticket_id: str, status: str, comment: str = None) -> bool:
        """Simulate updating a Jira ticket."""
        print(f"[JIRA MOCK] Updated Ticket: {ticket_id} | Status: {status} | Comment: {comment}")
        return True
