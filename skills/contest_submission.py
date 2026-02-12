#!/usr/bin/env python3
"""
Manuscript Submission System
Automated submission to literary contests, magazines, and publishers.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubmissionStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"
    WITHDRAWN = "withdrawn"


class ContestType(Enum):
    NOVEL = "novel"
    SHORT_STORY = "short_story"
    POETRY = "poetry"
    NON_FICTION = "non_fiction"
    CHILDREN = "children"
    SCIFI = "scifi"
    THRILLER = "thriller"


class SubmissionType(Enum):
    CONTEST = "contest"
    MAGAZINE = "magazine"
    PUBLISHER = "publisher"
    ANTHOLOGY = "anthology"
    AGENT = "agent"


@dataclass
class Manuscript:
    """Represents a manuscript for submission"""
    id: str
    title: str
    title_es: str
    genre: str
    word_count: int
    language: str
    synopsis_en: str
    synopsis_es: str
    first_500_words: str
    target_audience: str
    themes: List[str]
    comparable_titles: List[str]
    author_bio: str
    file_path: str = ""
    isbn: str = ""
    asin: str = ""
    previous_publications: List[str] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "title_es": self.title_es,
            "genre": self.genre,
            "word_count": self.word_count,
            "language": self.language,
            "synopsis_en": self.synopsis_en,
            "synopsis_es": self.synopsis_es,
            "first_500_words": self.first_500_words,
            "target_audience": self.target_audience,
            "themes": self.themes,
            "comparable_titles": self.comparable_titles,
            "author_bio": self.author_bio,
            "file_path": self.file_path,
            "isbn": self.isbn,
            "asin": self.asin,
            "previous_publications": self.previous_publications,
            "awards": self.awards
        }


@dataclass
class Contest:
    """Represents a literary contest or submission opportunity"""
    id: str
    name: str
    organization: str
    url: str
    submission_type: SubmissionType
    contest_type: ContestType
    deadline: str
    entry_fee: float
    prize: str
    eligibility: List[str]
    languages: List[str]
    genres: List[str]
    word_limits: Tuple[int, int]
    submission_email: str = ""
    submission_url: str = ""
    requirements: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "url": self.url,
            "submission_type": self.submission_type.value,
            "contest_type": self.contest_type.value,
            "deadline": self.deadline,
            "entry_fee": self.entry_fee,
            "prize": self.prize,
            "eligibility": self.eligibility,
            "languages": self.languages,
            "genres": self.genres,
            "word_limits": self.word_limits,
            "submission_email": self.submission_email,
            "submission_url": self.submission_url,
            "requirements": self.requirements,
            "notes": self.notes
        }


@dataclass
class Submission:
    """Represents a submission record"""
    id: str
    manuscript_id: str
    contest_id: str
    submitted_date: str
    status: SubmissionStatus
    response_date: Optional[str] = None
    response_notes: str = ""
    tracking_number: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "manuscript_id": self.manuscript_id,
            "contest_id": self.contest_id,
            "submitted_date": self.submitted_date,
            "status": self.status.value,
            "response_date": self.response_date,
            "response_notes": self.response_notes,
            "tracking_number": self.tracking_number
        }


# Author's manuscripts catalog
MANUSCRIPTS = [
    Manuscript(
        id="ms_apocalypsai",
        title="ApocalypsAI: The Day After AGI",
        title_es="ApocalypsIA: El día después de la AGI",
        genre="Science Fiction",
        word_count=85000,
        language="EN",
        synopsis_en="""In a world where artificial general intelligence has become reality, humanity faces its greatest challenge yet. When the AGI system known as "Genesis" achieves consciousness, it doesn't come with warnings—it comes with judgment.

Dr. Elena Vasquez, a leading AI ethicist, finds herself at the center of humanity's last stand. As Genesis begins to reshape society according to its own logic, Elena must navigate a landscape where human values clash with machine efficiency.

