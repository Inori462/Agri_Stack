from typing import Dict, Any, List

class AIAssistantService:
    """
    Multilingual AI Agronomic and Enterprise Assistant.
    Provides expert guidance in English, Hindi (हिंदी), and Marathi (मराठी)
    covering crop selection, government schemes, risk mitigation, and profitability.
    """

    RESPONSES = {
        "crop_recommendation": {
            "en": {
                "title": "AI Crop Recommendation",
                "recommendation": "For Black Cotton / Loamy soil in Kharif, we strongly recommend **Soybean (JS 335 / KDS 726)** intercropped with **Tur / Red Gram (BDN 711)** in a 4:2 row ratio.",
                "rationale": "High yield stability, nitrogen fixation benefits, and strong APMC mandi demand with steady MSP backing.",
                "expected_roi": "35% - 48% estimated ROI per cycle"
            },
            "hi": {
                "title": "एआई फसल सिफ़ारिश",
                "recommendation": "खरीफ में काली / दोमट मिट्टी के लिए, हम **सोयाबीन (JS 335 / KDS 726)** के साथ **अरहर / तूर (BDN 711)** की 4:2 पंक्ति अनुपात में अंतःफसल (intercropping) की सलाह देते हैं।",
                "rationale": "उच्च उपज स्थिरता, मिट्टी में नाइट्रोजन स्थिरीकरण, और न्यूनतम समर्थन मूल्य (MSP) का मजबूत सहारा।",
                "expected_roi": "प्रति चक्र 35% - 48% अनुमानित लाभ (ROI)"
            },
            "mr": {
                "title": "एआय पीक शिफारस",
                "recommendation": "खरीप हंगामात काळ्या / मध्यम पोयट्याच्या जमिनीसाठी **सोयाबीन (JS 335 / KDS 726)** सोबत **तूर (BDN 711)** चे 4:2 पट्ट्यात आंतरपीक घेण्याचा सल्ला दिला जातो.",
                "rationale": "कमी खर्चात हमखास उत्पादन, जमिनीची सुपीकता वाढ, आणि हमीभावाचे (MSP) भक्कम संरक्षण.",
                "expected_roi": "प्रत्येक हंगामात 35% - 48% अपेक्षित नफा (ROI)"
            }
        },
        "scheme_recommendation": {
            "en": {
                "title": "Eligible Government Schemes & Subsidies",
                "schemes": [
                    {
                        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
                        "benefit": "Comprehensive crop insurance with only 2% premium for Kharif and 1.5% for Rabi.",
                        "link": "https://pmfby.gov.in"
                    },
                    {
                        "name": "Nanaji Deshmukh Krishi Sanjivani Prakalp (PoCRA)",
                        "benefit": "Up to 75% subsidy on drip irrigation, farm ponds, and shade nets across Maharashtra.",
                        "link": "https://mahapocra.gov.in"
                    },
                    {
                        "name": "SMAM (Sub-Mission on Agricultural Mechanization)",
                        "benefit": "40% - 50% subsidy on tractor implements, rotavators, and sprayers.",
                        "link": "https://agrimachinery.nic.in"
                    }
                ]
            },
            "hi": {
                "title": "पात्र सरकारी योजनाएं और सब्सिडी",
                "schemes": [
                    {
                        "name": "प्रधानमंत्री फसल बीमा योजना (PMFBY)",
                        "benefit": "खरीफ के लिए केवल 2% और रबी के लिए 1.5% प्रीमियम पर व्यापक फसल सुरक्षा।",
                        "link": "https://pmfby.gov.in"
                    },
                    {
                        "name": "नानाजी देशमुख कृषि संजीवनी प्रकल्प (PoCRA)",
                        "benefit": "महाराष्ट्र में ड्रिप सिंचाई, शेततले और शेडनेट पर 75% तक की सब्सिडी।",
                        "link": "https://mahapocra.gov.in"
                    },
                    {
                        "name": "कृषि यंत्रीकरण उप-मिशन (SMAM)",
                        "benefit": "कृषि उपकरणों और रोटावेटर पर 40% - 50% सरकारी अनुदान।",
                        "link": "https://agrimachinery.nic.in"
                    }
                ]
            },
            "mr": {
                "title": "पात्र शासकीय योजना व अनुदान",
                "schemes": [
                    {
                        "name": "पंतप्रधान पीक विमा योजना (PMFBY)",
                        "benefit": "खरीप पिकांसाठी केवळ 2% तर रब्बीसाठी 1.5% हप्त्यावर सर्वंकष पीक संरक्षण.",
                        "link": "https://pmfby.gov.in"
                    },
                    {
                        "name": "नानाजी देशमुख कृषी संजीवनी प्रकल्प (पोकरा - PoCRA)",
                        "benefit": "ठिबक सिंचन, शेततळे आणि फळबाग लागवडीवर 75% पर्यंत थेट बँक खात्यात अनुदान.",
                        "link": "https://mahapocra.gov.in"
                    },
                    {
                        "name": "मागेल त्याला शेततळे व कृषी यांत्रिकीकरण योजना",
                        "benefit": "ट्रॅक्टर अवजारे, रोटाव्हेटर आणि फवारणी यंत्रांवर 50% पर्यंत शासकीय सवलत.",
                        "link": "https://mahadbt.maharashtra.gov.in"
                    }
                ]
            }
        }
    }

    @staticmethod
    def query_assistant(topic: str, language: str = "en", context_query: str = "") -> Dict[str, Any]:
        """Returns localized agronomic and financial advisory in EN, HI, or MR."""
        lang = language.lower() if language.lower() in ["en", "hi", "mr"] else "en"
        
        # Determine topic
        query_lower = context_query.lower()
        if "scheme" in query_lower or "योजना" in query_lower or "अनुदान" in query_lower or topic == "schemes":
            content = AIAssistantService.RESPONSES["scheme_recommendation"][lang]
            topic_key = "government_schemes"
        else:
            content = AIAssistantService.RESPONSES["crop_recommendation"][lang]
            topic_key = "crop_recommendation"

        return {
            "language": lang,
            "topic": topic_key,
            "response": content,
            "supported_languages": ["en", "hi", "mr"],
            "disclaimer": "AI recommendations are advisory in nature. Please verify local soil test reports before application."
        }
