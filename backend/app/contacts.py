"""Curated contacts; generation can select IDs but cannot invent phone numbers."""
from .schemas import Contact

CONTACTS = [
    Contact(id='emergency', name='Emergency Response Support System', scope='India — immediate danger', phone='112', url='https://112.gov.in/', checked_on='2026-10-09'),
    Contact(id='legal_aid', name='NALSA / District Legal Services Authority', scope='India — legal aid; eligibility and availability vary', phone='15100', url='https://nalsa.gov.in/', checked_on='2026-10-09'),
    Contact(id='maharashtra_acb', name='Maharashtra Anti-Corruption Bureau', scope='Maharashtra only — bribery complaints involving state public servants', phone='1064', url='https://acb.maharashtra.gov.in/', checked_on='2026-10-09'),
    Contact(id='cyber', name='National Cyber Crime Reporting Portal', scope='India — financial cyber fraud', phone='1930', url='https://cybercrime.gov.in/', checked_on='2026-10-09'),
    Contact(id='consumer', name='National Consumer Helpline', scope='India — consumer grievances', phone='1915', url='https://consumerhelpline.gov.in/', checked_on='2026-10-09'),
]
BY_ID = {c.id: c for c in CONTACTS}

LOCAL_LABELS = {
    'hi': {
        'emergency': ('आपातकालीन प्रतिक्रिया सहायता प्रणाली', 'भारत — तत्काल खतरा'),
        'legal_aid': ('NALSA / जिला विधिक सेवा प्राधिकरण', 'भारत — कानूनी सहायता; पात्रता और उपलब्धता अलग हो सकती है'),
        'maharashtra_acb': ('महाराष्ट्र भ्रष्टाचार निरोधक ब्यूरो', 'केवल महाराष्ट्र — राज्य के लोक सेवकों से संबंधित रिश्वत की शिकायतें'),
        'cyber': ('राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल', 'भारत — वित्तीय साइबर धोखाधड़ी'),
        'consumer': ('राष्ट्रीय उपभोक्ता हेल्पलाइन', 'भारत — उपभोक्ता शिकायतें'),
    },
    'mr': {
        'emergency': ('आपत्कालीन प्रतिसाद सहाय्य प्रणाली', 'भारत — तात्काळ धोका'),
        'legal_aid': ('NALSA / जिल्हा विधी सेवा प्राधिकरण', 'भारत — कायदेशीर मदत; पात्रता आणि उपलब्धता बदलू शकते'),
        'maharashtra_acb': ('महाराष्ट्र लाचलुचपत प्रतिबंधक विभाग', 'फक्त महाराष्ट्र — राज्य लोकसेवकांविरुद्ध लाचेच्या तक्रारी'),
        'cyber': ('राष्ट्रीय सायबर गुन्हे तक्रार पोर्टल', 'भारत — आर्थिक सायबर फसवणूक'),
        'consumer': ('राष्ट्रीय ग्राहक हेल्पलाइन', 'भारत — ग्राहक तक्रारी'),
    },
}

def localized(contact, language):
    labels = LOCAL_LABELS.get(language, {}).get(contact.id)
    return contact.model_copy(update={'name': labels[0], 'scope': labels[1]}) if labels else contact
