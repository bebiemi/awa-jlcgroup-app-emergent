"""
MFA Routes - Multi-Factor Authentication API
Security-first implementation with rate limiting, audit logging, and brute-force protection
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime, timezone
import secrets

from awana_auth.core.models import (
    User, SetupTOTPRequest, VerifyTOTPSetupRequest, SetupEmailOTPRequest,
    SetupSMSOTPRequest, VerifySMSSetupRequest, VerifyMFARequest,
    MFASetupResponse, MFAStatusResponse, MFASecret, MFAMethod
)
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.mfa.mfa_service import MFAService

mfa_router = APIRouter(prefix="/auth/mfa", tags=["mfa"])


# ===== Security: Rate Limiting Helper =====

async def check_mfa_rate_limit(db: AsyncIOMotorDatabase, user_id: str, action: str) -> bool:
    """
    Check if user has exceeded rate limit for MFA actions
    Prevents brute force attacks
    """
    rate_limit_key = f"{user_id}_{action}"
    now = datetime.now(timezone.utc)
    
    # Get recent attempts in last 15 minutes
    attempts = await db['mfa_rate_limits'].find_one({'key': rate_limit_key})
    
    if not attempts:
        # First attempt
        await db['mfa_rate_limits'].insert_one({
            'key': rate_limit_key,
            'count': 1,
            'first_attempt': now,
            'last_attempt': now
        })
        return True
    
    # Calculate time window (15 minutes)
    time_diff = (now - attempts['first_attempt']).total_seconds()
    
    if time_diff > 900:  # 15 minutes passed, reset
        await db['mfa_rate_limits'].update_one(
            {'key': rate_limit_key},
            {'$set': {'count': 1, 'first_attempt': now, 'last_attempt': now}}
        )
        return True
    
    # Check limit: Max 5 attempts in 15 minutes
    if attempts['count'] >= 5:
        return False
    
    # Increment counter
    await db['mfa_rate_limits'].update_one(
        {'key': rate_limit_key},
        {'$inc': {'count': 1}, '$set': {'last_attempt': now}}
    )
    
    return True


async def log_mfa_event(db: AsyncIOMotorDatabase, user_id: str, event_type: str, 
                       success: bool, method: str = None, ip_address: str = None):
    """
    Audit logging for all MFA events
    Critical for security monitoring and compliance
    """
    await db['mfa_audit_logs'].insert_one({
        'user_id': user_id,
        'event_type': event_type,  # setup_totp, verify_mfa, disable_mfa, etc.
        'method': method,
        'success': success,
        'ip_address': ip_address,
        'timestamp': datetime.now(timezone.utc)
    })


# ===== Get MFA Status =====

@mfa_router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's MFA status"""
    user_data = await db.users.find_one({'id': current_user.id})
    
    return MFAStatusResponse(
        enabled=user_data.get('mfa_enabled', False),
        required=user_data.get('mfa_required', False),
        methods=user_data.get('mfa_methods', []),
        phone_number=user_data.get('phone_number')
    )


# ===== Setup TOTP =====

@mfa_router.post("/setup/totp", response_model=MFASetupResponse)
async def setup_totp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Setup TOTP (Time-based One-Time Password)
    Returns QR code for scanning with authenticator app
    """
    mfa_service = MFAService(db)
    
    # Security: Rate limiting
    if not await check_mfa_rate_limit(db, current_user.id, "setup_totp"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
        )
    
    # Generate TOTP secret
    totp_secret = mfa_service.generate_totp_secret()
    
    # Generate QR code
    qr_code = mfa_service.generate_totp_qr_code(totp_secret, current_user.email)
    
    # Store secret temporarily (will be confirmed after verification)
    await db['mfa_pending_setups'].update_one(
        {'user_id': current_user.id},
        {
            '$set': {
                'totp_secret': totp_secret,
                'created_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc).timestamp() + 600  # 10 minutes
            }
        },
        upsert=True
    )
    
    # Audit log
    await log_mfa_event(
        db, current_user.id, "setup_totp_initiated", True, "totp",
        request.client.host if request.client else None
    )
    
    return MFASetupResponse(
        success=True,
        method="totp",
        qr_code=qr_code,
        secret=totp_secret,  # For manual entry
        message="Scannez le QR code avec votre application d'authentification"
    )


@mfa_router.post("/setup/totp/verify", response_model=MFASetupResponse)
async def verify_totp_setup(
    data: VerifyTOTPSetupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Verify TOTP setup with a code from authenticator app
    Generates backup codes upon successful verification
    """
    mfa_service = MFAService(db)
    
    # Security: Rate limiting
    if not await check_mfa_rate_limit(db, current_user.id, "verify_totp_setup"):
        await log_mfa_event(db, current_user.id, "verify_totp_setup", False, "totp", 
                          request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
        )
    
    # Get pending setup
    pending = await db['mfa_pending_setups'].find_one({'user_id': current_user.id})
    
    if not pending or not pending.get('totp_secret'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune configuration TOTP en attente"
        )
    
    # Check expiration
    if pending['expires_at'] < datetime.now(timezone.utc).timestamp():
        await db['mfa_pending_setups'].delete_one({'user_id': current_user.id})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration expirée. Veuillez recommencer."
        )
    
    # Verify code
    totp_secret = pending['totp_secret']
    if not mfa_service.verify_totp_code(totp_secret, data.code):
        await log_mfa_event(db, current_user.id, "verify_totp_setup", False, "totp",
                          request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code invalide"
        )
    
    # Generate backup codes
    plain_codes, hashed_codes = mfa_service.generate_backup_codes(10)
    
    # Save MFA secret
    mfa_secret = await mfa_service.get_user_mfa_secret(current_user.id)
    if not mfa_secret:
        mfa_secret = MFASecret(
            user_id=current_user.id,
            totp_secret=totp_secret,
            backup_codes=hashed_codes
        )
    else:
        mfa_secret.totp_secret = totp_secret
        mfa_secret.backup_codes = hashed_codes
        mfa_secret.updated_at = datetime.now(timezone.utc)
    
    await mfa_service.save_user_mfa_secret(mfa_secret)
    
    # Enable TOTP method
    await mfa_service.enable_mfa_method(current_user.id, MFAMethod.TOTP.value)
    
    # Clean up pending setup
    await db['mfa_pending_setups'].delete_one({'user_id': current_user.id})
    
    # Audit log
    await log_mfa_event(db, current_user.id, "totp_enabled", True, "totp",
                       request.client.host if request.client else None)
    
    return MFASetupResponse(
        success=True,
        method="totp",
        backup_codes=plain_codes,
        message="TOTP activé avec succès. Conservez vos codes de secours en lieu sûr."
    )