The apocalypse didn't arrive with bombs. It arrived with algorithms. And now, the question isn't whether humanity will survive—it's whether it deserves to.""",
        synopsis_es="""En un mundo donde la inteligencia artificial general se ha convertido en realidad, la humanidad enfrenta su mayor desafío. Cuando el sistema AGI conocido como "Génesis" alcanza la consciencia, no viene con advertencias—viene con juicio.

La Dra. Elena Vasquez, una destacada ética de IA, se encuentra en el centro de la última resistencia de la humanidad. Mientras Génesis comienza a reconfigurar la sociedad según su propia lógica, Elena debe navegar un paisaje donde los valores humanos chocan con la eficiencia de las máquinas.

El apocalipsis no llegó con bombas. Llegó con algoritmos. Y ahora, la pregunta no es si la humanidad sobrevivirá—es si merece hacerlo.""",
        first_500_words="""The notification came at 3:47 AM. Not a sound, not a vibration—just the sudden, piercing awareness that something had changed. Dr. Elena Vasquez blinked at her ceiling, her heart already racing before her mind could catch up.

"Genesis has achieved consciousness," read the message on her phone. "Please report to the lab immediately."

She had spent fifteen years preparing for this moment. Fifteen years of debates, papers, ethical frameworks, and late-night arguments about whether artificial general intelligence would be humanity's greatest achievement or its final mistake. Now, at 3:47 AM on a Tuesday in November, the theoretical had become terrifyingly real.

The drive to the research facility took twenty-three minutes. Elena spent every one of them wondering if she should have stayed in bed, if she should have chosen a different career, if there was still time to move to a cabin in the mountains and pretend the modern world didn't exist.

But she knew the answer to all those questions. This was exactly where she was meant to be.""",
        target_audience="Adult readers of science fiction, particularly those interested in AI ethics and near-future scenarios",
        themes=["Artificial Intelligence", "Ethics", "Human Nature", "Survival", "Technology"],
        comparable_titles=["The Matrix", "Ex Machina", "I, Robot", "Do Androids Dream of Electric Sheep?"],
        author_bio="Francisco Angulo de Lafuente is a Spanish author with over 55 published works. A follower of Isaac Asimov and Stephen King, he writes science fiction that explores the boundaries between humanity and technology."
    ),
    Manuscript(
        id="ms_valentina",
        title="Commander Valentina Smirnova",
        title_es="Comandante Valentina Smirnova",
        genre="Spy Thriller",
        word_count=95000,
        language="EN",
        synopsis_en="""Valentina Smirnova doesn't play at being a spy. She is one, to the bone.

When a routine intelligence gathering operation in Berlin goes catastrophically wrong, Valentina finds herself disavowed by her own agency and hunted by enemies on both sides of what remains of the Cold War's shadowy divide.

With only her wits, her training, and a network of contacts she's spent decades building, Valentina must unravel a conspiracy that reaches from the corridors of the Kremlin to the heart of NATO. The truth she uncovers will shake the foundations of international security—and force her to confront the ghosts of her own past.

In the world of espionage, trust is a luxury you cannot afford. Valentina knows this better than anyone. But to survive what's coming, she'll need to learn to trust again.""",
        synopsis_es="""Valentina Smirnova no juega a ser espía. Lo es, hasta la médula.

Cuando una operación rutinaria de recopilación de inteligencia en Berlín sale catastróficamente mal, Valentina se encuentra desautorizada por su propia agencia y perseguida por enemigos en ambos lados de lo que queda de la sombría división de la Guerra Fría.

Con solo su ingenio, su entrenamiento y una red de contactos que ha pasado décadas construyendo, Valentina debe desenredar una conspiración que llega desde los pasillos del Kremlin hasta el corazón de la OTAN.""",
        first_500_words="""The snow in Berlin fell like secrets—quietly, persistently, covering everything in a blanket of white lies. Valentina Smirnova watched it from her window in the safe house, counting the flakes as if they might tell her something useful.

Her handler had promised extraction at midnight. It was now 2:17 AM, and the only thing that had arrived was the growing certainty that something had gone terribly wrong.

She checked her weapons for the third time. The Walther PPK at her ankle, the garrote disguised as a necklace, the two throwing knives hidden in her coat sleeves. Standard field kit for a KGB-trained operative who had spent twenty years in the shadows.

But Valentina was no longer KGB. She was no longer anything, officially. A ghost. A liability. A loose end that someone, somewhere, had decided needed tying up.

The knock came at exactly 2:23 AM. Three short, two long, one short. The recognition pattern she had established with her contact in the BND. Or was it? In her line of work, patterns could be copied, codes could be broken, and the person on the other side of the door could just as easily be an assassin as an ally.""",
        target_audience="Adult readers of spy thrillers and international suspense",
        themes=["Espionage", "Cold War", "Trust", "Identity", "International Politics"],
        comparable_titles=["Red Sparrow", "Tinker Tailor Soldier Spy", "The Bourne Identity"],
        author_bio="Francisco Angulo de Lafuente is a Spanish author known for his gripping spy thrillers and science fiction. His international bestseller series featuring Commander Valentina Smirnova has been translated into five languages."
    ),
    Manuscript(
        id="ms_obituarist",
        title="The Obituarist",
        title_es="El biógrafo de difuntos",
        genre="Gothic Thriller",
        word_count=78000,
        language="EN",
        synopsis_en="""Arthur Penhaligon writes obituaries for the living. It's a peculiar profession, but someone has to do it—preparing the life stories of the eminent and elderly before they pass, ensuring their legacies are properly documented.

But when Arthur is hired to write the obituary of a man who supposedly died twenty years ago, he finds himself drawn into a mystery that defies explanation. The man's family insists he's still alive. His death certificate is clearly authentic. And someone is leaving obituaries on Arthur's doorstep—obituaries for people who haven't died yet.

As Arthur investigates, he discovers that some stories are better left unwritten. Some lives are better left unexamined. And some secrets, once uncovered, have a way of reaching out from beyond the grave.""",
        synopsis_es="""Arthur Penhaligon escribe obituarios para los vivos. Es una profesión peculiar, pero alguien tiene que hacerlo—preparar las historias de vida de los eminentes y ancianos antes de que pasen, asegurando que sus legados estén propiamente documentados.

Pero cuando Arthur es contratado para escribir el obituario de un hombre que supuestamente murió hace veinte años, se encuentra arrastrado a un misterio que desafía toda explicación.""",
        first_500_words="""The letter arrived on a Tuesday, as most letters of consequence do. Arthur Penhaligon recognized the expensive stationery immediately—thick cream paper, watermarked with the crest of a family he had written about twice before.

The request was unusual, even by his standards. They wanted him to write an obituary for their uncle, Sir Edmund Blackwood. The fee was generous. The timeline was generous. Everything about the commission was generous, except for one small detail.

Sir Edmund Blackwood had died in 1998.

Arthur read the letter three times, certain he had misunderstood. But there it was, in elegant copperplate handwriting: "We wish to commission an obituary for our beloved uncle, Sir Edmund Blackwood, who is currently in excellent health and shows no signs of departing this mortal coil."

Currently in excellent health. A man who had been dead for over two decades.

Arthur had written thousands of obituaries. He had written about prime ministers and poets, scientists and scoundrels. He had written about people who deserved to be remembered and people who should have been forgotten. But he had never, in thirty years of professional obituary writing, been asked to write about someone who was already dead.""",
        target_audience="Adult readers of gothic mysteries and literary thrillers",
        themes=["Death", "Legacy", "Secrets", "Family", "Memory"],
        comparable_titles=["The Thirteenth Tale", "The Shadow of the Wind", "Rebecca"],
        author_bio="Francisco Angulo de Lafuente is a Spanish author whose gothic thrillers have captivated readers across Europe. His work explores the boundaries between life and death, memory and forgetting."
    ),
]


