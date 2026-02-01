import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dictionary.settings')
django.setup()

from api.models import WordModel, PostCategoryModel, PostModel, FooterModel, HeaderModel, PageModel, BlogModel, FeatureModel
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import requests

def seed_data():
    print("Seeding data...")

    # 1. Header
    HeaderModel.objects.all().delete()
    HeaderModel.objects.create(
        site_title="MeaningBy",
        # Logo normally requires a file, we'll leave it blank or handle as default
    )
    print("Header seeded.")

    # 2. Footer
    FooterModel.objects.all().delete()
    FooterModel.objects.create(heading="About Us", description="MeaningBy is your ultimate companion for exploring language. Our mission is to provide accurate, easy-to-understand definitions and linguistic insights to learners and wordsmiths worldwide.")
    FooterModel.objects.create(heading="Contact Info", description="Email: support@meaningby.com<br>Phone: +1 234 567 890<br>Address: 123 Linguistics Way, Word City")
    FooterModel.objects.create(heading="Quick Links", description="Privacy Policy<br>Terms of Service<br>Cookie Policy")
    print("Footer seeded.")

    # 3. Post Categories
    PostCategoryModel.objects.all().delete()
    cat_general = PostCategoryModel.objects.create(cat_title="General Vocabulary", cat_order=1)
    cat_grammar = PostCategoryModel.objects.create(cat_title="Grammar Tips", cat_order=2)
    cat_idioms = PostCategoryModel.objects.create(cat_title="Idioms & Phrases", cat_order=3)
    print("Categories seeded.")

    # 4. Words
    WordModel.objects.all().delete()
    words = [
        {"word": "Serendipity", "synonyms": "fluke, chance", "antonyms": "misfortune", "example": "Finding that old photograph was pure serendipity.", "description": "<p>The occurrence and development of events by chance in a happy or beneficial way.</p>"},
        {"word": "Ephemeral", "synonyms": "transient, fleeting", "antonyms": "permanent", "example": "The beauty of a sunset is ephemeral.", "description": "<p>Lasting for a very short time.</p>"},
        {"word": "Eloquent", "synonyms": "fluent, silver-tongued", "antonyms": "inarticulate", "example": "She made an eloquent speech at the wedding.", "description": "<p>Fluent or persuasive in speaking or writing.</p>"},
    ]
    for w in words:
        WordModel.objects.create(**w)
    print("Words seeded.")

    # 5. Features
    FeatureModel.objects.all().delete()
    features = [
        {"title": "Instant Search", "description": "Search for thousands of words instantly with our high-speed lookup engine."},
        {"title": "Word of the Day", "description": "Expand your vocabulary every single day with hand-picked interesting words."},
        {"title": "Usage Examples", "description": "Learn how to use words correctly with deep context and real-world sentences."},
        {"title": "Audio Pronunciation", "description": "Hear how native speakers pronounce words to improve your speaking skills."},
    ]
    for f in features:
        FeatureModel.objects.create(**f)
    print("Features seeded.")

    # 6. Blogs
    BlogModel.objects.all().delete()
    blogs = [
        {"blog_title": "How to Master New Words", "blog_description": "Learning new words is more than just memorization. It's about context and frequency...", "blog_author": "Admin", "post_Cat": cat_general},
        {"blog_title": "The Evolution of English Idioms", "blog_description": "Did you know 'beating around the bush' has its roots in mid-14th century hunting?", "blog_author": "Expert", "post_Cat": cat_idioms},
    ]
    for b in blogs:
        BlogModel.objects.create(**b)
    print("Blogs seeded.")

    # 7. Posts (under features)
    PostModel.objects.all().delete()
    posts = [
        {"title": "Introduction to Linguistics", "full_desc": "Explore the scientific study of language and its structure...", "postCat": cat_general},
        {"title": "Grammar: Active vs Passive", "full_desc": "Understand the impact of voice in your writing style...", "postCat": cat_grammar},
    ]
    for p in posts:
        PostModel.objects.create(**p)
    print("Posts seeded.")

    # 8. Pages
    PageModel.objects.all().delete()
    PageModel.objects.create(page_title="About Us", page_description="<h1>Our Mission</h1><p>We aim to make the world's vocabulary accessible to everyone.</p>")
    print("Pages seeded.")

    print("Successfully seeded all data!")

if __name__ == "__main__":
    seed_data()
