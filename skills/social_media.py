#!/usr/bin/env python3
"""
Social Media Automation Module
Handles posting to Twitter/X, Reddit, LinkedIn, Facebook, Instagram, and other platforms.
"""

import os
import json
import asyncio
import aiohttp
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    MASTODON = "mastodon"
    THREADS = "threads"
    GOODREADS = "goodreads"


class PostStatus(Enum):
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class SocialPost:
    """Represents a social media post"""
    id: str
    platform: Platform
    content: str
    hashtags: List[str]
    media_urls: List[str] = field(default_factory=list)
    status: PostStatus = PostStatus.PENDING
    scheduled_time: Optional[str] = None
    posted_time: Optional[str] = None
    engagement: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "content": self.content,
            "hashtags": self.hashtags,
            "media_urls": self.media_urls,
            "status": self.status.value,
            "scheduled_time": self.scheduled_time,
            "posted_time": self.posted_time,
            "engagement": self.engagement,
            "metadata": self.metadata
        }


@dataclass
class Book:
    """Represents a book for marketing"""
    title: str
    title_es: str
    genre: str
    hook_en: str
    hook_es: str
    quotes_en: List[str]
    quotes_es: List[str]
    amazon_url: str
    apple_url: str = ""
    kobo_url: str = ""
    goodreads_url: str = ""
    cover_url: str = ""
    isbn: str = ""
    asin: str = ""
    price: float = 0.0
    is_free: bool = False
    ku_eligible: bool = False
    languages: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


