"""
BanglaMind — Response Templates
=================================
প্রতিটি intent-এর জন্য default বাংলা reply template।

Business owner পরে Dashboard থেকে এগুলো customize করতে পারবে।
এখন generic replies রয়েছে, যেগুলো business-র নাম দিয়ে
{business_name} placeholder fill হবে।
"""

import random
from typing import Optional


# ─── Response Templates ───────────────────────────────────────────────────────
# প্রতিটি intent-এ একাধিক reply আছে — randomly একটা বাছাই হবে
# এতে chatbot "robotic" মনে হবে না

TEMPLATES: dict[str, list[str]] = {

    "greeting": [
        "আস্সালামু আলাইকুম! 😊 {business_name}-তে আপনাকে স্বাগতম। আমি কীভাবে সাহায্য করতে পারি?",
        "হ্যালো! {business_name}-এ আপনাকে স্বাগত জানাই। আপনার কী জানার আছে?",
        "ওয়ালাইকুম আস্সালাম! {business_name}-এ আপনাকে স্বাগতম। 🌟 কী জানতে চান?",
        "হ্যালো! আমাদের সাথে যোগাযোগ করার জন্য ধন্যবাদ। আপনাকে কীভাবে সাহায্য করতে পারি?",
    ],

    "price_inquiry": [
        "আমাদের পণ্যের দাম সম্পর্কে জানতে, দয়া করে নির্দিষ্ট পণ্যের নাম বলুন। আমরা আপনাকে সঠিক মূল্য জানাব। 💰",
        "আপনি কোন পণ্যের দাম জানতে চাইছেন? নাম জানালে সাথে সাথে বলতে পারব।",
        "আমাদের দামের তালিকার জন্য একটু অপেক্ষা করুন। কোন পণ্যে আগ্রহী?",
    ],

    "location": [
        "📍 আমাদের ঠিকানা: {business_address}\n\nআরো বিস্তারিত জানতে আমাদের সাথে যোগাযোগ করুন।",
        "আমাদের দোকান/অফিস এখানে অবস্থিত: {business_address} 📍\nআপনি গুগল ম্যাপে 'সার্চ করতে পারেন।",
        "আমরা {business_address} এ আছি। আসার আগে ফোন করে নিলে ভালো হয়! 📞",
    ],

    "hours": [
        "🕐 আমাদের কার্যক্রমের সময়:\n{business_hours}\n\nছুটির দিন ব্যতীত আমরা সবসময় সেবায় প্রস্তুত!",
        "আমরা {business_hours} পর্যন্ত খোলা থাকি। ⏰ এই সময়ের মধ্যে আসুন!",
        "আমাদের খোলার সময়: {business_hours} 🕙\nআরো তথ্যের জন্য ফোন করুন।",
    ],

    "product_info": [
        "আমাদের কাছে বিভিন্ন ধরনের পণ্য/সেবা পাওয়া যায়। কোন বিষয়ে আগ্রহী? একটু বিস্তারিত বললে সাহায্য করতে পারব। 🛍️",
        "আমাদের পণ্য সম্পর্কে জানতে চান? নির্দিষ্ট পণ্যের নাম বললে আরো ভালোভাবে সাহায্য করতে পারব!",
        "আমাদের সার্ভিস সম্পর্কে জানতে চাইলে বলুন। আপনার কী দরকার সেটা জানালে সেরাটা দেওয়ার চেষ্টা করব। ✨",
    ],

    "order": [
        "অর্ডার দিতে চাইলে আমাদের {contact_number} নম্বরে ফোন করুন অথবা এখানেই বিস্তারিত জানান। 📦",
        "আপনার অর্ডারের জন্য ধন্যবাদ! 🎉 কী অর্ডার করতে চান এবং পরিমাণ জানালে প্রক্রিয়া শুরু করতে পারব।",
        "অর্ডার করতে চাইলে পণ্যের নাম, পরিমাণ এবং ডেলিভারির ঠিকানা জানান। আমরা যোগাযোগ করব! ✅",
    ],

    "delivery": [
        "হ্যাঁ, আমরা হোম ডেলিভারি দিই! 🚚 ডেলিভারি চার্জ ও সময় এলাকাভেদে ভিন্ন হতে পারে। বিস্তারিত জানাতে ফোন করুন।",
        "ডেলিভারি পাওয়া যায়! 📦 আপনার এলাকার নাম জানালে ডেলিভারি চার্জ এবং সময় বলতে পারব।",
        "আমরা ডেলিভারি সার্ভিস দিয়ে থাকি। অর্ডারের ঠিকানা ও যোগাযোগ নম্বর দিলে বাকিটা আমরা সামলে নেব! 🚀",
    ],

    "contact": [
        "📞 আমাদের সাথে যোগাযোগ:\nফোন: {contact_number}\n\nযেকোনো প্রশ্নে নির্দ্বিধায় কল করুন!",
        "আমাদের যোগাযোগ করুন: 📱\nফোন: {contact_number}\nআমরা সাহায্য করতে সদা প্রস্তুত!",
        "যোগাযোগের জন্য: {contact_number} 📞\nঅথবা এই মেসেজেই বিস্তারিত জানান।",
    ],

    "complaint": [
        "আপনার অসুবিধার জন্য আমরা আন্তরিকভাবে দুঃখিত। 🙏 সমস্যার বিস্তারিত জানান, আমরা দ্রুত সমাধান করব।",
        "আপনার অভিযোগটি আমরা গুরুত্বের সাথে দেখছি। বিস্তারিত বললে আমরা সাথে সাথে ব্যবস্থা নেব। 🙏",
        "দুঃখিত আপনি এই সমস্যায় পড়েছেন! আপনার অর্ডার নম্বর বা বিস্তারিত তথ্য দিলে আমরা সমাধান করতে পারব। 💪",
    ],

    "thanks": [
        "আপনাকে অনেক ধন্যবাদ! 😊 আর কোনো প্রশ্ন থাকলে যেকোনো সময় জানাবেন।",
        "ধন্যবাদ! {business_name}-এর সাথে থাকার জন্য কৃতজ্ঞ। 🌟 আবার আসবেন!",
        "আপনার মতো গ্রাহকের জন্যই আমরা কাজ করি। ধন্যবাদ! 💚",
    ],

    "fallback": [
        "দুঃখিত, আপনার প্রশ্নটি আমি সম্পূর্ণরূপে বুঝতে পারিনি। 😅 একটু অন্যভাবে বলবেন?\n\nঅথবা সরাসরি {contact_number}-এ ফোন করুন।",
        "আমি এখনো শিখছি! 🤖 এই বিষয়টি আমাকে আরেকটু বুঝিয়ে বলুন।\nজরুরি হলে {contact_number}-এ যোগাযোগ করুন।",
        "আপনার প্রশ্নটি আমার কাছে একটু অস্পষ্ট মনে হচ্ছে। 😊 ভিন্নভাবে জিজ্ঞেস করুন বা {contact_number}-এ সরাসরি কথা বলুন।",
    ],
}

