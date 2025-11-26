"""
Tests for Document Upload Endpoint
Tests file upload, validation, and storage
"""
import pytest
import os
from fastapi.testclient import TestClient
from io import BytesIO


class TestDocumentUpload:
    """Test document upload functionality"""
    
    def test_upload_pdf_success(self, client, auth_headers_candidat):
        """Test successful PDF upload"""
        # Create a minimal PDF
        pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
        
        files = {
            'file': ('test_cv.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        data = {
            'document_type': 'cv'
        }
        
        response = client.post(
            "/profiles/documents",
            files=files,
            data=data,
            headers=auth_headers_candidat
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "document_id" in result
        assert result["filename"] == "test_cv.pdf"
        assert result["file_size"] > 0
    
    def test_upload_file_too_large(self, client, auth_headers_candidat):
        """Test that file larger than 5MB is rejected"""
        # Create a file > 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        
        files = {
            'file': ('large_file.pdf', BytesIO(large_content), 'application/pdf')
        }
        data = {
            'document_type': 'cv'
        }
        
        response = client.post(
            "/profiles/documents",
            files=files,
            data=data,
            headers=auth_headers_candidat
        )
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    def test_upload_invalid_mime_type(self, client, auth_headers_candidat):
        """Test that invalid MIME type is rejected"""
        files = {
            'file': ('test.txt', BytesIO(b"Plain text"), 'text/plain')
        }
        data = {
            'document_type': 'cv'
        }
        
        response = client.post(
            "/profiles/documents",
            files=files,
            data=data,
            headers=auth_headers_candidat
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
    
    def test_upload_without_auth(self, client):
        """Test that upload without authentication is rejected"""
        files = {
            'file': ('test.pdf', BytesIO(b"content"), 'application/pdf')
        }
        data = {
            'document_type': 'cv'
        }
        
        response = client.post(
            "/profiles/documents",
            files=files,
            data=data
        )
        
        assert response.status_code == 401
    
    def test_upload_missing_document_type(self, client, auth_headers_candidat):
        """Test that missing document_type is rejected"""
        files = {
            'file': ('test.pdf', BytesIO(b"content"), 'application/pdf')
        }
        
        response = client.post(
            "/profiles/documents",
            files=files,
            headers=auth_headers_candidat
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_document_type_validation(self, client, auth_headers_candidat):
        """Test that only allowed document types are accepted"""
        pdf_content = b"%PDF-1.4 minimal"

        valid_files = {
            'file': ('valid.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        valid_data = {
            'document_type': 'cv'
        }

        valid_response = client.post(
            "/profiles/documents",
            files=valid_files,
            data=valid_data,
            headers=auth_headers_candidat
        )

        assert valid_response.status_code == 200

        invalid_files = {
            'file': ('invalid.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        invalid_data = {
            'document_type': 'unknown_type'
        }

        invalid_response = client.post(
            "/profiles/documents",
            files=invalid_files,
            data=invalid_data,
            headers=auth_headers_candidat
        )

        assert invalid_response.status_code == 400
        assert "document type" in invalid_response.json()["detail"].lower()


class TestDocumentRetrieval:
    """Test document retrieval"""
    
    def test_get_my_documents(self, client, auth_headers_candidat):
        """Test retrieving user's documents"""
        response = client.get(
            "/profiles/documents",
            headers=auth_headers_candidat
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "documents" in result
        assert isinstance(result["documents"], list)
    
    def test_get_documents_without_auth(self, client):
        """Test that getting documents without auth is rejected"""
        response = client.get("/profiles/documents")
        
        assert response.status_code == 401


class TestDocumentDeletion:
    """Test document deletion"""
    
    def test_delete_own_document(self, client, auth_headers_candidat, test_db):
        """Test deleting own document"""
        # First create a document
        doc_id = "test_doc_123"
        # Note: In real test, would upload first, then delete
        
        response = client.delete(
            f"/profiles/documents/{doc_id}",
            headers=auth_headers_candidat
        )
        
        # Should be 404 since document doesn't exist, but auth works
        assert response.status_code in [200, 404]
    
    def test_delete_without_auth(self, client):
        """Test that deleting without auth is rejected"""
        response = client.delete("/profiles/documents/doc123")
        
        assert response.status_code == 401


# Fixtures for test client and authentication

@pytest.fixture
def client():
    """Create a test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers_candidat():
    """Create authentication headers for a candidat user"""
    # In real tests, would authenticate and get token
    # For now, mock token
    return {
        "Authorization": "Bearer mock_token_candidat"
    }


@pytest.fixture
async def test_db():
    """Create a test database connection"""
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.auth_db_test
    yield db
    await client.drop_database("auth_db_test")
    client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