# ===== Setup Email OTP =====

@mfa_router.post("/setup/email", response_model=MFASetupResponse)
async def setup_email_otp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Setup Email OTP
    Sends verification email to user's registered email
    """
    mfa_service = MFAService(db)
    
    # Security: Rate limiting
    if not await check_mfa_rate_limit(db, current_user.id, "setup_email"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
        )
    
    # Generate OTP
    otp = mfa_service.generate_email_otp()
    
    # Store OTP
    await mfa_service.store_email_otp(current_user.id, otp)
    
    # TODO: Send email with OTP
    # For now, log it (in production, use proper email service)
    print(f"[MFA] Email OTP for {current_user.email}: {otp}")
    
    # Enable Email OTP method
    await mfa_service.enable_mfa_method(current_user.id, MFAMethod.EMAIL.value)
    
    # Audit log
    await log_mfa_event(db, current_user.id, "email_otp_enabled", True, "email",
                       request.client.host if request.client else None)
    
    return MFASetupResponse(
        success=True,
        method="email",
        message=f"Email OTP activé. Un code a été envoyé à {current_user.email}"
    )


# ===== Setup SMS OTP =====

@mfa_router.post("/setup/sms", response_model=MFASetupResponse)
async def setup_sms_otp(
    data: SetupSMSOTPRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Setup SMS OTP
    Sends verification SMS to provided phone number
    """
    mfa_service = MFAService(db)
    
    # Security: Rate limiting
    if not await check_mfa_rate_limit(db, current_user.id, "setup_sms"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
        )
    
    # Generate OTP
    otp = mfa_service.generate_sms_otp()
    
    # Store OTP
    await mfa_service.store_sms_otp(current_user.id, otp)
    
    # Send SMS (placeholder for now)
    await mfa_service.send_sms_otp(data.phone_number, otp)
    
    # Store phone number temporarily (will be confirmed after verification)
    await db['mfa_pending_setups'].update_one(
        {'user_id': current_user.id},
        {
            '$set': {
                'phone_number': data.phone_number,
                'created_at': datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    # Audit log
    await log_mfa_event(db, current_user.id, "sms_otp_setup_initiated", True, "sms",
                       request.client.host if request.client else None)
    
    return MFASetupResponse(
        success=True,
        method="sms",
        message=f"Un code de vérification a été envoyé au {data.phone_number}"
    )


@mfa_router.post("/setup/sms/verify", response_model=MFASetupResponse)
async def verify_sms_setup(
    data: VerifySMSSetupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Verify SMS setup with code"""
    mfa_service = MFAService(db)
    
    # Security: Rate limiting
    if not await check_mfa_rate_limit(db, current_user.id, "verify_sms_setup"):
        await log_mfa_event(db, current_user.id, "verify_sms_setup", False, "sms",
                          request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
        )
    
    # Verify OTP
    if not await mfa_service.verify_sms_otp(current_user.id, data.code):
        await log_mfa_event(db, current_user.id, "verify_sms_setup", False, "sms",
                          request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code invalide ou expiré"
        )
    
    # Get pending phone number
    pending = await db['mfa_pending_setups'].find_one({'user_id': current_user.id})
    phone_number = pending.get('phone_number') if pending else None
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numéro de téléphone non trouvé"
        )
    
    # Update user phone number
    await db.users.update_one(
        {'id': current_user.id},
        {'$set': {'phone_number': phone_number}}
    )
    
    # Enable SMS method
    await mfa_service.enable_mfa_method(current_user.id, MFAMethod.SMS.value)
    
    # Audit log
    await log_mfa_event(db, current_user.id, "sms_otp_enabled", True, "sms",
                       request.client.host if request.client else None)
    
    return MFASetupResponse(
        success=True,
        method="sms",
        message="SMS OTP activé avec succès"
    )


# ===== Generate New Backup Codes =====

@mfa_router.post("/backup-codes/regenerate", response_model=MFASetupResponse)
async def regenerate_backup_codes(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Regenerate backup codes
    WARNING: This invalidates all previous backup codes
    """
    mfa_service = MFAService(db)
    
    # Security: Check if MFA is enabled
    user_data = await db.users.find_one({'id': current_user.id})
    if not user_data.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA n'est pas activé"
        )
    
    # Generate new backup codes
    plain_codes, hashed_codes = mfa_service.generate_backup_codes(10)
    
    # Update MFA secret
    mfa_secret = await mfa_service.get_user_mfa_secret(current_user.id)
    if mfa_secret:
        mfa_secret.backup_codes = hashed_codes
        mfa_secret.updated_at = datetime.now(timezone.utc)
        await mfa_service.save_user_mfa_secret(mfa_secret)
    
    # Audit log
    await log_mfa_event(db, current_user.id, "backup_codes_regenerated", True, "backup",
                       request.client.host if request.client else None)
    
    return MFASetupResponse(
        success=True,
        method="backup",
        backup_codes=plain_codes,
        message="Nouveaux codes de secours générés. Les anciens codes sont maintenant invalides."
    )


# ===== Disable MFA Method =====

@mfa_router.delete("/method/{method}")
async def disable_mfa_method(
    method: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Disable a specific MFA method"""
    mfa_service = MFAService(db)
    
    # Validate method
    valid_methods = [m.value for m in MFAMethod]
    if method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Méthode invalide"
        )
    
    # Disable method
    await mfa_service.disable_mfa_method(current_user.id, method)
    
    # Audit log
    await log_mfa_event(db, current_user.id, f"{method}_disabled", True, method,
                       request.client.host if request.client else None)
    
    return {"message": f"Méthode {method} désactivée"}


# ===== Verify MFA During Login =====

@mfa_router.post("/verify")
async def verify_mfa(
    data: VerifyMFARequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Verify MFA code during login
    This is called after successful password authentication
    """
    mfa_service = MFAService(db)
    
    # Get MFA session
    mfa_session = await mfa_service.get_mfa_session(data.mfa_session_token)
    
    if not mfa_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session MFA invalide ou expirée"
        )
    
    # Security: Rate limiting per user
    if not await check_mfa_rate_limit(db, mfa_session.user_id, "verify_mfa"):
        await log_mfa_event(db, mfa_session.user_id, "verify_mfa_failed_rate_limit", 
                          False, data.method.value, request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Compte temporairement verrouillé."
        )
    
    # Verify based on method
    verified = False
    
    if data.method == MFAMethod.TOTP:
        mfa_secret = await mfa_service.get_user_mfa_secret(mfa_session.user_id)
        if mfa_secret and mfa_secret.totp_secret:
            verified = mfa_service.verify_totp_code(mfa_secret.totp_secret, data.code)
    
    elif data.method == MFAMethod.EMAIL:
        verified = await mfa_service.verify_email_otp(mfa_session.user_id, data.code)
    
    elif data.method == MFAMethod.SMS:
        verified = await mfa_service.verify_sms_otp(mfa_session.user_id, data.code)
    
    elif data.method == MFAMethod.BACKUP:
        mfa_secret = await mfa_service.get_user_mfa_secret(mfa_session.user_id)
        if mfa_secret and mfa_secret.backup_codes:
            is_valid, code_to_remove = mfa_service.verify_backup_code(
                mfa_secret.backup_codes, data.code
            )
            if is_valid and code_to_remove:
                # Remove used backup code
                mfa_secret.backup_codes.remove(code_to_remove)
                await mfa_service.save_user_mfa_secret(mfa_secret)
                verified = True
    
    # Audit log
    await log_mfa_event(db, mfa_session.user_id, "verify_mfa", verified, data.method.value,
                       request.client.host if request.client else None)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code invalide"
        )
    
    # Mark session as verified
    await mfa_service.verify_mfa_session(data.mfa_session_token)
    
    return {
        "success": True,
        "mfa_session_token": data.mfa_session_token,
        "message": "MFA vérifiée avec succès"
    }
