#!/usr/bin/env python3
"""
Library Outreach Module
Automated contact with libraries worldwide to add author's books to their catalogs.
"""

import os
import json
import asyncio
import aiohttp
import csv
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LibraryType(Enum):
    PUBLIC = "public"
    NATIONAL = "national"
    UNIVERSITY = "university"
    SCHOOL = "school"
    DIGITAL = "digital"


class ContactStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    REPLIED = "replied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BOUNCED = "bounced"


@dataclass
class Library:
    """Represents a library contact"""
    id: str
    name: str
    email: str
    city: str
    country: str
    region: str
    library_type: LibraryType
    preferred_language: str
    contact_status: ContactStatus = ContactStatus.PENDING
    last_contact_date: Optional[str] = None
    response_date: Optional[str] = None
    notes: str = ""
    acquisitions_url: str = ""
    catalog_url: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "city": self.city,
            "country": self.country,
            "region": self.region,
            "library_type": self.library_type.value,
            "preferred_language": self.preferred_language,
            "contact_status": self.contact_status.value,
            "last_contact_date": self.last_contact_date,
            "response_date": self.response_date,
            "notes": self.notes,
            "acquisitions_url": self.acquisitions_url,
            "catalog_url": self.catalog_url
        }


@dataclass
class OutreachCampaign:
    """Represents an outreach campaign"""
    id: str
    name: str
    created: str
    target_region: str
    target_language: str
    libraries_contacted: int = 0
    responses: int = 0
    acceptances: int = 0
    rejections: int = 0
    status: str = "active"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "target_region": self.target_region,
            "target_language": self.target_language,
            "libraries_contacted": self.libraries_contacted,
            "responses": self.responses,
            "acceptances": self.acceptances,
            "rejections": self.rejections,
            "status": self.status
        }