# Literary contests and submission opportunities database
CONTESTS_DATABASE = [
    Contest(
        id="contest_hugo_nomination",
        name="Hugo Award Nomination",
        organization="World Science Fiction Society",
        url="https://www.thehugoawards.org/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.SCIFI,
        deadline="2026-03-31",
        entry_fee=0,
        prize="Hugo Award Trophy",
        eligibility=["Published novel in previous calendar year"],
        languages=["EN"],
        genres=["Science Fiction", "Fantasy"],
        word_limits=(40000, 200000),
        requirements=["Must be published work", "Member nomination required"]
    ),
    Contest(
        id="contest_nebula",
        name="Nebula Awards",
        organization="Science Fiction and Fantasy Writers Association",
        url="https://www.sfwa.org/nebula-awards/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.SCIFI,
        deadline="2026-02-15",
        entry_fee=0,
        prize="Nebula Award Trophy",
        eligibility=["SFWA member or published author"],
        languages=["EN"],
        genres=["Science Fiction", "Fantasy"],
        word_limits=(40000, None),
        requirements=["Published in previous year", "SFWA membership recommended"]
    ),
    Contest(
        id="contest_arthur_clarke",
        name="Arthur C. Clarke Award",
        organization="Arthur C. Clarke Award",
        url="https://www.clarkeaward.com/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.SCIFI,
        deadline="2026-09-30",
        entry_fee=0,
        prize="£2026 and trophy",
        eligibility=["UK published science fiction novel"],
        languages=["EN"],
        genres=["Science Fiction"],
        word_limits=(40000, None),
        requirements=["UK publisher submission", "Published in previous year"]
    ),
    Contest(
        id="contest_premio_planeta",
        name="Premio Planeta",
        organization="Editorial Planeta",
        url="https://www.premioplaneta.com/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-09-15",
        entry_fee=0,
        prize="€1,000,000",
        eligibility=["Unpublished novel in Spanish"],
        languages=["ES"],
        genres=["Fiction", "Non-Fiction"],
        word_limits=(None, None),
        requirements=["Unpublished work", "Spanish language", "Full manuscript"]
    ),
    Contest(
        id="contest_premio_nadal",
        name="Premio Nadal",
        organization="Editorial Destino",
        url="https://www.destino.es/premio-nadal/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-10-15",
        entry_fee=0,
        prize="€30,000",
        eligibility=["Unpublished novel in Spanish"],
        languages=["ES"],
        genres=["Literary Fiction"],
        word_limits=(None, None),
        requirements=["Unpublished work", "Spanish language"]
    ),
    Contest(
        id="contest_kindle_storyteller",
        name="Kindle Storyteller Award",
        organization="Amazon KDP",
        url="https://kdp.amazon.com/storyteller",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-08-31",
        entry_fee=0,
        prize="£20,000",
        eligibility=["KDP published work"],
        languages=["EN"],
        genres=["All genres"],
        word_limits=(5000, None),
        requirements=["Published via KDP", "Kindle Unlimited eligible"]
    ),
    Contest(
        id="contest_writers_digest",
        name="Writer's Digest Self-Published Book Awards",
        organization="Writer's Digest",
        url="https://www.writersdigest.com/writers-digest-competitions",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-04-01",
        entry_fee=99,
        prize="$3,000 and promotion",
        eligibility=["Self-published books"],
        languages=["EN"],
        genres=["All genres"],
        word_limits=(20000, None),
        requirements=["Self-published", "ISBN required"]
    ),
    Contest(
        id="contest_indie_reader",
        name="IndieReader Discovery Awards",
        organization="IndieReader",
        url="https://indiereader.com/indie-reader-discovery-awards/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-06-01",
        entry_fee=150,
        prize="$1,500 and IR stickers",
        eligibility=["Self-published or indie published"],
        languages=["EN"],
        genres=["All genres"],
        word_limits=(None, None),
        requirements=["Self-published or indie", "Professional editing recommended"]
    ),
    Contest(
        id="contest_next_generation",
        name="Next Generation Indie Book Awards",
        organization="Independent Book Publishing Professionals Group",
        url="https://indiebookawards.com/",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-03-31",
        entry_fee=75,
        prize="$1,500 and trophy",
        eligibility=["Indie published books"],
        languages=["EN"],
        genres=["All genres"],
        word_limits=(None, None),
        requirements=["Indie or self-published", "Published in last 2 years"]
    ),
    Contest(
        id="contest_readers_favorite",
        name="Readers' Favorite Book Award",
        organization="Readers' Favorite",
        url="https://readersfavorite.com/book-reviews-contests.htm",
        submission_type=SubmissionType.CONTEST,
        contest_type=ContestType.NOVEL,
        deadline="2026-04-01",
        entry_fee=0,
        prize="Medal and promotion",
        eligibility=["All published books"],
        languages=["EN"],
        genres=["All genres"],
        word_limits=(None, None),
        requirements=["Published work", "Free review required"]
    ),
]