# ─── Default Business Config (Dashboard থেকে replace হবে) ────────────────────
DEFAULT_BUSINESS_CONFIG = {
    "business_name": "আমাদের প্রতিষ্ঠান",
    "business_address": "ঢাকা, বাংলাদেশ (বিস্তারিত শীঘ্রই আসছে)",
    "business_hours": "সকাল ৯টা - রাত ৯টা (শুক্রবার বন্ধ)",
    "contact_number": "01XXXXXXXXX",
}


# ─── Response Generator ───────────────────────────────────────────────────────
class ResponseGenerator:
    """
    Intent tag দেখে সঠিক বাংলা reply generate করো।

    Usage:
        generator = ResponseGenerator()
        reply = generator.get_reply("price_inquiry")
        # Returns: "আমাদের পণ্যের দাম সম্পর্কে জানতে..."
    """

    def __init__(self, business_config: Optional[dict] = None):
        """
        Args:
            business_config: Business-র নাম, ঠিকানা, সময় ইত্যাদি।
                             None হলে default config ব্যবহার হবে।
        """
        self.config = business_config or DEFAULT_BUSINESS_CONFIG
        self.templates = TEMPLATES

    def get_reply(self, intent_tag: str) -> str:
        """
        Intent tag দেখে একটা বাংলা reply return করো।

        Args:
            intent_tag: যেমন "greeting", "price_inquiry", "fallback"

        Returns:
            Formatted বাংলা reply string
        """
        # Intent-এর template list খোঁজো
        templates_list = self.templates.get(intent_tag)

        # Unknown intent হলে fallback
        if not templates_list:
            templates_list = self.templates["fallback"]

        # Random একটা template বাছাই করো
        template = random.choice(templates_list)

        # Business config দিয়ে placeholder fill করো
        try:
            reply = template.format(**self.config)
        except KeyError:
            # Template-এ কোনো key না থাকলে as-is return করো
            reply = template

        return reply

    def update_config(self, new_config: dict) -> None:
        """Business config আপডেট করো (Dashboard থেকে call হবে)।"""
        self.config.update(new_config)