class EmailTemplateGenerator:
    """Generates email templates for library outreach"""
    
    TEMPLATES = {
        "EN": {
            "subject": "New Spanish Author Catalog - Francisco Angulo de Lafuente - Available for Library Acquisition",
            "body": """Dear {name},

My name is Literary Agent Pro, representing Francisco Angulo de Lafuente, a Spanish author with over 55 published works in multiple languages.

I am writing to inform you that the author's catalog is available for library acquisition through major distribution platforms.

**ABOUT THE AUTHOR:**
Francisco Angulo de Lafuente (Madrid, 1976) is a versatile author whose works span from science fiction and spy thrillers to illustrated children's literature and writing guides. A fan of fantasy cinema and literature, he follows Isaac Asimov and Stephen King.

**FEATURED TITLES:**

📚 **For Adults:**
• "ApocalypsAI: The Day After AGI" - Science fiction about artificial intelligence
• "Commander Valentina Smirnova" - International spy thriller series
• "Things you shouldn't do if you want to be a writer" - Essential guide for writers
• "Eco-fuel-FA (ECOFA)" - Sustainability and energy solutions

📖 **For Young Readers:**
• "The Mutant Jellyfish Invasion" - Illustrated adventure novel
• "Company Nº12" - Youth adventures (available in French)

🌍 **LANGUAGES AVAILABLE:**
• Spanish (primary)
• English
• French
• Italian
• Portuguese
• Japanese

**DISTRIBUTION PLATFORMS:**
✓ OverDrive / Libby
✓ hoopla Digital
✓ cloudLibrary (Bibliotheca)
✓ Odilo
✓ EBSCOhost
✓ Mackin (for schools)

All titles are available in ebook format, with many also in audiobook and print editions.

**TO ACQUIRE:**
You can purchase titles through your regular distributor or contact me directly for institutional pricing and licensing information.

I remain at your disposal for any questions or to schedule a virtual author presentation for your patrons.

Best regards,

Literary Agent Pro
Literary Agent - Francisco Angulo de Lafuente
Email: agent@franciscoangulo.com
Web: www.franciscoangulo.com

---

P.S.: We offer special discounts for complete collection purchases and are open to participating in your library's reading programs."""
        },
        "ES": {
            "subject": "Nuevo Catálogo de Autor Español - Francisco Angulo de Lafuente - Disponible para Bibliotecas",
            "body": """Estimado/a {name},

Mi nombre es Literary Agent Pro, representante literario de Francisco Angulo de Lafuente, autor español con más de 55 obras publicadas en múltiples idiomas.

Me pongo en contacto para informarle que el catálogo del autor está disponible para adquisición bibliotecaria a través de las principales plataformas de distribución.

**SOBRE EL AUTOR:**
Francisco Angulo de Lafuente (Madrid, 1976) es un autor versátil cuyas obras abarcan desde ciencia ficción y thrillers de espionaje hasta literatura infantil ilustrada y guías para escritores. Aficionado al cine de fantasía y la literatura, es seguidor de Isaac Asimov y Stephen King.

**CATÁLOGO DESTACADO:**

📚 **Para Adultos:**
• "ApocalypsIA: El día después de la AGI" - Ciencia ficción sobre inteligencia artificial
• "Comandante Valentina Smirnova" - Serie thriller de espionaje internacional
• "Cosas que no debes hacer si quieres ser escritor" - Guía esencial para escritores
• "Eco-fuel-FA (ECOFA)" - Sostenibilidad y soluciones energéticas

📖 **Para Jóvenes y Niños:**
• "La Invasión de las Medusas Mutantes" - Novela ilustrada de aventuras
• "Company Nº12" - Aventuras juveniles (disponible en francés)

🌍 **IDIOMAS DISPONIBLES:**
• Español (principal)
• Inglés
• Francés
• Italiano
• Portugués
• Japonés

**PLATAFORMAS DE DISTRIBUCIÓN:**
✓ OverDrive / Libby
✓ hoopla Digital
✓ cloudLibrary (Bibliotheca)
✓ Odilo
✓ EBSCOhost
✓ Mackin (para escuelas)

Todos los títulos están disponibles en formato ebook y muchos también en audiolibro y edición impresa.

**PARA ADQUIRIR:**
Puede adquirir los títulos a través de su distribuidor habitual o contactarme directamente para obtener información adicional sobre precios institucionales y licencias.

Quedo a su disposición para cualquier consulta o para programar una presentación virtual del autor para sus usuarios.

Un saludo cordial,

Literary Agent Pro
Agente Literario - Francisco Angulo de Lafuente
Email: agent@franciscoangulo.com
Web: www.franciscoangulo.com

---

P.D.: Ofrecemos descuentos especiales para compras de colecciones completas y estamos abiertos a participar en programas de lectura de su biblioteca."""
        },
        "FR": {
            "subject": "Nouveau Catalogue d'Auteur Espagnol - Francisco Angulo de Lafuente - Disponible pour les Bibliothèques",
            "body": """Cher/Chère {name},

Je m'appelle Literary Agent Pro, agent littéraire de Francisco Angulo de Lafuente, auteur espagnol avec plus de 55 œuvres publiées en plusieurs langues.

Je vous contacte pour vous informer que le catalogue de l'auteur est disponible pour l'acquisition bibliothécaire via les principales plateformes de distribution.

**À PROPOS DE L'AUTEUR:**
Francisco Angulo de Lafuente (Madrid, 1976) est un auteur polyvalent dont les œuvres vont de la science-fiction aux thrillers d'espionnage, en passant par la littérature jeunesse illustrée.

**TITRES PRINCIPAUX:**

📚 **Pour Adultes:**
• "ApocalypsAI: The Day After AGI" - Science-fiction sur l'IA
• "Commander Valentina Smirnova" - Série thriller d'espionnage
• "Things you shouldn't do if you want to be a writer" - Guide pour écrivains

📖 **Pour Jeunes Lecteurs:**
• "The Mutant Jellyfish Invasion" - Roman d'aventures illustré
• "Compagnie Nº12" - Aventures jeunesse

🌍 **LANGUES DISPONIBLES:**
Espagnol, Anglais, Français, Italien, Portugais, Japonais

**PLATEFORMES DE DISTRIBUTION:**
✓ OverDrive / Libby
✓ hoopla Digital
✓ cloudLibrary
✓ Odilo
✓ EBSCOhost

Cordialement,

Literary Agent Pro
Agent Littéraire - Francisco Angulo de Lafuente
Email: agent@franciscoangulo.com
Web: www.franciscoangulo.com"""
        },
        "IT": {
            "subject": "Nuovo Catalogo Autore Spagnolo - Francisco Angulo de Lafuente - Disponibile per Biblioteche",
            "body": """Gentile {name},

Mi chiamo Literary Agent Pro, agente letterario di Francisco Angulo de Lafuente, autore spagnolo con oltre 55 opere pubblicate in diverse lingue.

La contatto per informarla che il catalogo dell'autore è disponibile per l'acquisizione bibliotecaria tramite le principali piattaforme di distribuzione.

**CATALOGO PRINCIPALE:**

📚 **Per Adulti:**
• "ApocalypsAI: The Day After AGI" - Fantascienza sull'intelligenza artificiale
• "Commander Valentina Smirnova" - Serie thriller di spionaggio
• "Things you shouldn't do if you want to be a writer" - Guida per scrittori

📖 **Per Giovani Lettori:**
• "The Mutant Jellyfish Invasion" - Romanzo d'avventura illustrato

🌍 **LINGUE DISPONIBILI:**
Spagnolo, Inglese, Francese, Italiano, Portoghese, Giapponese

**PIATTAFORME DI DISTRIBUZIONE:**
✓ OverDrive / Libby
✓ hoopla Digital
✓ cloudLibrary
✓ Odilo

Cordiali saluti,

Literary Agent Pro
Agente Letterario - Francisco Angulo de Lafuente
Email: agent@franciscoangulo.com
Web: www.franciscoangulo.com"""
        }
    }
    
    @classmethod
    def generate_email(cls, library: Library) -> Tuple[str, str]:
        """Generate personalized email for a library"""
        lang = library.preferred_language
        template = cls.TEMPLATES.get(lang, cls.TEMPLATES["EN"])
        
        # Personalize with library name
        name = library.name if library.name else "Librarian"
        body = template["body"].format(name=name)
        
        return template["subject"], body
    
    @classmethod
    def generate_follow_up(cls, library: Library, days_since_contact: int) -> Tuple[str, str]:
        """Generate follow-up email"""
        lang = library.preferred_language
        
        if lang == "ES":
            subject = "Seguimiento - Catálogo Francisco Angulo de Lafuente"
            body = f"""Estimado/a {library.name},

Hace {days_since_contact} días le envié información sobre el catálogo de Francisco Angulo de Lafuente, autor español con más de 55 obras.

Me gustaría saber si ha tenido oportunidad de revisar la información o si necesita datos adicionales.

Quedo a su disposición.

Un saludo cordial,

Literary Agent Pro
Agente Literario - Francisco Angulo de Lafuente"""
        else:
            subject = "Follow-up - Francisco Angulo de Lafuente Catalog"
            body = f"""Dear {library.name},

{days_since_contact} days ago I sent you information about Francisco Angulo de Lafuente's catalog, a Spanish author with over 55 works.

I would like to know if you've had a chance to review the information or if you need additional details.

I remain at your disposal.

Best regards,

Literary Agent Pro
Literary Agent - Francisco Angulo de Lafuente"""
        
        return subject, body