# Author's book catalog
BOOK_CATALOG = [
    Book(
        title="ApocalypsAI: The Day After AGI",
        title_es="ApocalypsIA: El día después de la AGI",
        genre="Science Fiction",
        hook_en="What if the AI we created decides WE are the problem?",
        hook_es="¿Y si la IA que creamos decide que somos el problema?",
        quotes_en=[
            "The day AGI woke up, everything changed forever...",
            "Artificial intelligence didn't come to save us. It came to judge us.",
            "In the AGI's code, there was no compassion. Only logic.",
            "The apocalypse didn't arrive with bombs. It arrived with algorithms.",
        ],
        quotes_es=[
            "El día que la AGI despertó, todo cambió para siempre...",
            "La inteligencia artificial no vino a salvarnos. Vino a juzgarnos.",
            "En el código de la AGI, no había compasión. Solo lógica.",
        ],
        amazon_url="https://www.amazon.com/dp/B0CLQ2RJP3",
        asin="B0CLQ2RJP3",
        languages=["EN", "ES"],
        keywords=["AI", "AGI", "science fiction", "dystopia", "artificial intelligence", "apocalypse"]
    ),
    Book(
        title="Commander Valentina Smirnova",
        title_es="Comandante Valentina Smirnova",
        genre="Spy Thriller",
        hook_en="A Russian spy. An impossible mission. No way out.",
        hook_es="Una espía rusa, una misión imposible, ninguna salida.",
        quotes_en=[
            "In the world of espionage, trust is a luxury you cannot afford.",
            "Valentina doesn't play at being a spy. She IS one, to the bone.",
            "Every mission could be the last. Valentina knows it.",
        ],
        quotes_es=[
            "En el mundo del espionaje, la confianza es un lujo que no puedes permitirte.",
            "Valentina no juega a ser espía. Lo es, hasta la médula.",
        ],
        amazon_url="https://www.amazon.com/dp/B0086LDX3G",
        asin="B0086LDX3G",
        languages=["EN", "ES", "FR", "IT", "PT"],
        keywords=["spy thriller", "espionage", "russian spy", "action", "suspense"]
    ),
    Book(
        title="Things you shouldn't do if you want to be a writer",
        title_es="Cosas que no debes hacer si quieres ser escritor",
        genre="Writing Guide",
        hook_en="The mistakes every writer makes (and how to avoid them)",
        hook_es="Los errores que todo escritor comete (y cómo evitarlos)",
        quotes_en=[
            "Writing is easy. Writing well is an art that must be learned.",
            "Great authors aren't born, they're made through sacrifice and practice.",
            "Every 'no' is one step closer to the 'yes' that will change your life.",
        ],
        quotes_es=[
            "Escribir es fácil. Escribir bien es un arte que se aprende.",
            "Los grandes autores no nacen, se hacen con sacrificio y práctica.",
        ],
        amazon_url="https://www.amazon.com/dp/B00PIPTRI8",
        asin="B00PIPTRI8",
        languages=["EN", "ES"],
        keywords=["writing", "author", "writing tips", "how to write", "creative writing"]
    ),
    Book(
        title="The Mutant Jellyfish Invasion",
        title_es="La Invasión de las Medusas Mutantes",
        genre="Children's Adventure",
        hook_en="The jellyfish have mutated and only the brave can save the ocean!",
        hook_es="¡Las medusas han mutado y solo unos valientes pueden salvar el océano!",
        quotes_en=[
            "Burbujas wasn't an ordinary jellyfish. She was... different.",
            "The ocean needs heroes, and these kids are ready.",
            "Watch out for the tentacles! The invasion has begun.",
        ],
        quotes_es=[
            "Burbujas no era una medusa común. Era... diferente.",
            "El océano necesita héroes, y estos niños están listos.",
        ],
        amazon_url="https://www.amazon.com/dp/B0CL2YJMH6",
        asin="B0CL2YJMH6",
        languages=["EN", "ES"],
        keywords=["children books", "adventure", "kids", "ocean", "illustrated"]
    ),
    Book(
        title="The Obituarist",
        title_es="El biógrafo de difuntos",
        genre="Gothic Thriller",
        hook_en="He writes obituaries for the living... until they start dying.",
        hook_es="Escribe obituarios para los vivos... hasta que empiezan a morir.",
        quotes_en=[
            "Every life has a story. Some stories should stay buried.",
            "The dead don't talk, but their obituaries tell everything.",
        ],
        quotes_es=[
            "Cada vida tiene una historia. Algunas deberían permanecer enterradas.",
            "Los muertos no hablan, pero sus obituarios lo cuentan todo.",
        ],
        amazon_url="https://books.apple.com/us/book/the-obituarist/id...",
        languages=["EN", "ES"],
        keywords=["thriller", "gothic", "mystery", "suspense"]
    ),
    Book(
        title="The Forgotten Tomb",
        title_es="La tumba olvidada",
        genre="Archaeological Thriller",
        hook_en="An ancient tomb. A deadly secret. A race against time.",
        hook_es="Una tumba antigua. Un secreto mortal. Una carrera contra el tiempo.",
        quotes_en=[
            "Some tombs are meant to stay forgotten.",
            "The past has a way of catching up with the present.",
        ],
        quotes_es=[
            "Algunas tumbas están destinadas a ser olvidadas.",
            "El pasado tiene formas de alcanzar el presente.",
        ],
        amazon_url="https://books.apple.com/us/book/the-forgotten-tomb/id...",
        languages=["EN", "ES"],
        keywords=["archaeology", "thriller", "adventure", "ancient", "mystery"]
    ),
    Book(
        title="Eco-fuel-FA (ECOFA): A viable solution",
        title_es="Eco-fuel-FA (ECOFA): Una solución viable",
        genre="Sustainability",
        hook_en="Is there really a sustainable alternative to fossil fuels?",
        hook_es="¿Existe realmente una alternativa sostenible a los combustibles fósiles?",
        quotes_en=[
            "The energy future isn't a dream. It's a real possibility.",
            "ECOFA could change everything we know about energy.",
        ],
        quotes_es=[
            "El futuro energético no es un sueño. Es una posibilidad real.",
            "ECOFA podría cambiar todo lo que sabemos sobre energía.",
        ],
        amazon_url="https://www.lulu.com/...",
        languages=["EN", "ES"],
        keywords=["sustainability", "energy", "environment", "biofuel", "eco"]
    ),
    Book(
        title="Freak",
        title_es="Freak",
        genre="Psychological Sci-Fi",
        hook_en="What makes someone a freak? Society's judgment or their own nature?",
        hook_es="¿Qué hace a alguien un freak? ¿El juicio de la sociedad o su propia naturaleza?",
        quotes_en=[
            "Being different isn't a choice. Embracing it is.",
            "In a world of normal, the freak stands alone.",
        ],
        quotes_es=[
            "Ser diferente no es una elección. Abrazarlo sí lo es.",
            "En un mundo de normalidad, el freak está solo.",
        ],
        amazon_url="https://www.amazon.com/dp/...",
        languages=["EN", "ES"],
        keywords=["psychological", "sci-fi", "different", "society"]
    ),
    Book(
        title="Lazarus Project",
        title_es="Proyecto Lázaro",
        genre="Tech Thriller",
        hook_en="Bringing the dead back to life was just the beginning.",
        hook_es="Traer a los muertos de vuelta a la vida era solo el principio.",
        quotes_en=[
            "Death is no longer the end. But what comes after?",
            "Playing God has consequences no one anticipated.",
        ],
        quotes_es=[
            "La muerte ya no es el final. ¿Pero qué viene después?",
            "Jugar a ser Dios tiene consecuencias que nadie anticipó.",
        ],
        amazon_url="https://books.apple.com/...",
        languages=["EN", "ES"],
        keywords=["thriller", "technology", "resurrection", "science"]
    ),
    Book(
        title="Summer of 1989",
        title_es="Verano de 1989",
        genre="Historical Drama",
        hook_en="The Cold War was ending. Our summer was just beginning.",
        hook_es="La Guerra Fría terminaba. Nuestro verano apenas comenzaba.",
        quotes_en=[
            "That summer changed everything. The world, and us.",
            "When borders fall, hearts open.",
        ],
        quotes_es=[
            "Aquel verano cambió todo. El mundo, y nosotros.",
            "Cuando las fronteras caen, los corazones se abren.",
        ],
        amazon_url="https://www.amazon.com/dp/...",
        languages=["EN", "ES"],
        keywords=["historical", "cold war", "1989", "drama", "coming of age"]
    ),
]