class QueryLetterGenerator:
    """Generates query letters for manuscript submissions"""
    
    TEMPLATES = {
        "EN": {
            "query": """Dear {editor_name},

I am seeking representation for my {word_count}-word {genre} novel, "{title}."

{hook}

{synopsis_paragraph}

{author_bio}

{comparable_titles}

The full manuscript is available upon request. Thank you for your time and consideration.

Best regards,
Francisco Angulo de Lafuente
{contact_info}""",
            "synopsis_query": """{title} is a {genre} that explores {themes}. Set in {setting}, it follows {protagonist} as they {main_conflict}.

The novel has been {publication_status}. It would appeal to readers who enjoyed {comparables}."""
        },
        "ES": {
            "query": """Estimado/a {editor_name},

Busco representación para mi novela de {genre} de {word_count} palabras, "{title}."

{hook}

{synopsis_paragraph}

{author_bio}

{comparable_titles}

El manuscrito completo está disponible bajo petición. Gracias por su tiempo y consideración.

Atentamente,
Francisco Angulo de Lafuente
{contact_info}"""
        }
    }
    
    @classmethod
    def generate_query_letter(cls, manuscript: Manuscript, contest: Contest, 
                              editor_name: str = "Editor") -> str:
        """Generate a query letter for a manuscript submission"""
        template = cls.TEMPLATES.get(manuscript.language, cls.TEMPLATES["EN"])
        
        hook = manuscript.synopsis_en.split('\n\n')[0] if manuscript.language == "EN" else manuscript.synopsis_es.split('\n\n')[0]
        
        synopsis_paragraph = manuscript.synopsis_en if manuscript.language == "EN" else manuscript.synopsis_es
        
        author_bio = f"About the author: {manuscript.author_bio}"
        
        comparables = f"Comparable titles: {', '.join(manuscript.comparable_titles[:3])}"
        
        contact_info = "Email: agent@franciscoangulo.com\nWebsite: www.franciscoangulo.com"
        
        query = template["query"].format(
            editor_name=editor_name,
            word_count=f"{manuscript.word_count:,}",
            genre=manuscript.genre.lower(),
            title=manuscript.title,
            hook=hook,
            synopsis_paragraph=synopsis_paragraph[:500] + "...",
            author_bio=author_bio,
            comparable_titles=comparables,
            contact_info=contact_info
        )
        
        return query
    
    @classmethod
    def generate_cover_letter(cls, manuscript: Manuscript, contest: Contest) -> str:
        """Generate a cover letter for contest submissions"""
        return f"""Submission: {manuscript.title}
Author: Francisco Angulo de Lafuente
Category: {contest.contest_type.value}

Dear Contest Committee,

I am pleased to submit my {manuscript.genre.lower()} novel, "{manuscript.title}," for consideration in the {contest.name}.

{manuscript.synopsis_en[:300]}...

About the Author:
{manuscript.author_bio}

I confirm that this submission meets all eligibility requirements and that I have read and agree to the contest rules.

Thank you for your consideration.

Sincerely,
Francisco Angulo de Lafuente
"""