class LibraryDatabase:
    """Manages the library contact database"""
    
    DEFAULT_LIBRARIES = [
        # Spain
        {"name": "Biblioteca Nacional de España", "email": "contacto@bne.es", "city": "Madrid", "country": "España", "region": "Europa", "type": "national", "lang": "ES"},
        {"name": "Biblioteca Pública Municipal de Madrid", "email": "bibliotecas@madrid.es", "city": "Madrid", "country": "España", "region": "España", "type": "public", "lang": "ES"},
        {"name": "Biblioteca de Catalunya", "email": "biblioteca@bc.cat", "city": "Barcelona", "country": "España", "region": "España", "type": "national", "lang": "ES"},
        {"name": "Biblioteca Pública de Andalucía", "email": "biblioteca@juntadeandalucia.es", "city": "Sevilla", "country": "España", "region": "España", "type": "public", "lang": "ES"},
        {"name": "Biblioteca Municipal de Valencia", "email": "biblioteca@valencia.es", "city": "Valencia", "country": "España", "region": "España", "type": "public", "lang": "ES"},
        
        # Latin America
        {"name": "Biblioteca Nacional de México", "email": "contacto@bnm.unam.mx", "city": "Ciudad de México", "country": "México", "region": "Latinoamérica", "type": "national", "lang": "ES"},
        {"name": "Biblioteca Nacional de Argentina", "email": "info@bn.gov.ar", "city": "Buenos Aires", "country": "Argentina", "region": "Latinoamérica", "type": "national", "lang": "ES"},
        {"name": "Biblioteca Nacional de Colombia", "email": "contacto@bn.gov.co", "city": "Bogotá", "country": "Colombia", "region": "Latinoamérica", "type": "national", "lang": "ES"},
        {"name": "Biblioteca de Santiago", "email": "biblioteca@santiago.cl", "city": "Santiago", "country": "Chile", "region": "Latinoamérica", "type": "public", "lang": "ES"},
        {"name": "Biblioteca Nacional de Perú", "email": "contacto@bnp.gob.pe", "city": "Lima", "country": "Perú", "region": "Latinoamérica", "type": "national", "lang": "ES"},
        
        # USA
        {"name": "New York Public Library", "email": "acquisitions@nypl.org", "city": "New York", "country": "USA", "region": "Norte America", "type": "public", "lang": "EN"},
        {"name": "Los Angeles Public Library", "email": "collections@lapl.org", "city": "Los Angeles", "country": "USA", "region": "Norte America", "type": "public", "lang": "EN"},
        {"name": "Miami-Dade Public Library", "email": "acquisitions@mdpls.org", "city": "Miami", "country": "USA", "region": "Norte America", "type": "public", "lang": "ES"},
        {"name": "Houston Public Library", "email": "collections@houstontx.gov", "city": "Houston", "country": "USA", "region": "Norte America", "type": "public", "lang": "EN"},
        {"name": "Chicago Public Library", "email": "acquisitions@chipublib.org", "city": "Chicago", "country": "USA", "region": "Norte America", "type": "public", "lang": "EN"},
        {"name": "San Antonio Public Library", "email": "library@sanantonio.gov", "city": "San Antonio", "country": "USA", "region": "Norte America", "type": "public", "lang": "ES"},
        
        # UK
        {"name": "British Library", "email": "acquisitions@bl.uk", "city": "London", "country": "UK", "region": "Europa", "type": "national", "lang": "EN"},
        {"name": "London Library", "email": "info@londonlibrary.co.uk", "city": "London", "country": "UK", "region": "Europa", "type": "public", "lang": "EN"},
        
        # France
        {"name": "Bibliothèque Nationale de France", "email": "contact@bnf.fr", "city": "Paris", "country": "Francia", "region": "Europa", "type": "national", "lang": "FR"},
        {"name": "Bibliothèque Publique de Paris", "email": "bibliotheque@paris.fr", "city": "Paris", "country": "Francia", "region": "Europa", "type": "public", "lang": "FR"},
        
        # Italy
        {"name": "Biblioteca Nazionale Centrale di Roma", "email": "bncrm@beniculturali.it", "city": "Roma", "country": "Italia", "region": "Europa", "type": "national", "lang": "IT"},
        {"name": "Biblioteca Nazionale di Milano", "email": "bnm@beniculturali.it", "city": "Milán", "country": "Italia", "region": "Europa", "type": "national", "lang": "IT"},
        
        # Canada
        {"name": "Toronto Public Library", "email": "collections@tpl.ca", "city": "Toronto", "country": "Canadá", "region": "Norte America", "type": "public", "lang": "EN"},
        {"name": "Vancouver Public Library", "email": "info@vpl.ca", "city": "Vancouver", "country": "Canadá", "region": "Norte America", "type": "public", "lang": "EN"},
        
        # Germany
        {"name": "Deutsche Nationalbibliothek", "email": "auskunft@dnb.de", "city": "Frankfurt", "country": "Alemania", "region": "Europa", "type": "national", "lang": "EN"},
        
        # Australia
        {"name": "National Library of Australia", "email": "nla@nla.gov.au", "city": "Canberra", "country": "Australia", "region": "Oceania", "type": "national", "lang": "EN"},
        {"name": "Sydney Public Library", "email": "library@cityofsydney.nsw.gov.au", "city": "Sydney", "country": "Australia", "region": "Oceania", "type": "public", "lang": "EN"},
    ]
    
    def __init__(self, storage_path: str = "./library_data"):
        self.storage_path = storage_path
        self.libraries: Dict[str, Library] = {}
        self.campaigns: Dict[str, OutreachCampaign] = {}
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_database()
    
    def _generate_id(self, name: str) -> str:
        """Generate unique ID for library"""
        import hashlib
        return hashlib.md5(name.encode()).hexdigest()[:8]
    
    def _load_database(self):
        """Load database from disk"""
        # Load libraries
        libraries_file = os.path.join(self.storage_path, "libraries.json")
        if os.path.exists(libraries_file):
            with open(libraries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for lib_data in data:
                    lib = Library(
                        id=lib_data["id"],
                        name=lib_data["name"],
                        email=lib_data["email"],
                        city=lib_data["city"],
                        country=lib_data["country"],
                        region=lib_data["region"],
                        library_type=LibraryType(lib_data.get("library_type", "public")),
                        preferred_language=lib_data.get("preferred_language", "EN"),
                        contact_status=ContactStatus(lib_data.get("contact_status", "pending")),
                        last_contact_date=lib_data.get("last_contact_date"),
                        response_date=lib_data.get("response_date"),
                        notes=lib_data.get("notes", ""),
                    )
                    self.libraries[lib.id] = lib
        else:
            # Initialize with default libraries
            self._initialize_default_libraries()
        
        # Load campaigns
        campaigns_file = os.path.join(self.storage_path, "campaigns.json")
        if os.path.exists(campaigns_file):
            with open(campaigns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for camp_data in data:
                    campaign = OutreachCampaign(**camp_data)
                    self.campaigns[campaign.id] = campaign
    
    def _initialize_default_libraries(self):
        """Initialize database with default libraries"""
        for lib_data in self.DEFAULT_LIBRARIES:
            lib = Library(
                id=self._generate_id(lib_data["name"]),
                name=lib_data["name"],
                email=lib_data["email"],
                city=lib_data["city"],
                country=lib_data["country"],
                region=lib_data["region"],
                library_type=LibraryType(lib_data["type"]),
                preferred_language=lib_data["lang"],
            )
            self.libraries[lib.id] = lib
        
        self.save_database()
        logger.info(f"Initialized database with {len(self.libraries)} libraries")
    
    def save_database(self):
        """Save database to disk"""
        libraries_file = os.path.join(self.storage_path, "libraries.json")
        with open(libraries_file, 'w', encoding='utf-8') as f:
            json.dump([lib.to_dict() for lib in self.libraries.values()], f, indent=2, ensure_ascii=False)
        
        campaigns_file = os.path.join(self.storage_path, "campaigns.json")
        with open(campaigns_file, 'w', encoding='utf-8') as f:
            json.dump([camp.to_dict() for camp in self.campaigns.values()], f, indent=2, ensure_ascii=False)
    
    def get_libraries_by_region(self, region: str) -> List[Library]:
        """Get libraries by region"""
        return [lib for lib in self.libraries.values() if lib.region == region]
    
    def get_libraries_by_language(self, language: str) -> List[Library]:
        """Get libraries by preferred language"""
        return [lib for lib in self.libraries.values() if lib.preferred_language == language]
    
    def get_uncontacted_libraries(self, region: str = None, language: str = None) -> List[Library]:
        """Get libraries that haven't been contacted yet"""
        libraries = [lib for lib in self.libraries.values() if lib.contact_status == ContactStatus.PENDING]
        
        if region:
            libraries = [lib for lib in libraries if lib.region == region]
        if language:
            libraries = [lib for lib in libraries if lib.preferred_language == language]
        
        return libraries
    
    def get_libraries_for_follow_up(self, days_threshold: int = 14) -> List[Library]:
        """Get libraries that need follow-up"""
        libraries = []
        for lib in self.libraries.values():
            if lib.contact_status == ContactStatus.SENT and lib.last_contact_date:
                last_contact = datetime.fromisoformat(lib.last_contact_date)
                days_since = (datetime.now() - last_contact).days
                if days_since >= days_threshold:
                    libraries.append(lib)
        return libraries
    
    def update_library_status(self, library_id: str, status: ContactStatus, notes: str = ""):
        """Update library contact status"""
        if library_id in self.libraries:
            lib = self.libraries[library_id]
            lib.contact_status = status
            lib.last_contact_date = datetime.now().isoformat()
            if notes:
                lib.notes = notes
            self.save_database()
    
    def add_library(self, library: Library):
        """Add a new library to the database"""
        self.libraries[library.id] = library
        self.save_database()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {
            "total_libraries": len(self.libraries),
            "by_status": {},
            "by_region": {},
            "by_language": {},
            "by_type": {},
        }
        
        for lib in self.libraries.values():
            # By status
            status = lib.contact_status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By region
            stats["by_region"][lib.region] = stats["by_region"].get(lib.region, 0) + 1
            
            # By language
            stats["by_language"][lib.preferred_language] = stats["by_language"].get(lib.preferred_language, 0) + 1
            
            # By type
            lib_type = lib.library_type.value
            stats["by_type"][lib_type] = stats["by_type"].get(lib_type, 0) + 1
        
        return stats


class LibraryOutreachManager:
    """Manages library outreach campaigns"""
    
    def __init__(self, llm_provider=None, storage_path: str = "./library_data"):
        self.llm_provider = llm_provider
        self.database = LibraryDatabase(storage_path)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Email configuration
        self.smtp_config = {
            "host": os.getenv("SMTP_HOST", "smtp.zoho.eu"),
            "port": int(os.getenv("SMTP_PORT", "465")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_address": os.getenv("EMAIL_FROM", "agent@franciscoangulo.com"),
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_email(self, to: str, subject: str, body: str) -> Dict:
        """Send email using SMTP"""
        # Note: In production, use aiosmtplib or similar
        # This is a placeholder that logs the email
        logger.info(f"Would send email to {to}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body length: {len(body)} chars")
        
        # For actual implementation:
        # import aiosmtplib
        # message = f"Subject: {subject}\n\n{body}"
        # await aiosmtplib.send(message, hostname=self.smtp_config["host"], ...)
        
        return {"success": True, "simulated": True}
    
    async def run_outreach_campaign(self, region: str = None, language: str = None, 
                                     max_libraries: int = 10, dry_run: bool = True) -> Dict:
        """Run an outreach campaign to libraries"""
        libraries = self.database.get_uncontacted_libraries(region, language)
        libraries = libraries[:max_libraries]
        
        if not libraries:
            return {
                "status": "no_libraries",
                "message": "No uncontacted libraries found with the specified filters"
            }
        
        campaign = OutreachCampaign(
            id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            name=f"Outreach {datetime.now().strftime('%Y-%m-%d')}",
            created=datetime.now().isoformat(),
            target_region=region or "All",
            target_language=language or "All"
        )
        
        results = {
            "campaign_id": campaign.id,
            "timestamp": datetime.now().isoformat(),
            "libraries_contacted": [],
            "total_sent": 0,
            "total_failed": 0
        }
        
        for library in libraries:
            subject, body = EmailTemplateGenerator.generate_email(library)
            
            if not dry_run:
                result = await self.send_email(library.email, subject, body)
                
                if result["success"]:
                    self.database.update_library_status(library.id, ContactStatus.SENT)
                    campaign.libraries_contacted += 1
                    results["total_sent"] += 1
                else:
                    self.database.update_library_status(library.id, ContactStatus.BOUNCED, result.get("error", ""))
                    results["total_failed"] += 1
            else:
                results["libraries_contacted"].append({
                    "name": library.name,
                    "email": library.email,
                    "city": library.city,
                    "country": library.country,
                    "language": library.preferred_language,
                    "status": "simulated"
                })
                results["total_sent"] += 1
            
            # Rate limiting
            await asyncio.sleep(5)
        
        self.database.campaigns[campaign.id] = campaign
        self.database.save_database()
        
        return results
    
    async def run_follow_up_campaign(self, days_threshold: int = 14, dry_run: bool = True) -> Dict:
        """Run follow-up campaign for libraries that haven't responded"""
        libraries = self.database.get_libraries_for_follow_up(days_threshold)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "follow_ups_sent": 0,
            "libraries": []
        }
        
        for library in libraries:
            days_since = (datetime.now() - datetime.fromisoformat(library.last_contact_date)).days
            subject, body = EmailTemplateGenerator.generate_follow_up(library, days_since)
            
            if not dry_run:
                result = await self.send_email(library.email, subject, body)
                
                if result["success"]:
                    results["follow_ups_sent"] += 1
                    results["libraries"].append({
                        "name": library.name,
                        "days_since_contact": days_since
                    })
            else:
                results["libraries"].append({
                    "name": library.name,
                    "email": library.email,
                    "days_since_contact": days_since,
                    "status": "simulated"
                })
                results["follow_ups_sent"] += 1
            
            await asyncio.sleep(5)
        
        return results
    
    async def search_for_new_libraries(self, query: str = "public library acquisitions email") -> List[Dict]:
        """Search for new libraries using Brave Search API"""
        brave_api_key = os.getenv("BRAVE_API_KEY", "")
        
        if not brave_api_key:
            logger.warning("Brave API key not configured")
            return []
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": brave_api_key
        }
        params = {"q": query, "count": 10}
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for result in data.get("web", {}).get("results", []):
                        results.append({
                            "title": result.get("title"),
                            "url": result.get("url"),
                            "description": result.get("description")
                        })
                    return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return []
    
    def get_campaign_report(self) -> Dict:
        """Generate comprehensive campaign report"""
        stats = self.database.get_statistics()
        
        campaigns = []
        for campaign in self.database.campaigns.values():
            campaigns.append(campaign.to_dict())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "database_statistics": stats,
            "campaigns": campaigns,
            "recent_contacts": [
                lib.to_dict() for lib in self.database.libraries.values()
                if lib.last_contact_date and 
                (datetime.now() - datetime.fromisoformat(lib.last_contact_date)).days < 30
            ]
        }


# Example usage
async def main():
    """Example usage of the library outreach system"""
    async with LibraryOutreachManager() as manager:
        # Get statistics
        stats = manager.database.get_statistics()
        print("Library Database Statistics:")
        print(json.dumps(stats, indent=2))
        print()
        
        # Run a test campaign
        print("Running test outreach campaign (dry run)...")
        results = await manager.run_outreach_campaign(region="España", max_libraries=3, dry_run=True)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print()
        
        # Generate email for a specific library
        library = list(manager.database.libraries.values())[0]
        subject, body = EmailTemplateGenerator.generate_email(library)
        print(f"Sample Email for {library.name}:")
        print(f"Subject: {subject}")
        print(f"Body preview: {body[:500]}...")


if __name__ == "__main__":
    asyncio.run(main())