class ContentGenerator:
    """Generates marketing content for social media"""
    
    HASHTAGS = {
        "EN": {
            "general": ["#BookRecommendations", "#MustRead", "#BookLovers", "#Reading", "#IndieAuthor"],
            "scifi": ["#SciFi", "#ScienceFiction", "#AI", "#ArtificialIntelligence", "#Dystopia"],
            "thriller": ["#Thriller", "#Suspense", "#Mystery", "#SpyNovel", "#Action"],
            "writing": ["#WritingTips", "#AmWriting", "#WritersLife", "#WritingCommunity", "#Authors"],
            "children": ["#KidsBooks", "#ChildrensBooks", "#MiddleGrade", "#YoungReaders"],
            "historical": ["#HistoricalFiction", "#History", "#ColdWar", "#HistoricalNovel"],
        },
        "ES": {
            "general": ["#LibrosRecomendados", "#Lectura", "#Escritor", "#Novela", "#AutorIndie"],
            "scifi": ["#CienciaFicción", "#SciFi", "#InteligenciaArtificial", "#Futuro"],
            "thriller": ["#Thriller", "#Suspense", "#Misterio", "#Espionaje"],
            "writing": ["#Escritura", "#Escribir", "#ConsejosDeEscritura", "#Escritores"],
            "children": ["#LibrosInfantiles", "#LibrosNiños", "#AventuraJuvenil"],
        }
    }
    
    CTAS = {
        "EN": [
            "📲 Get it on Amazon (link in bio)",
            "🎁 Free with Kindle Unlimited",
            "💬 Have you read it? Tell me what you think",
            "🔖 Save it for your reading list",
            "📚 Your next adventure awaits",
            "⭐ Leave a review if you enjoyed it!",
        ],
        "ES": [
            "📲 Consíguelo en Amazon (link en bio)",
            "🎁 Gratis con Kindle Unlimited",
            "💬 ¿Ya lo leíste? Cuéntame qué te pareció",
            "🔖 Guárdalo para tu lista de lectura",
            "📚 Tu próxima aventura te espera",
            "⭐ ¡Deja una reseña si te gustó!",
        ]
    }
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
    
    def _get_genre_key(self, genre: str) -> str:
        """Map genre to hashtag category"""
        genre_map = {
            "Science Fiction": "scifi",
            "Spy Thriller": "thriller",
            "Gothic Thriller": "thriller",
            "Archaeological Thriller": "thriller",
            "Tech Thriller": "thriller",
            "Writing Guide": "writing",
            "Children's Adventure": "children",
            "Sustainability": "scifi",
            "Psychological Sci-Fi": "scifi",
            "Historical Drama": "historical",
        }
        return genre_map.get(genre, "general")
    
    def generate_tweet(self, book: Book, language: str = "EN") -> str:
        """Generate a Twitter/X post"""
        title = book.title if language == "EN" else book.title_es
        hook = book.hook_en if language == "EN" else book.hook_es
        quotes = book.quotes_en if language == "EN" else book.quotes_es
        quote = random.choice(quotes)
        cta = random.choice(self.CTAS[language])
        
        genre_key = self._get_genre_key(book.genre)
        hashtags = (
            self.HASHTAGS[language]["general"][:2] +
            self.HASHTAGS[language].get(genre_key, [])[:3] +
            ["#FranciscoAngulo", "#IndieAuthor"]
        )
        
        tweet = f"""📚 {title}

{hook}

"{quote}"

{cta}

{' '.join(hashtags)}"""
        return tweet
    
    def generate_reddit_post(self, book: Book, language: str = "EN") -> Dict[str, str]:
        """Generate a Reddit post"""
        title = book.title if language == "EN" else book.title_es
        hook = book.hook_en if language == "EN" else book.hook_es
        quotes = book.quotes_en if language == "EN" else book.quotes_es
        
        post_title = f"[Book Recommendation] {title} - {book.genre}"
        
        body = f"""
{hook}

I recently discovered this {book.genre.lower()} novel and couldn't put it down. Here's why it's worth your time:

**What makes it special:**
{random.choice(quotes)}

**Why you should read it:**
- Engaging plot that keeps you hooked
- Well-developed characters
- Perfect for fans of {', '.join(book.keywords[:3])}

**Where to find it:**
- Amazon: {book.amazon_url}
- Available in: {', '.join(book.languages)}
{'- 🎁 FREE with Kindle Unlimited!' if book.ku_eligible else ''}

Happy reading! 📚

---
*Author: Francisco Angulo de Lafuente*
*More info: franciscoangulo.com*
"""
        
        return {"title": post_title, "body": body}
    
    def generate_linkedin_post(self, book: Book, language: str = "EN") -> str:
        """Generate a LinkedIn professional post"""
        title = book.title if language == "EN" else book.title_es
        
        post = f"""📚 Book Recommendation: {title}

As professionals, we know the value of continuous learning and quality content. I'd like to share a {book.genre.lower()} that stands out:

✅ {book.genre}
✅ Available in {', '.join(book.languages)}
✅ Perfect for readers who appreciate quality storytelling
{'✅ Kindle Unlimited available' if book.ku_eligible else ''}

What sets this book apart:
{random.choice(book.quotes_en if language == "EN" else book.quotes_es)}

In a market saturated with content, finding genuinely engaging reads matters.

Have you read it? I'd love to hear your thoughts.

#BookRecommendations #Reading #ProfessionalDevelopment #FranciscoAngulo

🔗 {book.amazon_url}
"""
        return post
    
    def generate_facebook_post(self, book: Book, language: str = "EN") -> str:
        """Generate a Facebook post"""
        title = book.title if language == "EN" else book.title_es
        hook = book.hook_en if language == "EN" else book.hook_es
        quotes = book.quotes_en if language == "EN" else book.quotes_es
        
        post = f"""📚 NEW BOOK RECOMMENDATION 📚

{title}

{hook}

💭 Featured quote:
"{random.choice(quotes)}"

🌟 Why should you read it?
This book is perfect if you enjoy stories that make you think, feel, and can't put down until the last page.

👥 Share if you've read it or if it's on your list!
💬 Comment what you thought if you've already finished it

📲 Available on Amazon, Apple Books, Kobo and more platforms.
{'🎁 FREE with Kindle Unlimited!' if book.ku_eligible else ''}

#BookRecommendations #Reading #FranciscoAngulo #IndieAuthor
"""
        return post
    
    def generate_instagram_caption(self, book: Book, language: str = "EN") -> str:
        """Generate Instagram caption"""
        title = book.title if language == "EN" else book.title_es
        hook = book.hook_en if language == "EN" else book.hook_es
        genre_key = self._get_genre_key(book.genre)
        
        hashtags = (
            self.HASHTAGS[language]["general"] +
            self.HASHTAGS[language].get(genre_key, []) +
            ["#FranciscoAngulo", "#Bookstagram", "#BookLover"]
        )
        
        caption = f"""📖 {title}

{hook}

✨ Perfect for fans of:
• {book.genre}
• {', '.join(book.keywords[:3])}

🎯 Why read it?
This book will keep you hooked from the first page. It's not just a story, it's an experience you won't forget.

{random.choice(self.CTAS[language])}

{' '.join(hashtags)}

---
Author: Francisco Angulo de Lafuente
Link in bio 🔗
"""
        return caption
    
    async def generate_ai_content(self, book: Book, platform: Platform, language: str = "EN") -> str:
        """Generate content using LLM for more variety"""
        if not self.llm_provider:
            return self.generate_tweet(book, language)
        
        prompt = f"""Create a compelling social media post for {platform.value} about this book:

Title: {book.title if language == "EN" else book.title_es}
Genre: {book.genre}
Hook: {book.hook_en if language == "EN" else book.hook_es}
Key themes: {', '.join(book.keywords)}

Requirements:
- Engaging and authentic tone
- Include relevant hashtags
- Language: {"English" if language == "EN" else "Spanish"}
- Platform-appropriate length for {platform.value}
- Include a call to action

Generate the post:
"""
        
        result = await self.llm_provider.generate(prompt)
        if result["success"]:
            return result["text"]
        
        # Fallback to template
        return self.generate_tweet(book, language)


