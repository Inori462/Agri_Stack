import uuid
from typing import Dict, Any, Optional

class DigiLockerAdapter:
    """
    Adapter for DigiLocker API integration (Sandbox/Mock).
    Simulates fetching verified Aadhaar profile, PAN, and land records from DigiLocker.
    """

    @staticmethod
    def get_authorization_url(redirect_uri: str, state: str) -> str:
        """Returns the OAuth2 consent URL for DigiLocker sandbox."""
        return f"https://api.digitallocker.gov.in/public/oauth2/1/authorize?response_type=code&client_id=agristack_sandbox&redirect_uri={redirect_uri}&state={state}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Simulates exchanging authorization code for access token."""
        return {
            "access_token": f"dl_access_{uuid.uuid4().hex[:16]}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "digilocker_id": f"DL-IND-{uuid.uuid4().hex[:8].upper()}"
        }

    @staticmethod
    def pull_aadhaar_profile(access_token: str) -> Dict[str, Any]:
        """
        Simulates pulling verified e-Aadhaar XML data from DigiLocker.
        Returns masked Aadhaar and verified name.
        """
        return {
            "verified": True,
            "name": "Ramesh Tukaram Patil",
            "dob": "1982-05-14",
            "gender": "M",
            "address": {
                "village": "Pimpalgaon",
                "taluka": "Niphad",
                "district": "Nashik",
                "state": "Maharashtra",
                "pincode": "422209"
            },
            "masked_aadhaar": "XXXX-XXXX-8421",
            "aadhaar_hash_sample": "c5f11a8b23490fd38e91845bb290ef410a51c726710b91cb52d80d21e847c21f",
            "issuer": "UIDAI",
            "digilocker_doc_uri": f"in.gov.uidai-aadhaar-{uuid.uuid4().hex[:12]}"
        }

    @staticmethod
    def pull_pan_profile(pan_number: str) -> Dict[str, Any]:
        """Simulates verifying PAN with NSDL/DigiLocker."""
        clean_pan = pan_number.upper().strip()
        is_valid = len(clean_pan) == 10 and clean_pan[:5].isalpha() and clean_pan[5:9].isdigit() and clean_pan[9].isalpha()
        return {
            "verified": is_valid,
            "pan": f"{clean_pan[:2]}XXXXX{clean_pan[-2:]}" if is_valid else clean_pan,
            "name_on_card": "RAMESH TUKARAM PATIL",
            "status": "VALID_OPERATIVE" if is_valid else "INVALID_FORMAT"
        }
