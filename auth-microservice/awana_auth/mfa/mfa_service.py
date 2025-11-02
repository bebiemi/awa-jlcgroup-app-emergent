"""
MFA Service - TOTP, Email OTP, SMS OTP, Backup Codes
"""
import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.models import MFASecret, MFASession, MFAMethod


class MFAService:
    """Service for managing Multi-Factor Authentication"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.mfa_secrets_collection = db['mfa_secrets']
        self.mfa_sessions_collection = db['mfa_sessions']
        self.users_collection = db['users']
    
    # ===== TOTP Methods =====
    
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def generate_totp_qr_code(self, secret: str, user_email: str, issuer: str = "JLC Group") -> str:
        """
        Generate QR code for TOTP setup
        Returns base64 encoded PNG image
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 30s window
    
    # ===== Backup Codes Methods =====
    
    def generate_backup_codes(self, count: int = 10) -> Tuple[List[str], List[str]]:
        """
        Generate backup codes
        Returns (plain_codes, hashed_codes)
        """
        plain_codes = []
        hashed_codes = []
        
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            plain_codes.append(code)
            
            # Hash the code
            hashed = hashlib.sha256(code.encode()).hexdigest()
            hashed_codes.append(hashed)
        
        return plain_codes, hashed_codes
    
    def verify_backup_code(self, hashed_codes: List[str], code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify backup code and return the hashed code to remove
        Returns (is_valid, hashed_code_to_remove)
        """
        code_hash = hashlib.sha256(code.upper().encode()).hexdigest()
        
        if code_hash in hashed_codes:
            return True, code_hash
        return False, None
    
    # ===== Email OTP Methods =====
    
    def generate_email_otp(self) -> str:
        """Generate 6-digit OTP for email"""
        return ''.join(str(secrets.randbelow(10)) for _ in range(6))
    
    async def store_email_otp(self, user_id: str, otp: str):
        """Store email OTP with 10-minute expiration"""
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        await self.db['email_otps'].update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'otp_hash': otp_hash,
                    'created_at': datetime.now(timezone.utc),
                    'expires_at': datetime.now(timezone.utc).timestamp() + 600  # 10 minutes
                }
            },
            upsert=True
        )
    
    async def verify_email_otp(self, user_id: str, otp: str) -> bool:
        """Verify email OTP"""
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        stored_otp = await self.db['email_otps'].find_one({'user_id': user_id})
        
        if not stored_otp:
            return False
        
        # Check expiration
        if stored_otp['expires_at'] < datetime.now(timezone.utc).timestamp():
            # Delete expired OTP
            await self.db['email_otps'].delete_one({'user_id': user_id})
            return False
        
        # Verify OTP
        is_valid = stored_otp['otp_hash'] == otp_hash
        
        # Delete OTP after verification (one-time use)
        if is_valid:
            await self.db['email_otps'].delete_one({'user_id': user_id})
        
        return is_valid
    
    # ===== SMS OTP Methods (Placeholder for future integration) =====
    
    def generate_sms_otp(self) -> str:
        """Generate 6-digit OTP for SMS"""
        return ''.join(str(secrets.randbelow(10)) for _ in range(6))
    
    async def send_sms_otp(self, phone_number: str, otp: str) -> bool:
        """
        Send SMS OTP (placeholder for future integration)
        TODO: Integrate with Africa's Talking, Termii, or Mnotify
        """
        # For now, just store it like email OTP
        # In production, this would call SMS provider API
        print(f"[MFA] SMS OTP for {phone_number}: {otp}")
        return True
    
    async def store_sms_otp(self, user_id: str, otp: str):
        """Store SMS OTP with 10-minute expiration"""
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        await self.db['sms_otps'].update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'otp_hash': otp_hash,
                    'created_at': datetime.now(timezone.utc),
                    'expires_at': datetime.now(timezone.utc).timestamp() + 600
                }
            },
            upsert=True
        )
    
    async def verify_sms_otp(self, user_id: str, otp: str) -> bool:
        """Verify SMS OTP"""
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        stored_otp = await self.db['sms_otps'].find_one({'user_id': user_id})
        
        if not stored_otp:
            return False
        
        if stored_otp['expires_at'] < datetime.now(timezone.utc).timestamp():
            await self.db['sms_otps'].delete_one({'user_id': user_id})
            return False
        
        is_valid = stored_otp['otp_hash'] == otp_hash
        
        if is_valid:
            await self.db['sms_otps'].delete_one({'user_id': user_id})
        
        return is_valid
    
    # ===== MFA Session Management =====
    
    async def create_mfa_session(self, user_id: str, available_methods: List[str]) -> MFASession:
        """Create temporary MFA session after first factor"""
        session_token = secrets.token_urlsafe(32)
        
        mfa_session = MFASession(
            user_id=user_id,
            session_token=session_token,
            available_methods=available_methods
        )
        
        await self.mfa_sessions_collection.insert_one(mfa_session.model_dump())
        
        return mfa_session
    
    async def get_mfa_session(self, session_token: str) -> Optional[MFASession]:
        """Get MFA session by token"""
        session_data = await self.mfa_sessions_collection.find_one({'session_token': session_token})
        
        if not session_data:
            return None
        
        session = MFASession(**session_data)
        
        # Check expiration
        if session.expires_at < datetime.now(timezone.utc):
            await self.mfa_sessions_collection.delete_one({'session_token': session_token})
            return None
        
        return session
    
    async def verify_mfa_session(self, session_token: str) -> bool:
        """Mark MFA session as verified"""
        result = await self.mfa_sessions_collection.update_one(
            {'session_token': session_token},
            {'$set': {'verified': True}}
        )
        return result.modified_count > 0
    
    async def delete_mfa_session(self, session_token: str):
        """Delete MFA session"""
        await self.mfa_sessions_collection.delete_one({'session_token': session_token})
    
    # ===== User MFA Settings =====
    
    async def get_user_mfa_secret(self, user_id: str) -> Optional[MFASecret]:
        """Get user's MFA secrets"""
        secret_data = await self.mfa_secrets_collection.find_one({'user_id': user_id})
        
        if not secret_data:
            return None
        
        return MFASecret(**secret_data)
    
    async def save_user_mfa_secret(self, mfa_secret: MFASecret):
        """Save or update user's MFA secrets"""
        await self.mfa_secrets_collection.update_one(
            {'user_id': mfa_secret.user_id},
            {'$set': mfa_secret.model_dump()},
            upsert=True
        )
    
    async def enable_mfa_method(self, user_id: str, method: str):
        """Enable MFA method for user"""
        await self.users_collection.update_one(
            {'id': user_id},
            {
                '$set': {'mfa_enabled': True},
                '$addToSet': {'mfa_methods': method}
            }
        )
    
    async def disable_mfa_method(self, user_id: str, method: str):
        """Disable MFA method for user"""
        await self.users_collection.update_one(
            {'id': user_id},
            {'$pull': {'mfa_methods': method}}
        )
        
        # Check if any methods left
        user = await self.users_collection.find_one({'id': user_id})
        if not user.get('mfa_methods'):
            await self.users_collection.update_one(
                {'id': user_id},
                {'$set': {'mfa_enabled': False}}
            )