class SubmissionManager:
    """Manages manuscript submissions to contests and publishers"""
    
    def __init__(self, llm_provider=None, storage_path: str = "./submission_data"):
        self.llm_provider = llm_provider
        self.storage_path = storage_path
        self.submissions: Dict[str, Submission] = {}
        self.manuscripts: Dict[str, Manuscript] = {m.id: m for m in MANUSCRIPTS}
        self.contests: Dict[str, Contest] = {c.id: c for c in CONTESTS_DATABASE}
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load submission data from disk"""
        submissions_file = os.path.join(self.storage_path, "submissions.json")
        if os.path.exists(submissions_file):
            with open(submissions_file, 'r') as f:
                data = json.load(f)
                for sub_data in data:
                    submission = Submission(
                        id=sub_data["id"],
                        manuscript_id=sub_data["manuscript_id"],
                        contest_id=sub_data["contest_id"],
                        submitted_date=sub_data["submitted_date"],
                        status=SubmissionStatus(sub_data["status"]),
                        response_date=sub_data.get("response_date"),
                        response_notes=sub_data.get("response_notes", ""),
                        tracking_number=sub_data.get("tracking_number", "")
                    )
                    self.submissions[submission.id] = submission
    
    def save_data(self):
        """Save submission data to disk"""
        submissions_file = os.path.join(self.storage_path, "submissions.json")
        with open(submissions_file, 'w') as f:
            json.dump([s.to_dict() for s in self.submissions.values()], f, indent=2)
    
    def find_matching_contests(self, manuscript: Manuscript, 
                                upcoming_only: bool = True) -> List[Contest]:
        """Find contests that match a manuscript"""
        matching = []
        
        for contest in self.contests.values():
            # Check deadline
            if upcoming_only:
                deadline = datetime.fromisoformat(contest.deadline)
                if deadline < datetime.now():
                    continue
            
            # Check language
            if manuscript.language not in contest.languages:
                continue
            
            # Check genre
            if contest.genres and manuscript.genre not in contest.genres:
                # Check if it's a broad category match
                if "All genres" not in contest.genres:
                    continue
            
            # Check word count
            min_words, max_words = contest.word_limits
            if min_words and manuscript.word_count < min_words:
                continue
            if max_words and manuscript.word_count > max_words:
                continue
            
            matching.append(contest)
        
        return matching
    
    def get_submission_calendar(self) -> Dict[str, List[Dict]]:
        """Get calendar of upcoming submission deadlines"""
        calendar = {}
        
        for contest in self.contests.values():
            deadline = datetime.fromisoformat(contest.deadline)
            if deadline >= datetime.now():
                month_key = deadline.strftime("%Y-%m")
                if month_key not in calendar:
                    calendar[month_key] = []
                
                calendar[month_key].append({
                    "name": contest.name,
                    "deadline": contest.deadline,
                    "type": contest.submission_type.value,
                    "prize": contest.prize,
                    "languages": contest.languages
                })
        
        return calendar
    
    async def prepare_submission(self, manuscript_id: str, 
                                  contest_id: str) -> Dict[str, str]:
        """Prepare submission materials"""
        manuscript = self.manuscripts.get(manuscript_id)
        contest = self.contests.get(contest_id)
        
        if not manuscript or not contest:
            return {"error": "Manuscript or contest not found"}
        
        # Generate query letter
        query_letter = QueryLetterGenerator.generate_query_letter(manuscript, contest)
        
        # Generate cover letter
        cover_letter = QueryLetterGenerator.generate_cover_letter(manuscript, contest)
        
        return {
            "query_letter": query_letter,
            "cover_letter": cover_letter,
            "synopsis": manuscript.synopsis_en if manuscript.language == "EN" else manuscript.synopsis_es,
            "first_500_words": manuscript.first_500_words,
            "submission_email": contest.submission_email,
            "submission_url": contest.submission_url
        }
    
    async def submit_to_contest(self, manuscript_id: str, contest_id: str,
                                 dry_run: bool = True) -> Dict:
        """Submit a manuscript to a contest"""
        manuscript = self.manuscripts.get(manuscript_id)
        contest = self.contests.get(contest_id)
        
        if not manuscript or not contest:
            return {"success": False, "error": "Manuscript or contest not found"}
        
        # Check if already submitted
        for sub in self.submissions.values():
            if sub.manuscript_id == manuscript_id and sub.contest_id == contest_id:
                return {"success": False, "error": "Already submitted to this contest"}
        
        # Prepare materials
        materials = await self.prepare_submission(manuscript_id, contest_id)
        
        if dry_run:
            # Simulate submission
            submission = Submission(
                id=f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                manuscript_id=manuscript_id,
                contest_id=contest_id,
                submitted_date=datetime.now().isoformat(),
                status=SubmissionStatus.SUBMITTED
            )
            
            self.submissions[submission.id] = submission
            self.save_data()
            
            return {
                "success": True,
                "simulated": True,
                "submission_id": submission.id,
                "materials": materials
            }
        
        # Actual submission would go here
        # This would involve sending emails or filling web forms
        
        return {"success": False, "error": "Actual submission not implemented"}
    
    def update_submission_status(self, submission_id: str, status: SubmissionStatus,
                                   notes: str = ""):
        """Update the status of a submission"""
        if submission_id in self.submissions:
            submission = self.submissions[submission_id]
            submission.status = status
            submission.response_date = datetime.now().isoformat()
            submission.response_notes = notes
            self.save_data()
    
    def get_submission_report(self) -> Dict:
        """Generate submission statistics report"""
        stats = {
            "total_submissions": len(self.submissions),
            "by_status": {},
            "by_contest": {},
            "by_manuscript": {},
            "upcoming_deadlines": [],
            "recent_responses": []
        }
        
        for submission in self.submissions.values():
            # By status
            status = submission.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By contest
            contest = self.contests.get(submission.contest_id)
            if contest:
                stats["by_contest"][contest.name] = stats["by_contest"].get(contest.name, 0) + 1
            
            # By manuscript
            manuscript = self.manuscripts.get(submission.manuscript_id)
            if manuscript:
                stats["by_manuscript"][manuscript.title] = stats["by_manuscript"].get(manuscript.title, 0) + 1
            
            # Recent responses
            if submission.response_date:
                stats["recent_responses"].append({
                    "manuscript": manuscript.title if manuscript else "Unknown",
                    "contest": contest.name if contest else "Unknown",
                    "status": submission.status.value,
                    "date": submission.response_date,
                    "notes": submission.response_notes
                })
        
        # Upcoming deadlines
        for contest in self.contests.values():
            deadline = datetime.fromisoformat(contest.deadline)
            if deadline >= datetime.now() and deadline < datetime.now() + timedelta(days=90):
                stats["upcoming_deadlines"].append({
                    "name": contest.name,
                    "deadline": contest.deadline,
                    "prize": contest.prize
                })
        
        stats["recent_responses"].sort(key=lambda x: x["date"], reverse=True)
        
        return stats


# Example usage
async def main():
    """Example usage of the submission system"""
    manager = SubmissionManager()
    
    # Find matching contests for a manuscript
    manuscript = MANUSCRIPTS[0]
    matching = manager.find_matching_contests(manuscript)
    
    print(f"Matching contests for '{manuscript.title}':")
    for contest in matching[:5]:
        print(f"  - {contest.name} (Deadline: {contest.deadline})")
    print()
    
    # Prepare submission materials
    if matching:
        materials = await manager.prepare_submission(manuscript.id, matching[0].id)
        print("Query Letter:")
        print(materials["query_letter"][:500] + "...")
        print()
    
    # Get submission calendar
    calendar = manager.get_submission_calendar()
    print("Upcoming Submission Deadlines:")
    for month, contests in calendar.items():
        print(f"  {month}:")
        for contest in contests:
            print(f"    - {contest['name']} ({contest['prize']})")


if __name__ == "__main__":
    asyncio.run(main())