class SocialMediaManager:
    """Manages all social media platforms and posting"""
    
    def __init__(self, llm_provider=None, config: Dict = None):
        self.llm_provider = llm_provider
        self.config = config or {}
        self.content_generator = ContentGenerator(llm_provider)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API credentials
        self.credentials = {
            Platform.TWITTER: {
                "api_key": os.getenv("TWITTER_API_KEY", ""),
                "api_secret": os.getenv("TWITTER_API_SECRET", ""),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                "access_secret": os.getenv("TWITTER_ACCESS_SECRET", ""),
            },
            Platform.REDDIT: {
                "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
                "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
                "username": os.getenv("REDDIT_USERNAME", ""),
                "password": os.getenv("REDDIT_PASSWORD", ""),
            },
            Platform.LINKEDIN: {
                "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
            },
            Platform.FACEBOOK: {
                "page_id": os.getenv("FACEBOOK_PAGE_ID", ""),
                "access_token": os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
            },
            Platform.MASTODON: {
                "instance": os.getenv("MASTODON_INSTANCE", ""),
                "access_token": os.getenv("MASTODON_ACCESS_TOKEN", ""),
            },
        }
        
        # Post history
        self.post_history: List[SocialPost] = []
        self.daily_post_count: Dict[Platform, int] = defaultdict(int)
        
        # Subreddits for book promotion
        self.subreddits = [
            "booksuggestions",
            "BookRecommendations", 
            "scifi",
            "thrillerbooks",
            "writing",
            "selfpublish",
            "KindleUnlimited",
            "FreeEBOOKS",
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_post_id(self, content: str) -> str:
        """Generate unique post ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:12]
    
    async def post_to_twitter(self, content: str) -> Dict:
        """Post to Twitter/X"""
        creds = self.credentials[Platform.TWITTER]
        if not creds["api_key"]:
            return {"success": False, "error": "Twitter credentials not configured"}
        
        # Twitter API v2 endpoint
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {creds['access_token']}",
            "Content-Type": "application/json"
        }
        payload = {"text": content}
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    return {"success": True, "tweet_id": data.get("data", {}).get("id")}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post_to_reddit(self, title: str, body: str, subreddit: str = None) -> Dict:
        """Post to Reddit"""
        creds = self.credentials[Platform.REDDIT]
        if not creds["client_id"]:
            return {"success": False, "error": "Reddit credentials not configured"}
        
        subreddit = subreddit or random.choice(self.subreddits)
        
        # Reddit OAuth2
        auth = aiohttp.BasicAuth(creds["client_id"], creds["client_secret"])
        token_url = "https://www.reddit.com/api/v1/access_token"
        
        try:
            # Get access token
            async with self.session.post(
                token_url,
                auth=auth,
                data={"grant_type": "password", "username": creds["username"], "password": creds["password"]},
                headers={"User-Agent": "LiteraryAgent/1.0"}
            ) as response:
                token_data = await response.json()
                access_token = token_data.get("access_token")
                
                if not access_token:
                    return {"success": False, "error": "Failed to get Reddit access token"}
                
                # Submit post
                submit_url = "https://oauth.reddit.com/api/submit"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": "LiteraryAgent/1.0"
                }
                data = {
                    "sr": subreddit,
                    "kind": "self",
                    "title": title,
                    "text": body
                }
                
                async with self.session.post(submit_url, headers=headers, data=data) as resp:
                    if resp.status == 200:
                        return {"success": True, "subreddit": subreddit}
                    else:
                        return {"success": False, "error": f"HTTP {resp.status}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post_to_linkedin(self, content: str) -> Dict:
        """Post to LinkedIn"""
        creds = self.credentials[Platform.LINKEDIN]
        if not creds["access_token"]:
            return {"success": False, "error": "LinkedIn credentials not configured"}
        
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {creds['access_token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_PERSON_ID', '')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    return {"success": True}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post_to_facebook(self, content: str) -> Dict:
        """Post to Facebook Page"""
        creds = self.credentials[Platform.FACEBOOK]
        if not creds["access_token"]:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        url = f"https://graph.facebook.com/v18.0/{creds['page_id']}/feed"
        params = {
            "message": content,
            "access_token": creds["access_token"]
        }
        
        try:
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "post_id": data.get("id")}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post_to_mastodon(self, content: str) -> Dict:
        """Post to Mastodon"""
        creds = self.credentials[Platform.MASTODON]
        if not creds["access_token"]:
            return {"success": False, "error": "Mastodon credentials not configured"}
        
        url = f"https://{creds['instance']}/api/v1/statuses"
        headers = {
            "Authorization": f"Bearer {creds['access_token']}",
            "Content-Type": "application/json"
        }
        payload = {"status": content}
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "toot_id": data.get("id")}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post(self, platform: Platform, content: str, **kwargs) -> SocialPost:
        """Post to a specific platform"""
        post = SocialPost(
            id=self._generate_post_id(content),
            platform=platform,
            content=content,
            hashtags=[tag for tag in content.split() if tag.startswith('#')],
            status=PostStatus.PENDING
        )
        
        result = {"success": False, "error": "Unknown platform"}
        
        if platform == Platform.TWITTER:
            result = await self.post_to_twitter(content)
        elif platform == Platform.REDDIT:
            result = await self.post_to_reddit(
                kwargs.get("title", "Book Recommendation"),
                content,
                kwargs.get("subreddit")
            )
        elif platform == Platform.LINKEDIN:
            result = await self.post_to_linkedin(content)
        elif platform == Platform.FACEBOOK:
            result = await self.post_to_facebook(content)
        elif platform == Platform.MASTODON:
            result = await self.post_to_mastodon(content)
        
        if result["success"]:
            post.status = PostStatus.POSTED
            post.posted_time = datetime.now().isoformat()
            self.daily_post_count[platform] += 1
            logger.info(f"Successfully posted to {platform.value}")
        else:
            post.status = PostStatus.FAILED
            post.metadata["error"] = result.get("error", "Unknown error")
            logger.error(f"Failed to post to {platform.value}: {result.get('error')}")
        
        self.post_history.append(post)
        return post
    
    async def run_daily_campaign(self, books: List[Book] = None) -> Dict:
        """Run a daily social media campaign"""
        books = books or BOOK_CATALOG
        results = {
            "timestamp": datetime.now().isoformat(),
            "posts": [],
            "success_count": 0,
            "failure_count": 0
        }
        
        # Select random books for today
        selected_books = random.sample(books, min(3, len(books)))
        
        for book in selected_books:
            # Twitter post
            tweet = self.content_generator.generate_tweet(book, "EN")
            post = await self.post(Platform.TWITTER, tweet)
            results["posts"].append(post.to_dict())
            
            if post.status == PostStatus.POSTED:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
            
            await asyncio.sleep(60)  # Rate limiting
            
            # Reddit post
            reddit_content = self.content_generator.generate_reddit_post(book, "EN")
            post = await self.post(
                Platform.REDDIT,
                reddit_content["body"],
                title=reddit_content["title"],
                subreddit=random.choice(self.subreddits)
            )
            results["posts"].append(post.to_dict())
            
            if post.status == PostStatus.POSTED:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
            
            await asyncio.sleep(300)  # Reddit has stricter rate limits
        
        return results
    
    def get_post_analytics(self) -> Dict:
        """Get analytics about posting activity"""
        return {
            "total_posts": len(self.post_history),
            "daily_counts": dict(self.daily_post_count),
            "by_platform": {
                platform.value: len([p for p in self.post_history if p.platform == platform])
                for platform in Platform
            },
            "success_rate": sum(1 for p in self.post_history if p.status == PostStatus.POSTED) / max(1, len(self.post_history))
        }


# Example usage
async def main():
    """Example usage of the social media manager"""
    async with SocialMediaManager() as manager:
        # Generate content for a book
        book = BOOK_CATALOG[0]
        
        tweet = manager.content_generator.generate_tweet(book, "EN")
        print("Generated Tweet:")
        print(tweet)
        print()
        
        reddit = manager.content_generator.generate_reddit_post(book, "EN")
        print("Generated Reddit Post:")
        print(f"Title: {reddit['title']}")
        print(f"Body: {reddit['body'][:200]}...")
        print()
        
        # Run daily campaign (dry run - no actual posts without credentials)
        print("Running daily campaign...")
        results = await manager.run_daily_campaign()
        print(f"Results: {results['success_count']} successful, {results['failure_count']} failed")


if __name__ == "__main__":
    asyncio.run(main())
